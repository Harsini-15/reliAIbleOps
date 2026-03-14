"""reliableops URL Configuration"""
from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse


def api_root(request):
    return JsonResponse({
        'name': 'ReliAIbleOps API',
        'version': '1.0.0',
        'endpoints': {
            'admin': '/admin/',
            'ingestion': '/api/ingestion/',
            'validation': '/api/validation/',
            'anomaly-detection': '/api/anomaly-detection/',
            'alerts': '/api/alerts/',
            'accounts': '/api/accounts/',
        }
    })


urlpatterns = [
    path('', api_root, name='api-root'),
    path('admin/', admin.site.urls),
    path('api/ingestion/', include('ingestion.urls')),
    path('api/validation/', include('validation.urls')),
    path('api/anomaly-detection/', include('anomaly_detection.urls')),
    path('api/alerts/', include('alerts.urls')),
    path('api/accounts/', include('accounts.urls')),
]
