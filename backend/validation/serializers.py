from rest_framework import serializers
from .models import ReliabilityScore


class ReliabilityScoreSerializer(serializers.ModelSerializer):
    data_record_id = serializers.IntegerField(source='data_record.id', read_only=True)
    source_name = serializers.CharField(source='data_record.source_name', read_only=True)

    class Meta:
        model = ReliabilityScore
        fields = [
            'id', 'data_record_id', 'source_name',
            'completeness_score', 'consistency_score',
            'uniqueness_score', 'overall_score',
            'issues_found', 'calculated_at',
        ]
