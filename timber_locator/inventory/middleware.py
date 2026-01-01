import re
import os
import logging
from django.http import HttpResponseBadRequest

AZURE_PROBE_RE = re.compile(r"^169\.254\.\d+\.\d+$")
logger = logging.getLogger(__name__)

class AllowAzureProbesMiddleware:
    """
    Azure internal health probes sometimes hit your app with Host like:
    169.254.x.x:8000
    Django rejects it before your views run. This middleware rewrites it
    to a safe host that is already in ALLOWED_HOSTS.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        host = request.get_host().split(":")[0]
        if AZURE_PROBE_RE.match(host):
            # rewrite to a valid host
            request.META["HTTP_HOST"] = "localhost"
            request.META["SERVER_NAME"] = "localhost"
        return self.get_response(request)


class ProxyHeaderDebugMiddleware:
    """
    Logs proxy-related headers once per process to help debug HTTPS redirect loops.
    Enable with DJANGO_LOG_PROXY_HEADERS=True.
    """
    _logged = False

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not ProxyHeaderDebugMiddleware._logged:
            if os.environ.get("DJANGO_LOG_PROXY_HEADERS", "False") == "True":
                logger.info(
                    "proxy-debug is_secure=%s xfp=%s host=%s",
                    request.is_secure(),
                    request.META.get("HTTP_X_FORWARDED_PROTO"),
                    request.get_host(),
                )
                ProxyHeaderDebugMiddleware._logged = True
        return self.get_response(request)
