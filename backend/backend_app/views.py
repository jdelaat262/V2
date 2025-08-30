from rest_framework import viewsets, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import get_object_or_404, render
from django.template.loader import render_to_string
from django.http import HttpResponse, JsonResponse
from django.core.mail import EmailMessage
from django.conf import settings
from weasyprint import HTML
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


# CERTIFICAAT GENERATIE VIEWS
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