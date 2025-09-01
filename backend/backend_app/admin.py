from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from .models import Cursus, Deelnemer

class DeelnemerInline(admin.TabularInline):
    model = Cursus.deelnemers.through
    extra = 1
    verbose_name = "Deelnemer"
    verbose_name_plural = "Deelnemers"
    readonly_fields = ('certificaat_actions',)

    def certificaat_actions(self, obj):
        if obj.id:
            # We creëren alleen de URL voor de Preview
            preview_url = reverse('preview-certificate', args=[obj.deelnemer.id, obj.cursus.id])
            return format_html(
                '<a href="{}" target="_blank" class="button">Preview</a>',
                preview_url
            )
        return "Sla eerst op"
    certificaat_actions.short_description = "Certificaat"

class CursusInline(admin.TabularInline):
    model = Cursus.deelnemers.through
    extra = 1
    verbose_name = "Cursus"
    verbose_name_plural = "Cursussen"
    readonly_fields = ('certificaat_actions',)

    def certificaat_actions(self, obj):
        if obj.id:
            # We creëren alleen de URL voor de Preview
            preview_url = reverse('preview-certificate', args=[obj.deelnemer.id, obj.cursus.id])
            return format_html(
                '<a href="{}" target="_blank" class="button">Preview</a>',
                preview_url
            )
        return "Sla eerst op"
    certificaat_actions.short_description = "Certificaat"

class DeelnemerAdmin(admin.ModelAdmin):
    list_display = ['voornaam', 'tussenvoegsel', 'achternaam', 'email', 'bedrijfsnaam']
    inlines = [CursusInline]
    
class CursusAdmin(admin.ModelAdmin):
    list_display = ['cursus', 'cursusdatum', 'refresher']
    inlines = [DeelnemerInline]
    filter_horizontal = ('deelnemers',)

admin.site.register(Deelnemer, DeelnemerAdmin)
admin.site.register(Cursus, CursusAdmin)