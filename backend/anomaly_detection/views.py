from rest_framework import viewsets, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db.models import Count

from ingestion.models import OperationalData
from .models import AnomalyRecord
from .serializers import AnomalyRecordSerializer
from .ml_pipeline import run_detection_pipeline


class AnomalyRecordViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AnomalyRecord.objects.select_related('data_record').all()
    serializer_class = AnomalyRecordSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        severity = self.request.query_params.get('severity')
        algorithm = self.request.query_params.get('algorithm')
        ack = self.request.query_params.get('acknowledged')
        if severity:
            qs = qs.filter(severity=severity)
        if algorithm:
            qs = qs.filter(algorithm=algorithm)
        if ack is not None:
            qs = qs.filter(is_acknowledged=ack.lower() == 'true')
        return qs


@api_view(['POST'])
def run_anomaly_detection(request):
    """Trigger anomaly detection on validated operational data."""
    qs = OperationalData.objects.filter(is_validated=True)

    source_type = request.data.get('source_type')
    if source_type:
        qs = qs.filter(source_type=source_type)

    try:
        contamination = float(request.data.get('contamination', 0.1))
        if not (0 < contamination <= 0.5):
            return Response(
                {'error': 'Contamination must be greater than 0 and less than or equal to 0.5'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
    except (ValueError, TypeError):
        return Response({'error': 'Invalid contamination parameter.'}, status=status.HTTP_400_BAD_REQUEST)

    results = run_detection_pipeline(qs, contamination=contamination)

    created_count = 0
    for r in results:
        _, created = AnomalyRecord.objects.update_or_create(
            data_record_id=r['data_record_id'],
            algorithm=r['algorithm'],
            defaults={
                'severity': r['severity'],
                'anomaly_score': r['anomaly_score'],
                'affected_fields': r['affected_fields'],
                'description': r['description'],
            }
        )
        if created:
            created_count += 1

    return Response({
        'message': f'Detection complete. {len(results)} anomalies found, {created_count} new records created.',
        'total_anomalies': len(results),
        'new_records': created_count,
    })


@api_view(['GET'])
def anomaly_summary(request):
    """Summary statistics for anomaly detection results."""
    total = AnomalyRecord.objects.count()
    by_severity = list(
        AnomalyRecord.objects.values('severity')
        .annotate(count=Count('id'))
        .order_by('-count')
    )
    by_algorithm = list(
        AnomalyRecord.objects.values('algorithm')
        .annotate(count=Count('id'))
        .order_by('-count')
    )
    unacknowledged = AnomalyRecord.objects.filter(is_acknowledged=False).count()

    return Response({
        'total_anomalies': total,
        'unacknowledged': unacknowledged,
        'by_severity': by_severity,
        'by_algorithm': by_algorithm,
    })


@api_view(['POST'])
def acknowledge_anomaly(request, pk):
    """Acknowledge an anomaly."""
    try:
        anomaly = AnomalyRecord.objects.get(pk=pk)
        anomaly.is_acknowledged = True
        anomaly.save()
        return Response({'message': 'Anomaly acknowledged.'})
    except AnomalyRecord.DoesNotExist:
        return Response({'error': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)
