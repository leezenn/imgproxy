import logging
from fastapi import FastAPI, HTTPException
from fastapi.requests import Request
import httpx
from os import getenv
from starlette.responses import StreamingResponse


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

timeout_config = httpx.Timeout(connect=20.0, read=30.0, write=20.0, pool=60.0)

username = getenv("IMGPROXY_PROXY_USERNAME")
password = getenv("IMGPROXY_PROXY_PASSWORD")
host = getenv("IMGPROXY_PROXY_HOST")
port = getenv("IMGPROXY_PROXY_PORT")


def get_proxy_config():
    if not all([username, password, host, port]):
        logger.warning(
            "Proxy configuration is incomplete. Direct requests will be used."
        )
        return None
    return {
        "http://": f"http://{username}:{password}@{host}:{port}",
    }


proxy = get_proxy_config()

app = FastAPI()


@app.get("/")
async def root():
    return {
        "message": "Proxy Manager is running. Use /fetch-image/ to fetch images via proxy."
    }


@app.get("/fetch-image/")
async def fetch_image(url: str):
    async with httpx.AsyncClient(timeout=timeout_config) as client:
        try:
            request = client.build_request("GET", url)
            response = await client.send(request, stream=True)
            response.raise_for_status()
            return StreamingResponse(
                response.aiter_raw(),
                media_type=response.headers.get("Content-Type"),
                headers=dict(response.headers),
            )
        except httpx.HTTPError:
            if proxy:
                try:
                    async with httpx.AsyncClient(
                        proxies=proxy, timeout=timeout_config
                    ) as client:
                        request = client.build_request("GET", url)
                        response = await client.send(request, stream=True)
                        response.raise_for_status()
                        return StreamingResponse(
                            response.aiter_raw(),
                            media_type=response.headers.get("Content-Type"),
                            headers=dict(response.headers),
                        )
                except httpx.HTTPError as e:
                    raise HTTPException(
                        status_code=502,
                        detail=f"Failed to fetch image via proxy: {str(e)}",
                    )
            raise HTTPException(
                status_code=502,
                detail="Failed to fetch image directly and no proxy available.",
            )


@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"Incoming request: {request.method} {request.url}")
    response = await call_next(request)
    logger.info(f"Request completed: {response.status_code}")
    return response
