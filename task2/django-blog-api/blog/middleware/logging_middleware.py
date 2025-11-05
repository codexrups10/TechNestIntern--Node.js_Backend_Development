
import logging
import time
import json
from django.utils.deprecation import MiddlewareMixin
from django.http import JsonResponse

logger = logging.getLogger('blog')


class LoggingMiddleware(MiddlewareMixin):
    """
    Custom middleware for logging API requests and responses
    """

    def process_request(self, request):
        """Log incoming requests"""
        request._start_time = time.time()

        # Log request details
        log_data = {
            'method': request.method,
            'path': request.path,
            'user': str(request.user) if hasattr(request, 'user') and request.user.is_authenticated else 'Anonymous',
            'ip_address': self.get_client_ip(request),
            'user_agent': request.META.get('HTTP_USER_AGENT', ''),
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
        }

        # Log request body for POST/PUT/PATCH requests (but mask sensitive data)
        if request.method in ['POST', 'PUT', 'PATCH']:
            try:
                if hasattr(request, 'body') and request.body:
                    body = json.loads(request.body.decode('utf-8'))
                    # Mask sensitive fields
                    if isinstance(body, dict):
                        for field in ['password', 'password_confirm', 'token']:
                            if field in body:
                                body[field] = '***MASKED***'
                    log_data['request_body'] = body
            except (json.JSONDecodeError, UnicodeDecodeError):
                log_data['request_body'] = 'Unable to parse request body'

        logger.info(f"REQUEST: {json.dumps(log_data, indent=2)}")
        return None

    def process_response(self, request, response):
        """Log outgoing responses"""
        if hasattr(request, '_start_time'):
            duration = time.time() - request._start_time

            log_data = {
                'method': request.method,
                'path': request.path,
                'status_code': response.status_code,
                'duration_ms': round(duration * 1000, 2),
                'user': str(request.user) if hasattr(request, 'user') and request.user.is_authenticated else 'Anonymous',
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
            }

            # Log response for errors or if it's JSON
            if response.status_code >= 400:
                try:
                    if hasattr(response, 'content'):
                        content = response.content.decode('utf-8')
                        if content:
                            log_data['response_body'] = json.loads(content)
                except (json.JSONDecodeError, UnicodeDecodeError):
                    log_data['response_body'] = 'Unable to parse response body'

            if response.status_code >= 400:
                logger.error(f"RESPONSE ERROR: {json.dumps(log_data, indent=2)}")
            else:
                logger.info(f"RESPONSE: {json.dumps(log_data, indent=2)}")

        return response

    def process_exception(self, request, exception):
        """Log exceptions"""
        log_data = {
            'method': request.method,
            'path': request.path,
            'user': str(request.user) if hasattr(request, 'user') and request.user.is_authenticated else 'Anonymous',
            'exception_type': type(exception).__name__,
            'exception_message': str(exception),
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
        }

        logger.error(f"EXCEPTION: {json.dumps(log_data, indent=2)}", exc_info=True)
        return None

    def get_client_ip(self, request):
        """Get the client's IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
