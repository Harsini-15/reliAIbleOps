from rest_framework import serializers
from .models import AnomalyRecord


class AnomalyRecordSerializer(serializers.ModelSerializer):
    source_name = serializers.CharField(source='data_record.source_name', read_only=True)
    timestamp = serializers.DateTimeField(source='data_record.timestamp', read_only=True)

    class Meta:
        model = AnomalyRecord
        fields = [
            'id', 'data_record_id', 'source_name', 'timestamp',
            'algorithm', 'severity', 'anomaly_score',
            'affected_fields', 'description',
            'is_acknowledged', 'detected_at',
        ]
