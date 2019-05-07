from threading import current_thread
from django.utils.deprecation import MiddlewareMixin
_requests = {}

def get_username():

    req = _requests.get(current_thread().ident, None)
    return getattr(req, 'user', None)

class RequestMiddleware(MiddlewareMixin):
    def process_request(self, request):
        _requests[current_thread().ident] = request

    def process_response(self, request, response):
        _requests.pop(current_thread().ident, None)
        return response

    def process_exception(self, request, Exception):
        _requests.pop(current_thread().ident, None)
