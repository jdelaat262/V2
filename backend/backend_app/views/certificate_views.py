# backend_app/views/certificate_views.py

from rest_framework.decorators import api_view
from django.shortcuts import get_object_or_404, render
from django.template.loader import render_to_string
from django.http import HttpResponse
from weasyprint import HTML
from ..models import Cursus, Deelnemer


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