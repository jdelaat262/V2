from django.contrib import admin
from .models import Cursus, Deelnemer

class DeelnemerInline(admin.TabularInline):
    model = Cursus.deelnemers.through
    extra = 1
    verbose_name = "Deelnemer"
    verbose_name_plural = "Deelnemers"

class CursusInline(admin.TabularInline):
    model = Cursus.deelnemers.through
    extra = 1
    verbose_name = "Cursus"
    verbose_name_plural = "Cursussen"

class DeelnemerAdmin(admin.ModelAdmin):
    list_display = ['voornaam', 'tussenvoegsel', 'achternaam', 'email', 'bedrijfsnaam']
    inlines = [CursusInline]  # Toont cursussen bij elke deelnemer
    
class CursusAdmin(admin.ModelAdmin):
    list_display = ['cursus', 'cursusdatum', 'refresher']
    inlines = [DeelnemerInline]  # Toont deelnemers bij elke cursus
    filter_horizontal = ('deelnemers',)  # Extra selector voor bulk toevoegen

admin.site.register(Deelnemer, DeelnemerAdmin)
admin.site.register(Cursus, CursusAdmin)