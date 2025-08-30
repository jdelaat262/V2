from rest_framework import viewsets, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import JsonResponse
from .models import Cursus, Deelnemer
from .serializers import DeelnemerSerializer, CursusSerializer


class DeelnemerViewSet(viewsets.ModelViewSet):
    queryset = Deelnemer.objects.all()
    serializer_class = DeelnemerSerializer


def ping_view(request):
    """
    Simpele view die een JSON-respons terugstuurt om de verbinding te testen.
    """
    return JsonResponse({"status": "Backend is bereikbaar!"})


@api_view(['POST'])
def create_deelnemer_and_cursus(request):
    print("=== DEBUG START ===")
    print("Alle ontvangen data:", request.data)
    
    # Fix lege strings naar None voor datum velden
    cursus_data = {
        'cursus': request.data.get('cursus'),
        'cursusdatum': request.data.get('cursusdatum') if request.data.get('cursusdatum') else None,
        'refresher': request.data.get('refreshercheck') == 'on',
        'geldigheid_jaren': request.data.get('geldigheid-jaren') if request.data.get('geldigheid-jaren') != 'Kies...' else None,
        'geldigheid_datum': request.data.get('geldigheid-datum-input') if request.data.get('geldigheid-jaren') == 'custom' and request.data.get('geldigheid-datum-input') else None
    }
    
    deelnemer_data = {
        'aanhef': request.data.get('aanhef'),
        'voornaam': request.data.get('voornaam') if request.data.get('voornaam') else None,
        'tussenvoegsel': request.data.get('tussenvoegsel') if request.data.get('tussenvoegsel') else None,
        'achternaam': request.data.get('achternaam') if request.data.get('achternaam') else None,
        'bedrijfsnaam': request.data.get('bedrijfsnaam') if request.data.get('bedrijfsnaam') else None,
        'email': request.data.get('email') if request.data.get('email') else None,
        'geboortedatum': request.data.get('geboortedatum') if request.data.get('geboortedatum') else None,
        'telefoonnummer': request.data.get('telefoonnummer') if request.data.get('telefoonnummer') else None,
        'windaId': request.data.get('windaId') if request.data.get('windaId') else None
    }

    print("Cursus data opgebouwd:", cursus_data)
    print("Deelnemer data opgebouwd:", deelnemer_data)

    cursus_serializer = CursusSerializer(data=cursus_data)
    deelnemer_serializer = DeelnemerSerializer(data=deelnemer_data)

    print("Cursus serializer valid?", cursus_serializer.is_valid())
    print("Cursus serializer errors:", cursus_serializer.errors)
    print("Deelnemer serializer valid?", deelnemer_serializer.is_valid())
    print("Deelnemer serializer errors:", deelnemer_serializer.errors)

    if cursus_serializer.is_valid() and deelnemer_serializer.is_valid():
        cursus_instance = cursus_serializer.save()
        deelnemer_instance = deelnemer_serializer.save()
        print("Cursus instance aangemaakt:", cursus_instance)
        print("Deelnemer instance aangemaakt:", deelnemer_instance)
        
        cursus_instance.deelnemers.add(deelnemer_instance)
        print("Koppeling gemaakt!")
        
        response_data = {
            "cursus_data": cursus_serializer.data,
            "deelnemer_data": deelnemer_serializer.data
        }
        
        return Response(response_data, status=status.HTTP_201_CREATED)
    else:
        errors = {}
        if not cursus_serializer.is_valid():
            errors['cursus_errors'] = cursus_serializer.errors
        if not deelnemer_serializer.is_valid():
            errors['deelnemer_errors'] = deelnemer_serializer.errors
        
        print("Errors geretourneerd:", errors)
        return Response(errors, status=status.HTTP_400_BAD_REQUEST)