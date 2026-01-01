import os
import re
import logging
from django.conf import settings
from django.http import HttpResponseBadRequest

AZURE_PROBE_RE = re.compile(r"^169\.254\.\d+\.\d+$")

def _raw_host(meta):
    host = meta.get("HTTP_HOST") or meta.get("SERVER_NAME") or ""
    return host.split(":")[0]


class ProxyHeaderNormalizeMiddleware:
    """
    Normalize X-Forwarded-Proto so Django sees HTTPS correctly behind proxies.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        xfp = request.META.get("HTTP_X_FORWARDED_PROTO")
        if xfp and "https" in xfp:
            request.META["HTTP_X_FORWARDED_PROTO"] = "https"
            request.META["wsgi.url_scheme"] = "https"
        return self.get_response(request)

class ProxyHeaderDebugMiddleware:
    """
    Logs proxy-related headers once per process to help debug HTTPS redirect loops.
    Enable with DJANGO_LOG_PROXY_HEADERS=True.
    """
    _logged = False

    def __init__(self, get_response):
        self.get_response = get_response
        self.logger = logging.getLogger("django")

    def __call__(self, request):
        if not ProxyHeaderDebugMiddleware._logged:
            if os.environ.get("DJANGO_LOG_PROXY_HEADERS", "False") == "True":
                host = _raw_host(request.META)
                if not AZURE_PROBE_RE.match(host):
                    self.logger.info(
                        "proxy-debug is_secure=%s xfp=%s host=%s secure_redirect=%s in_azure=%s debug=%s",
                        request.is_secure(),
                        request.META.get("HTTP_X_FORWARDED_PROTO"),
                        host,
                        settings.SECURE_SSL_REDIRECT,
                        getattr(settings, "IN_AZURE", False),
                        settings.DEBUG,
                    )
                    ProxyHeaderDebugMiddleware._logged = True
        return self.get_response(request)


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
        host = _raw_host(request.META)
        if AZURE_PROBE_RE.match(host):
            # rewrite to a valid host
            request.META["HTTP_HOST"] = "localhost"
            request.META["SERVER_NAME"] = "localhost"
        return self.get_response(request)
