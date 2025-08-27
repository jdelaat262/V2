from django.contrib import admin
from .models import Cursus, Deelnemer

# Registreer je modellen
admin.site.register(Cursus)
admin.site.register(Deelnemer)