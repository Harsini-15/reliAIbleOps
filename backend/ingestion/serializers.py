from rest_framework import serializers
from .models import OperationalData, SystemMetric


class OperationalDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = OperationalData
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'is_validated']


class OperationalDataCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = OperationalData
        fields = [
            'source_type', 'source_name', 'timestamp',
            'cpu_usage', 'memory_usage', 'disk_io',
            'network_throughput', 'temperature', 'error_rate',
            'response_time', 'status_code', 'raw_payload',
        ]


class CSVUploadSerializer(serializers.Serializer):
    file = serializers.FileField()
    source_name = serializers.CharField(max_length=200, default='csv_upload')


class SystemMetricSerializer(serializers.ModelSerializer):
    class Meta:
        model = SystemMetric
        fields = '__all__'
        read_only_fields = ['id', 'created_at']
