import logging
from fastapi import FastAPI, HTTPException
from fastapi.requests import Request
import httpx
from os import getenv
from starlette.responses import StreamingResponse


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


username = getenv("IMGPROXY_PROXY_USERNAME")
password = getenv("IMGPROXY_PROXY_PASSWORD")
host = getenv("IMGPROXY_PROXY_HOST")
port = getenv("IMGPROXY_PROXY_PORT")

allowed_headers = [
    "content-type",
    "content-length",
    "content-encoding",
    "etag",
    "cache-control",
]


def get_proxy_config():
    if not all([username, password, host, port]):
        logger.warning(
            "Proxy configuration is incomplete. Direct requests will be used."
        )
        return None
    return {
        "http": f"http://{username}:{password}@{host}:{port}",
        "https": f"https://{username}:{password}@{host}:{port}",
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
    async with httpx.AsyncClient(proxies=proxy if proxy else None) as client:
        try:
            response = await client.get(url, stream=True)
            response.raise_for_status()
            response_headers = {
                key: value
                for key, value in response.headers.items()
                if key.lower() in allowed_headers
            }
            return StreamingResponse(
                response.aiter_raw(),
                media_type=response.headers.get("Content-Type"),
                headers=response_headers,
            )
        except httpx.HTTPError as e:
            logger.error(f"Failed to fetch image: {str(e)}")
            raise HTTPException(status_code=502, detail="Failed to fetch image.")


@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"Incoming request: {request.method} {request.url}")
    response = await call_next(request)
    logger.info(f"Request completed: {response.status_code}")
    return response