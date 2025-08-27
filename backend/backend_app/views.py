from django.http import JsonResponse
from rest_framework import viewsets
from .models import Cursus, Deelnemer
from .serializers import DeelnemerSerializer

def ping_view(request):
    """
    Simpele view die een JSON-respons terugstuurt om de verbinding te testen.
    """
    return JsonResponse({"status": "Backend is bereikbaar!"})

class DeelnemerViewSet(viewsets.ModelViewSet):
    queryset = Deelnemer.objects.all()
    serializer_class = DeelnemerSerializer