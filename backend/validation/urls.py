from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'scores', views.ReliabilityScoreViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('run/', views.run_validation, name='run-validation'),
    path('summary/', views.reliability_summary, name='reliability-summary'),
]
