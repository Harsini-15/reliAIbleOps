from rest_framework import serializers
from .models import AlertLog


class AlertLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = AlertLog
        fields = '__all__'
        read_only_fields = ['id', 'created_at']
