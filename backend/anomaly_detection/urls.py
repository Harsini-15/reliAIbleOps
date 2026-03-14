from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'records', views.AnomalyRecordViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('run/', views.run_anomaly_detection, name='run-anomaly-detection'),
    path('summary/', views.anomaly_summary, name='anomaly-summary'),
    path('acknowledge/<int:pk>/', views.acknowledge_anomaly, name='acknowledge-anomaly'),
]
