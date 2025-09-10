# backend_app/views/cursus_views.py

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from datetime import datetime
from dateutil.relativedelta import relativedelta
from ..models import Cursus, Deelnemer
from ..serializers import DeelnemerSerializer, CursusSerializer


@csrf_exempt
@api_view(['POST'])
def create_deelnemer_and_cursus(request):
    print("=== DEBUG START ===")
    
    cursusdatum_str = request.data.get('cursusdatum')
    geldigheid_jaren_str = request.data.get('geldigheid-jaren')
    geldigheid_datum_custom = request.data.get('geldigheid-datum-input')
    
    geldigheid_datum = None
    if geldigheid_jaren_str == 'custom' and geldigheid_datum_custom:
        geldigheid_datum = geldigheid_datum_custom
    elif cursusdatum_str and geldigheid_jaren_str and geldigheid_jaren_str.isdigit():
        cursusdatum = datetime.strptime(cursusdatum_str, '%Y-%m-%d').date()
        jaren = int(geldigheid_jaren_str)
        geldigheid_datum = cursusdatum + relativedelta(years=jaren)
    
    cursus_data = {
        'cursus': request.data.get('cursus'),
        'cursusdatum': cursusdatum_str if cursusdatum_str else None,
        'refresher': request.data.get('refreshercheck') == 'on',
        'geldigheid_jaren': geldigheid_jaren_str if geldigheid_jaren_str != 'Kies...' else None,
        'geldigheid_datum': geldigheid_datum
    }
    
    deelnemer_data = {
        'aanhef': request.data.get('aanhef') or None,
        'voornaam': request.data.get('voornaam') or None,
        'tussenvoegsel': request.data.get('tussenvoegsel') or None,
        'achternaam': request.data.get('achternaam') or None,
        'bedrijfsnaam': request.data.get('bedrijfsnaam') or None,
        'email': request.data.get('email') or None,
        'geboortedatum': request.data.get('geboortedatum') or None,
        'telefoonnummer': request.data.get('telefoonnummer') or None,
        'windaId': request.data.get('windaId') or None
    }
    
    try:
        with transaction.atomic():
            # Gebruik get_or_create() voor de cursus, die de uniekheid afdwingt
            cursus_instance, created_cursus = Cursus.objects.get_or_create(
                cursus=cursus_data['cursus'],
                cursusdatum=cursus_data['cursusdatum'],
                defaults=cursus_data
            )
            
            if created_cursus:
                print("Nieuwe cursus aangemaakt:", cursus_instance)
            else:
                print("Bestaande cursus gevonden:", cursus_instance)
                
            # Hiernaast wordt de deelnemer bijgewerkt of aangemaakt.
            deelnemer_instance, created_deelnemer = Deelnemer.objects.update_or_create(
                voornaam=deelnemer_data['voornaam'],
                achternaam=deelnemer_data['achternaam'],
                geboortedatum=deelnemer_data['geboortedatum'],
                defaults=deelnemer_data
            )
            
            if created_deelnemer:
                print("Nieuwe deelnemer aangemaakt:", deelnemer_instance)
            else:
                print("Bestaande deelnemer bijgewerkt:", deelnemer_instance)

            cursus_instance.deelnemers.add(deelnemer_instance)
            print("Koppeling gemaakt!")

            response_data = {
                "cursus_data": CursusSerializer(cursus_instance).data,
                "deelnemer_data": DeelnemerSerializer(deelnemer_instance).data
            }
            return Response(response_data, status=status.HTTP_201_CREATED)
    except Exception as e:
        print("Fout bij aanmaken/bijwerken:", str(e))
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def get_expiring_certificates(request):
    from datetime import date, timedelta
    
    days = int(request.GET.get('days', 30))
    expiry_date = date.today() + timedelta(days=days)
    
    show_sent = request.GET.get('show_sent', 'false').lower() == 'true'
    
    filter_criteria = {
        'geldigheid_datum__lte': expiry_date,
        'geldigheid_datum__gte': date.today()
    }
    
    if not show_sent:
        filter_criteria['reminder_sent'] = False
    
    expiring_cursussen = Cursus.objects.filter(**filter_criteria).select_related().prefetch_related('deelnemers')
    
    results = []
    for cursus in expiring_cursussen:
        for deelnemer in cursus.deelnemers.all():
            if deelnemer.email:
                results.append({
                    'deelnemer_id': deelnemer.id,
                    'cursus_id': cursus.id,
                    'naam': f"{deelnemer.voornaam} {deelnemer.achternaam}",
                    'email': deelnemer.email,
                    'cursus': cursus.cursus,
                    'expiry_date': cursus.geldigheid_datum,
                    'days_remaining': (cursus.geldigheid_datum - date.today()).days
                })
    
    return Response(results)