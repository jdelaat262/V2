from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (DeelnemerViewSet, ping_view, create_deelnemer_and_cursus, 
                   generate_certificate_pdf, preview_certificate_html, send_certificate_email)

router = DefaultRouter()
router.register(r'deelnemers', DeelnemerViewSet)

urlpatterns = [
    path('', include(router.urls)), 
    path('deelnemer-cursus/', create_deelnemer_and_cursus, name='deelnemer-cursus'),
    path('ping/', ping_view, name='ping'),
    path('generate-certificate/<int:deelnemer_id>/<int:cursus_id>/', generate_certificate_pdf, name='generate-certificate-pdf'),
    path('preview-certificate/<int:deelnemer_id>/<int:cursus_id>/', preview_certificate_html, name='preview-certificate'),
    path('send-certificate/<int:deelnemer_id>/<int:cursus_id>/', send_certificate_email, name='send-certificate-email'),
]