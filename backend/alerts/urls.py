from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'logs', views.AlertLogViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('generate/', views.generate_alerts, name='generate-alerts'),
    path('resolve/<int:pk>/', views.resolve_alert, name='resolve-alert'),
    path('dashboard/', views.dashboard_overview, name='dashboard-overview'),
]
