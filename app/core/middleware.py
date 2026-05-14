import time
import uuid
from fastapi import Request

SLOW_REQUEST_THRESHOLD_MS = 500


async def log_request_timing(request: Request, call_next):
    start = time.time()
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id
    response = await call_next(request)
    duration = (time.time() - start) * 1000
    print(f"[{request_id}] {request.method} {request.url.path} — {duration:.1f}ms")
    return response


async def add_request_id(request: Request, call_next):
    request_id = getattr(request.state, "request_id", str(uuid.uuid4()))
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response


async def log_slow_requests(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    duration = (time.time() - start) * 1000
    if duration > SLOW_REQUEST_THRESHOLD_MS:
        print(f"SLOW REQUEST: {request.method} {request.url.path} — {duration:.1f}ms")
    return response
