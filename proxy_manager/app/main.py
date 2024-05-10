import logging
from fastapi import FastAPI, HTTPException
from fastapi.requests import Request
import httpx
from os import getenv
import base64
from starlette.responses import StreamingResponse


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


username = getenv("IMGPROXY_PROXY_USERNAME")
password = getenv("IMGPROXY_PROXY_PASSWORD")
host = getenv("IMGPROXY_PROXY_HOST")
port = getenv("IMGPROXY_PROXY_PORT")
protocol = getenv("IMGPROXY_PROXY_PROTOCOL", "http")


def proxy_url():
    if not all([username, password, host, port]):
        logger.warning(
            "Proxy configuration is incomplete. Direct requests will be used."
        )
        return None
    else:
        creds_encoded = base64.b64encode(f"{username}:{password}".encode()).decode(
            "utf-8"
        )
        return f"{protocol}://{creds_encoded}@{host}:{port}"


proxy = proxy_url()

app = FastAPI()


@app.get("/")
async def root():
    return {
        "message": "Proxy Manager is running. Use /fetch-image/ to fetch images via proxy."
    }


@app.get("/fetch-image/")
async def fetch_image(url: str):
    timeout = httpx.Timeout(10.0, connect=5.0)
    client = httpx.AsyncClient(timeout=timeout)
    try:
        # Make the initial request to fetch the image
        response = await client.get(url)
        response.raise_for_status()
        return StreamingResponse(
            response.iter_content(), media_type=response.headers.get("Content-Type")
        )
    except (httpx.RequestError, httpx.HTTPStatusError) as e:
        if proxy:
            try:
                # If the direct request fails, try via the configured proxy
                proxy_response = await client.get(
                    url, proxies={"http://": proxy, "https://": proxy}
                )
                proxy_response.raise_for_status()
                return StreamingResponse(
                    proxy_response.iter_content(),
                    media_type=proxy_response.headers.get("Content-Type"),
                )
            except (httpx.RequestError, httpx.HTTPStatusError):
                logger.error("Failed to fetch image via direct and proxy methods.")
                raise HTTPException(
                    status_code=502,
                    detail="Failed to fetch image via direct and proxy methods.",
                )
        else:
            logger.error(f"Failed to fetch image directly: {str(e)}")
            raise HTTPException(
                status_code=502, detail="Failed to fetch image directly."
            )
    finally:
        await client.aclose()


@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"Incoming request: {request.method} {request.url}")
    response = await call_next(request)
    logger.info(f"Request completed: {response.status_code}")
    return response