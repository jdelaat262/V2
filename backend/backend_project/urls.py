from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include('backend_app.urls')),
    
    # Frontend routes
    path('', TemplateView.as_view(template_name='index.html'), name='home'),
    path('qr-generator/', TemplateView.as_view(template_name='qr-code-generator.html'), name='qr_generator'),
    path('qr-code/', TemplateView.as_view(template_name='qr-code-page.html'), name='qr_code'),
    path('qr-scan/', TemplateView.as_view(template_name='qr-scan-form.html'), name='qr_scan'),
    path('reminders/', TemplateView.as_view(template_name='reminders.html'), name='reminders'),
]

# Serve static files in development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])