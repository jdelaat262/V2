from django.urls import path
from .views import ping_view, create_deelnemer_and_cursus

urlpatterns = [
    path('deelnemer-cursus/', create_deelnemer_and_cursus, name='deelnemer-cursus'),
    path('ping/', ping_view, name='ping'),
]