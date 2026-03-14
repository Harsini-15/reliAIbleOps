from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'data', views.OperationalDataViewSet)
router.register(r'metrics', views.SystemMetricViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('upload-csv/', views.upload_csv, name='upload-csv'),
    path('simulate-iot/', views.simulate_iot_data, name='simulate-iot'),
    path('summary/', views.data_summary, name='data-summary'),
]
