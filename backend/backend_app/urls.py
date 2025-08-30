from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DeelnemerViewSet, ping_view, create_deelnemer_and_cursus

router = DefaultRouter()
router.register(r'deelnemers', DeelnemerViewSet)

urlpatterns = [
    path('', include(router.urls)), 
    path('deelnemer-cursus/', create_deelnemer_and_cursus, name='deelnemer-cursus'),
    path('ping/', ping_view, name='ping'), 
]