import os
import logging
import time
from dotenv import load_dotenv


logger = logging.getLogger(__name__)
load_dotenv()
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

class AddHeaderToRequest:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.META['x-vercel-protection-bypass'] = os.getenv("VERCEL_BYPASS")

        response = self.get_response(request)
        return response
