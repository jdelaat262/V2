# backend_app/views/qr_views.py

from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from ..models import QREvent, QRDeelnemer


def qr_code_page_view(request):
    return render(request, 'qr-code-page.html')


def qr_scan_form_view(request):
    return render(request, 'qr-scan-form.html')


def qr_code_generator_view(request):
    return render(request, 'qr-code-generator.html')


@csrf_exempt
@api_view(['POST'])
def create_qr_deelnemer_and_event(request):
    try:
        data = request.data
        
        # 1. Haal de cursusgegevens op
        cursus_naam = data.get('cursusNaam')
        cursus_datum = data.get('cursusdatum')
        
        # 2. Gebruik get_or_create() om te garanderen dat het QREvent uniek is
        qr_event_instance, created = QREvent.objects.get_or_create(
            titel=cursus_naam,
            datum=cursus_datum,
            defaults={
                'locatie': data.get('locatie', '')
            }
        )
        
        # 3. Gebruik update_or_create() om de QRDeelnemer bij te werken of aan te maken
        #    Dit voorkomt duplicaten in de deelnemerslijst
        deelnemer_data = {
            'voornaam': data.get('voornaam'),
            'achternaam': data.get('achternaam'),
            'email': data.get('email'),
            'telefoonnummer': data.get('telefoonnummer'),
        }
        qr_deelnemer_instance, created = QRDeelnemer.objects.update_or_create(
            voornaam=deelnemer_data['voornaam'],
            achternaam=deelnemer_data['achternaam'],
            defaults={**deelnemer_data, 'qr_event': qr_event_instance}
        )

        return Response({
            'message': 'Inschrijving succesvol.',
            'qr_event_id': qr_event_instance.id,
            'qr_deelnemer_id': qr_deelnemer_instance.id
        }, status=201)

    except Exception as e:
        return Response({'error': str(e)}, status=400)