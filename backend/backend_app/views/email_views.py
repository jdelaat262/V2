# backend_app/views/email_views.py

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import get_object_or_404, render
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.conf import settings
from weasyprint import HTML
from ..models import Cursus, Deelnemer
import json


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


def email_preview_view(request):
    return render(request, 'email-preview.html')