from rest_framework import viewsets, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import get_object_or_404, render
from django.template.loader import render_to_string
from django.http import HttpResponse, JsonResponse
from django.core.mail import EmailMessage
from django.core.mail import send_mail  # Importeer send_mail
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt  # TOEGEVOEGD
from django.utils.decorators import method_decorator  # TOEGEVOEGD
from weasyprint import HTML
from .models import Cursus, Deelnemer
from .serializers import DeelnemerSerializer, CursusSerializer
from datetime import datetime
from dateutil.relativedelta import relativedelta
from datetime import date, timedelta
import json  
from django.db import transaction

@method_decorator(csrf_exempt, name='dispatch')  # TOEGEVOEGD
class DeelnemerViewSet(viewsets.ModelViewSet):
    queryset = Deelnemer.objects.all()
    serializer_class = DeelnemerSerializer


def ping_view(request):
    """
    Simpele view die een JSON-respons terugstuurt om de verbinding te testen.
    """
    return JsonResponse({"status": "Backend is bereikbaar!"})


# backend_app/views.py

@csrf_exempt
@api_view(['POST'])
def create_deelnemer_and_cursus(request):
    from datetime import datetime
    from dateutil.relativedelta import relativedelta
    
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
    
    # We gebruiken de serializer om de data te verwerken en te valideren
    cursus_serializer = CursusSerializer(data=cursus_data)

    # We controleren alleen of de cursusgegevens valide zijn
    if cursus_serializer.is_valid():
        try:
            with transaction.atomic():
                cursus_instance = cursus_serializer.save()

                # Gebruik update_or_create om duplicaten te voorkomen
                deelnemer_instance, created = Deelnemer.objects.update_or_create(
                    voornaam=request.data.get('voornaam'),
                    achternaam=request.data.get('achternaam'),
                    geboortedatum=request.data.get('geboortedatum'),
                    defaults={
                        'aanhef': request.data.get('aanhef'),
                        'tussenvoegsel': request.data.get('tussenvoegsel'),
                        'bedrijfsnaam': request.data.get('bedrijfsnaam'),
                        'email': request.data.get('email'),
                        'telefoonnummer': request.data.get('telefoonnummer'),
                        'windaId': request.data.get('windaId')
                    }
                )
                
                if created:
                    print("Nieuwe deelnemer aangemaakt:", deelnemer_instance)
                else:
                    print("Bestaande deelnemer bijgewerkt:", deelnemer_instance)

                cursus_instance.deelnemers.add(deelnemer_instance)
                print("Koppeling gemaakt!")

                response_data = {
                    "cursus_data": cursus_serializer.data,
                    "deelnemer_data": DeelnemerSerializer(deelnemer_instance).data
                }
                
                return Response(response_data, status=status.HTTP_201_CREATED)
        except Exception as e:
            print("Fout bij aanmaken/bijwerken:", str(e))
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        print("Errors geretourneerd:", cursus_serializer.errors)
        return Response(cursus_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
@csrf_exempt  # TOEGEVOEGD
@api_view(['GET'])
def get_expiring_certificates(request):
    from datetime import date, timedelta
    
    # Aantal dagen uit query parameter (default 30)
    days = int(request.GET.get('days', 30))
    expiry_date = date.today() + timedelta(days=days)
    
    # Check if we should show sent reminders too
    show_sent = request.GET.get('show_sent', 'false').lower() == 'true'
    
    # Vind alle cursussen die binnen X dagen verlopen
    filter_criteria = {
        'geldigheid_datum__lte': expiry_date,
        'geldigheid_datum__gte': date.today()
    }
    
    # Add reminder_sent filter if we don't want to show sent reminders
    if not show_sent:
        filter_criteria['reminder_sent'] = False
    
    expiring_cursussen = Cursus.objects.filter(**filter_criteria).select_related().prefetch_related('deelnemers')
    
    results = []
    for cursus in expiring_cursussen:
        for deelnemer in cursus.deelnemers.all():
            if deelnemer.email:  # Alleen met email
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

@csrf_exempt  # TOEGEVOEGD
@api_view(['POST'])
def send_expiry_reminders(request):
    # Ontvangt lijst van deelnemer/cursus IDs
    reminder_list = request.data.get('reminders', [])
    sent_count = 0
    
    try:
        for item in reminder_list:
            deelnemer = get_object_or_404(Deelnemer, id=item['deelnemer_id'])
            cursus = get_object_or_404(Cursus, id=item['cursus_id'])
            
            # Email content
            subject = f"Herinnering: Je certificaat voor {cursus.cursus} verloopt binnenkort"
            body = f"Beste {deelnemer.voornaam},\n\nJe certificaat voor {cursus.cursus} verloopt op {cursus.geldigheid_datum.strftime('%d-%m-%Y')}. \n\nMet vriendelijke groet,\nSafetyPro"
            
            # Controleer of e-mailadres niet leeg is
            if not deelnemer.email:
                continue

            email = EmailMessage(subject, body, settings.EMAIL_HOST_USER, [deelnemer.email])
            email.send()
            
            # NIEUW: Markeer cursus als reminder verzonden
            cursus.reminder_sent = True
            cursus.save()
            sent_count += 1
        
        return Response({"sent": sent_count}, status=status.HTTP_200_OK)
    
    except Deelnemer.DoesNotExist:
        return Response({"error": "Deelnemer niet gevonden."}, status=status.HTTP_404_NOT_FOUND)
    except Cursus.DoesNotExist:
        return Response({"error": "Cursus niet gevonden of niet gekoppeld aan deze deelnemer."}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": f"Fout bij het versturen van de e-mail: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# CERTIFICAAT GENERATIE VIEWS
@csrf_exempt  # TOEGEVOEGD
@api_view(['GET'])
def generate_certificate_pdf(request, deelnemer_id, cursus_id):
    """
    Genereert een PDF-certificaat voor een specifieke deelnemer en cursus.
    """
    try:
        deelnemer = get_object_or_404(Deelnemer, pk=deelnemer_id)
        # Zoek de specifieke cursus die bij de deelnemer hoort
        cursus = deelnemer.cursussen.get(pk=cursus_id)
        
        context = {
            'deelnemer': deelnemer,
            'cursus': cursus,
        }

        html_string = render_to_string('certificaat_template.html', context)
        
        pdf_file = HTML(string=html_string, base_url=request.build_absolute_uri('/')).write_pdf()

        response = HttpResponse(pdf_file, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="certificaat_{deelnemer.voornaam}_{deelnemer.achternaam}_{cursus.id}.pdf"'
        return response

    except Deelnemer.DoesNotExist:
        return HttpResponse("Deelnemer niet gevonden.", status=404)
    except Cursus.DoesNotExist:
        return HttpResponse("Cursus niet gevonden of niet gekoppeld aan deze deelnemer.", status=404)
    except Exception as e:
        return HttpResponse(f"Fout bij het genereren van het certificaat: {str(e)}", status=500)


@csrf_exempt  # TOEGEVOEGD
@api_view(['GET'])
def preview_certificate_html(request, deelnemer_id, cursus_id):
    """
    Toont een HTML-preview van het certificaat in de browser.
    """
    try:
        deelnemer = get_object_or_404(Deelnemer, pk=deelnemer_id)
        # Zoek de specifieke cursus die bij de deelnemer hoort
        cursus = deelnemer.cursussen.get(pk=cursus_id)
        
        if not cursus:
            return HttpResponse("Geen cursus gevonden voor deze deelnemer.", status=404)

        context = {
            'deelnemer': deelnemer,
            'cursus': cursus,
        }
        
        return render(request, 'certificaat_template.html', context)

    except Deelnemer.DoesNotExist:
        return HttpResponse("Deelnemer niet gevonden.", status=404)
    except Cursus.DoesNotExist:
        return HttpResponse("Cursus niet gevonden of niet gekoppeld aan deze deelnemer.", status=404)
    except Exception as e:
        return HttpResponse(f"Fout bij het genereren van de preview: {str(e)}", status=500)


@csrf_exempt  # TOEGEVOEGD
@api_view(['POST'])
def send_certificate_email(request, deelnemer_id, cursus_id):
    """
    Genereert een PDF-certificaat en verstuurt dit als e-mailbijlage naar de deelnemer.
    """
    try:
        deelnemer = get_object_or_404(Deelnemer, pk=deelnemer_id)
        cursus = deelnemer.cursussen.get(pk=cursus_id)

        # 1. Genereer de PDF
        context = {
            'deelnemer': deelnemer,
            'cursus': cursus,
        }
        html_string = render_to_string('certificaat_template.html', context)
        pdf_file = HTML(string=html_string, base_url=request.build_absolute_uri('/')).write_pdf()

        # 2. Maak de e-mail aan
        subject = f"Je certificaat voor de cursus {cursus.cursus}"
        body = f"Beste {deelnemer.voornaam},\n\nHierbij sturen wij je jouw certificaat voor de cursus '{cursus.cursus}', die je succesvol hebt afgerond. Je vindt het certificaat als bijlage bij deze e-mail.\n\nMet vriendelijke groet,\n\nSafetyPro"
        to_email = deelnemer.email
        
        email = EmailMessage(
            subject,
            body,
            settings.EMAIL_HOST_USER,  # Gebruikt de zender uit settings.py
            [to_email],
        )
        
        # 3. Voeg de PDF toe als bijlage
        email.attach(
            f"certificaat_{deelnemer.voornaam}_{deelnemer.achternaam}.pdf",
            pdf_file,
            'application/pdf'
        )

        # 4. Verzend de e-mail
        email.send()
        
        return Response({"message": "E-mail succesvol verzonden!"}, status=status.HTTP_200_OK)

    except Deelnemer.DoesNotExist:
        return Response({"error": "Deelnemer niet gevonden."}, status=status.HTTP_404_NOT_FOUND)
    except Cursus.DoesNotExist:
        return Response({"error": "Cursus niet gevonden of niet gekoppeld aan deze deelnemer."}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": f"Fout bij het versturen van de e-mail: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)