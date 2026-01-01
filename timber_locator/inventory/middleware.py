import re
from django.http import HttpResponseBadRequest

AZURE_PROBE_RE = re.compile(r"^169\.254\.\d+\.\d+$")

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
