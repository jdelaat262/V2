# backend_app/views/utility_views.py

from rest_framework.decorators import api_view
from django.http import JsonResponse
import socket


@api_view(['GET'])
def ping_view(request):
    """
    Simpele view die een JSON-respons terugstuurt om de verbinding te testen.
    """
    return JsonResponse({"status": "Backend is bereikbaar!"})


@api_view(['GET'])
def get_local_ip(request):
    try:
        hostname = socket.gethostname()
        ip_address = socket.gethostbyname(hostname)
        return JsonResponse({'local_ip': ip_address})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)