from rest_framework import viewsets, status
from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Cursus, Deelnemer
from .serializers import DeelnemerSerializer, CursusSerializer

@api_view(['POST'])
def create_deelnemer_and_cursus(request):
    cursus_data = {
        'cursus_naam': request.data.get('cursus_naam'),
        'cursusdatum': request.data.get('cursusdatum'),
        'refresher': request.data.get('refresher'),
        'geldigheid_jaren': request.data.get('geldigheid_jaren'),
        'geldigheid_datum': request.data.get('geldigheid_datum')
    }
    
    deelnemer_data = {
        'aanhef': request.data.get('aanhef'),
        'voornaam': request.data.get('voornaam'),
        'tussenvoegsel': request.data.get('tussenvoegsel'),
        'achternaam': request.data.get('achternaam'),
        'bedrijfsnaam': request.data.get('bedrijfsnaam'),
        'email': request.data.get('email'),
        'geboortedatum': request.data.get('geboortedatum'),
        'telefoonnummer': request.data.get('telefoonnummer'),
        'windaId': request.data.get('windaId')
    }

    cursus_serializer = CursusSerializer(data=cursus_data)
    deelnemer_serializer = DeelnemerSerializer(data=deelnemer_data)

    if cursus_serializer.is_valid() and deelnemer_serializer.is_valid():
        cursus_instance = cursus_serializer.save()
        deelnemer_instance = deelnemer_serializer.save()
        deelnemer_instance.cursussen.add(cursus_instance)
        return Response(deelnemer_serializer.data, status=status.HTTP_201_CREATED)

    return Response(deelnemer_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

def ping_view(request):
    """
    Simpele view die een JSON-respons terugstuurt om de verbinding te testen.
    """
    return JsonResponse({"status": "Backend is bereikbaar!"})