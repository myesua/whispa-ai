# app/middleware/prometheus.py
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from prometheus_client import Histogram, Counter, generate_latest
import time

REQUEST_COUNT = Counter(
    'http_requests_total', 'Total HTTP requests',
    ['method', 'endpoint', 'status_code']
)

REQUEST_LATENCY = Histogram(
    'http_request_duration_seconds', 'HTTP request latency (seconds)',
    ['method', 'endpoint']
)

class PrometheusMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.url.path == "/metrics":
            return await call_next(request)

        method = request.method
        endpoint = request.url.path
        
        start_time = time.time()
        
        try:
            response = await call_next(request)
        except Exception as e:
            status_code = 500
            raise e
        finally:
            end_time = time.time()
            process_time = end_time - start_time
            status_code = response.status_code if 'response' in locals() else 500
            REQUEST_COUNT.labels(method=method, endpoint=endpoint, status_code=status_code).inc()
            REQUEST_LATENCY.labels(method=method, endpoint=endpoint).observe(process_time)
            
        return response

async def metrics_endpoint(request: Request):
    return Response(generate_latest(), media_type="text/plain")