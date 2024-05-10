import logging
from fastapi import FastAPI, HTTPException
from fastapi.requests import Request
import httpx
from os import getenv
import base64

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
        response = await client.get(url)
        response.raise_for_status()
        return response.content
    except (httpx.RequestError, httpx.HTTPStatusError) as e:
        if proxy:
            try:
                proxy_response = await client.get(url, proxies={"all://": proxy})
                proxy_response.raise_for_status()
                return proxy_response.content
            except (httpx.RequestError, httpx.HTTPStatusError):
                raise HTTPException(
                    status_code=502,
                    detail="Failed to fetch image via direct and proxy methods.",
                )
        else:
            raise HTTPException(status_code=502, detail=str(e))
    finally:
        await client.aclose()


@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"Incoming request: {request.method} {request.url}")
    response = await call_next(request)
    logger.info(f"Request completed: {response.status_code}")
    return response