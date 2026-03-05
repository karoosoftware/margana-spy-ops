import logging, time
from fastapi import FastAPI, Request

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s - %(message)s"
)
logger = logging.getLogger("api.access")

app = FastAPI()

@app.middleware("http")
async def log_request(request: Request, call_next):
    start = time.perf_counter()
    client = request.client.host if request.client else "unknown"

    try:
        response = await call_next(request)
        duration_ms = (time.perf_counter() - start) * 1000
        status = response.status_code

        log_msg = "%s %s from=%s status=%s duration_ms=%.2f"
        log_args = (
            request.method,
            request.url.path,
            client,
            status,
            duration_ms,
        )

        if status >= 500:
            logger.error(log_msg, *log_args)
        elif status >= 400:
            logger.warning(log_msg, *log_args)
        else:
            logger.info(log_msg, *log_args)

        return response

    except Exception:
        duration_ms = (time.perf_counter() - start) * 1000
        logger.exception(
            "%s %s from=%s status=500 duration_ms=%.2f",
            request.method,
            request.url.path,
            client,
            duration_ms,
        )
        raise


@app.get("/")
def hello():
    return {"message": "hello world"}