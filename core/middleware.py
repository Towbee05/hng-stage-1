import logging
import time

logger = logging.getLogger(__name__)

class CustomLoggerMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start_time = time.time()
        response = self.get_response(request)
        response_time = time.time() - start_time

        logger.info(
            f"Method: {request.method} | "
            f"Endpoint: {request.path} | "
            f"Status: {response.status_code} | "
            f"Response-Time: {response_time:.4f}ms"
        )

        return response
