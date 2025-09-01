# backend_app/views.py

from rest_framework import viewsets, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import get_object_or_404, render
from django.template.loader import render_to_string
from django.http import HttpResponse, JsonResponse
from django.core.mail import EmailMessage
from django.core.mail import send_mail
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from weasyprint import HTML
from .models import Cursus, Deelnemer
from .serializers import DeelnemerSerializer, CursusSerializer
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta
from .models import QREvent, QRDeelnemer
from .serializers import QREventSerializer, QRDeelnemerSerializer
import json
import socket

class DeelnemerViewSet(viewsets.ModelViewSet):
    queryset = Deelnemer.objects.all()
    serializer_class = DeelnemerSerializer

@api_view(['GET'])
def ping_view(request):
    """
    Simpele view die een JSON-respons terugstuurt om de verbinding te testen.
    """
    return JsonResponse({"status": "Backend is bereikbaar!"})

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

    print("Cursus data opgebouwd:", cursus_data)
    print("Deelnemer data opgebouwd:", deelnemer_data)

    cursus_serializer = CursusSerializer(data=cursus_data)
    deelnemer_serializer = DeelnemerSerializer(data=deelnemer_data)

    print("Cursus serializer valid?", cursus_serializer.is_valid())
    print("Cursus serializer errors:", cursus_serializer.errors)
    print("Deelnemer serializer valid?", deelnemer_serializer.is_valid())
    print("Deelnemer serializer errors:", deelnemer_serializer.errors)

    if cursus_serializer.is_valid() and deelnemer_serializer.is_valid():
        try:
            with transaction.atomic():
                cursus_instance = cursus_serializer.save()

                deelnemer_instance, created = Deelnemer.objects.update_or_create(
                    voornaam=deelnemer_data['voornaam'],
                    achternaam=deelnemer_data['achternaam'],
                    geboortedatum=deelnemer_data['geboortedatum'],
                    defaults=deelnemer_data
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
        errors = {}
        if not cursus_serializer.is_valid():
            errors['cursus_errors'] = cursus_serializer.errors
        if not deelnemer_serializer.is_valid():
            errors['deelnemer_errors'] = deelnemer_serializer.errors
        
        print("Errors geretourneerd:", errors)
        return Response(errors, status=status.HTTP_400_BAD_REQUEST)

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

@api_view(['POST'])
def send_expiry_reminders(request):
    reminder_list = request.data.get('reminders', [])
    sent_count = 0
    
    try:
        for item in reminder_list:
            deelnemer = get_object_or_404(Deelnemer, id=item['deelnemer_id'])
            cursus = get_object_or_404(Cursus, id=item['cursus_id'])
            
            subject = f"Herinnering: Je certificaat voor {cursus.cursus} verloopt binnenkort"
            body = f"Beste {deelnemer.voornaam},\n\nJe certificaat voor {cursus.cursus} verloopt op {cursus.geldigheid_datum.strftime('%d-%m-%Y')}. \n\nMet vriendelijke groet,\nSafetyPro"
            
            if not deelnemer.email:
                continue

            email = EmailMessage(subject, body, settings.EMAIL_HOST_USER, [deelnemer.email])
            email.send()
            
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

@api_view(['GET'])
def generate_certificate_pdf(request, deelnemer_id, cursus_id):
    try:
        deelnemer = get_object_or_404(Deelnemer, pk=deelnemer_id)
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

@api_view(['GET'])
def preview_certificate_html(request, deelnemer_id, cursus_id):
    try:
        deelnemer = get_object_or_404(Deelnemer, pk=deelnemer_id)
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

@api_view(['POST'])
def send_certificate_email(request, deelnemer_id, cursus_id):
    try:
        deelnemer = get_object_or_404(Deelnemer, pk=deelnemer_id)
        cursus = deelnemer.cursussen.get(pk=cursus_id)

        context = {
            'deelnemer': deelnemer,
            'cursus': cursus,
        }
        html_string = render_to_string('certificaat_template.html', context)
        pdf_file = HTML(string=html_string, base_url=request.build_absolute_uri('/')).write_pdf()

        subject = f"Je certificaat voor de cursus {cursus.cursus}"
        body = f"Beste {deelnemer.voornaam},\n\nHierbij sturen wij je jouw certificaat voor de cursus '{cursus.cursus}', die je succesvol hebt afgerond. Je vindt het certificaat als bijlage bij deze e-mail.\n\nMet vriendelijke groet,\n\nSafetyPro"
        to_email = deelnemer.email
        
        email = EmailMessage(
            subject,
            body,
            settings.EMAIL_HOST_USER,
            [to_email],
        )
        
        email.attach(
            f"certificaat_{deelnemer.voornaam}_{deelnemer.achternaam}.pdf",
            pdf_file,
            'application/pdf'
        )

        email.send()
        
        return Response({"message": "E-mail succesvol verzonden!"}, status=status.HTTP_200_OK)

    except Deelnemer.DoesNotExist:
        return Response({"error": "Deelnemer niet gevonden."}, status=status.HTTP_404_NOT_FOUND)
    except Cursus.DoesNotExist:
        return Response({"error": "Cursus niet gevonden of niet gekoppeld aan deze deelnemer."}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": f"Fout bij het versturen van de e-mail: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_local_ip(request):
    try:
        hostname = socket.gethostname()
        ip_address = socket.gethostbyname(hostname)
        return JsonResponse({'local_ip': ip_address})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def qr_code_page_view(request):
    return render(request, 'qr-code-page.html')

def email_preview_view(request):
    return render(request, 'email-preview.html')

def qr_scan_form_view(request):
    return render(request, 'qr-scan-form.html')

def qr_code_generator_view(request):
    return render(request, 'qr-code-generator.html')

@api_view(['POST'])
def send_custom_reminders(request):
    try:
        data = json.loads(request.body)
        reminders = data.get('reminders', [])
        subject = data.get('subject', 'Herinnering certificaat')
        body = data.get('body', 'Je certificaat verloopt binnenkort.')

        sent_count = 0
        for reminder in reminders:
            deelnemer = get_object_or_404(Deelnemer, id=reminder['deelnemer_id'])
            
            # Controleer of e-mailadres niet leeg is
            if not deelnemer.email:
                continue

            email = EmailMessage(subject, body, settings.EMAIL_HOST_USER, [deelnemer.email])
            email.send()
            sent_count += 1
            
        return Response({"sent": sent_count}, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({"error": f"Fout bij het versturen van de e-mail: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

@api_view(['POST'])
def create_qr_deelnemer_and_event(request):
    try:
        data = request.data
        
        # 1. Maak de gebeurtenis aan
        qr_event_data = {
            'titel': data.get('cursusNaam'),
            'datum': data.get('cursusdatum'),
        }
        qr_event_serializer = QREventSerializer(data=qr_event_data)
        qr_event_serializer.is_valid(raise_exception=True)
        qr_event_instance = qr_event_serializer.save()

        # 2. Maak de QR-deelnemer aan en koppel hem aan de gebeurtenis
        qr_deelnemer_data = {
            'voornaam': data.get('voornaam'),
            'achternaam': data.get('achternaam'),
            'email': data.get('email'),
            'telefoonnummer': data.get('telefoonnummer'),
            'qr_event': qr_event_instance.id # Koppel de deelnemer aan het event
        }
        qr_deelnemer_serializer = QRDeelnemerSerializer(data=qr_deelnemer_data)
        qr_deelnemer_serializer.is_valid(raise_exception=True)
        qr_deelnemer_instance = qr_deelnemer_serializer.save()

        return Response({
            'message': 'Inschrijving succesvol.',
            'qr_event_id': qr_event_instance.id,
            'qr_deelnemer_id': qr_deelnemer_instance.id
        }, status=201)

    except Exception as e:
        return Response({'error': str(e)}, status=400)