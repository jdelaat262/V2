from django.urls import path
from django.shortcuts import render
from .views import ping_view, create_deelnemer_and_cursus, home_view, qr_code_generator_view, qr_code_page_view, qr_scan_form_view, reminders_view

urlpatterns = [
    path('', home_view, name='home'),
    path('qr-code-generator', qr_code_generator_view, name='qr-code-generator'),
    path('qr-code-page', qr_code_page_view, name='qr-code-page'),
    path('qr-scan-form', qr_scan_form_view, name='qr-scan-form'),
    path('reminders', reminders_view, name='reminders'),
    path('ping/', ping_view, name='ping'),
    path('api/v1/deelnemer-cursus/', create_deelnemer_and_cursus, name='deelnemer-cursus'),
]
