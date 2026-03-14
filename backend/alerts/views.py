from rest_framework import viewsets, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.utils import timezone
from django.db.models import Count, Avg

from .models import AlertLog
from .serializers import AlertLogSerializer
from anomaly_detection.models import AnomalyRecord
from validation.models import ReliabilityScore
from ingestion.models import OperationalData


class AlertLogViewSet(viewsets.ModelViewSet):
    queryset = AlertLog.objects.all()
    serializer_class = AlertLogSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        level = self.request.query_params.get('level')
        resolved = self.request.query_params.get('resolved')
        if level:
            qs = qs.filter(level=level)
        if resolved is not None:
            qs = qs.filter(is_resolved=resolved.lower() == 'true')
        return qs


@api_view(['POST'])
def generate_alerts(request):
    """Generate alerts from unacknowledged anomalies."""
    anomalies = AnomalyRecord.objects.filter(is_acknowledged=False)
    created = 0

    for anomaly in anomalies:
        level_map = {
            'critical': 'critical',
            'high': 'error',
            'medium': 'warning',
            'low': 'info',
        }
        level = level_map.get(anomaly.severity, 'warning')

        _, was_created = AlertLog.objects.get_or_create(
            related_anomaly_id=anomaly.id,
            defaults={
                'title': f'Anomaly Detected: {anomaly.description[:100]}',
                'message': anomaly.description,
                'level': level,
                'source': f'anomaly_detection/{anomaly.algorithm}',
                'metadata': {
                    'anomaly_score': anomaly.anomaly_score,
                    'affected_fields': anomaly.affected_fields,
                    'data_record_id': anomaly.data_record_id,
                },
            }
        )
        if was_created:
            created += 1

    return Response({
        'message': f'Generated {created} new alerts.',
        'new_alerts': created,
    })


@api_view(['POST'])
def resolve_alert(request, pk):
    """Resolve an alert."""
    try:
        alert = AlertLog.objects.get(pk=pk)
        alert.is_resolved = True
        alert.resolved_at = timezone.now()
        alert.save()
        
        # Also acknowledge the related anomaly if it exists
        if alert.related_anomaly_id:
            try:
                anomaly = AnomalyRecord.objects.get(pk=alert.related_anomaly_id)
                anomaly.is_acknowledged = True
                anomaly.save()
            except AnomalyRecord.DoesNotExist:
                pass
            
        return Response({'message': 'Alert resolved and related anomaly acknowledged.'})
    except AlertLog.DoesNotExist:
        return Response({'error': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
def dashboard_overview(request):
    """
    Decision Intelligence Module – comprehensive dashboard data.
    Generates insights, predictions, and recommendations.
    """
    # System overview
    total_data = OperationalData.objects.count()
    validated_data = OperationalData.objects.filter(is_validated=True).count()
    total_anomalies = AnomalyRecord.objects.count()
    unresolved_alerts = AlertLog.objects.filter(is_resolved=False).count()

    # Reliability overview
    reliability_avg = ReliabilityScore.objects.aggregate(
        avg=Avg('overall_score')
    )['avg'] or 0

    # Anomaly severity breakdown
    severity_breakdown = list(
        AnomalyRecord.objects.values('severity')
        .annotate(count=Count('id'))
        .order_by('severity')
    )

    # Recent operational data (last 100 records)
    recent_data = list(
        OperationalData.objects.order_by('-timestamp')[:100]
        .values('timestamp', 'cpu_usage', 'memory_usage', 'temperature', 'error_rate', 'response_time')
    )

    # Reliability trend (last 50 scores)
    reliability_trend = list(
        ReliabilityScore.objects.order_by('-calculated_at')[:50]
        .values('overall_score', 'calculated_at')
    )

    # Recent alerts
    recent_alerts = list(
        AlertLog.objects.filter(is_resolved=False)
        .order_by('-created_at')[:10]
        .values('id', 'title', 'level', 'created_at', 'source')
    )

    # Decision intelligence: recommendations
    recommendations = []
    if reliability_avg < 70:
        recommendations.append({
            'type': 'warning',
            'title': 'Low Data Reliability',
            'message': f'Average reliability score is {reliability_avg:.1f}%. Data quality needs improvement.',
        })
    if total_anomalies > 0:
        critical = AnomalyRecord.objects.filter(severity='critical', is_acknowledged=False).count()
        if critical > 0:
            recommendations.append({
                'type': 'critical',
                'title': 'Critical Anomalies Detected',
                'message': f'{critical} critical anomalies require immediate attention.',
            })
    if unresolved_alerts > 5:
        recommendations.append({
            'type': 'info',
            'title': 'Pending Alerts',
            'message': f'{unresolved_alerts} alerts pending review. Consider resolving stale alerts.',
        })
    if total_data > 0 and validated_data / total_data < 0.5:
        recommendations.append({
            'type': 'warning',
            'title': 'Low Validation Coverage',
            'message': 'Less than 50% of data has been validated. Run the validation pipeline.',
        })

    # System health score (0-100)
    health_score = 100
    if total_data > 0:
        anomaly_rate = (total_anomalies / total_data) * 100 if total_data else 0
        health_score = max(0, 100 - anomaly_rate * 5 - (100 - reliability_avg) * 0.3)

    return Response({
        'system_health_score': round(health_score, 1),
        'total_data_points': total_data,
        'validated_data_points': validated_data,
        'total_anomalies': total_anomalies,
        'unresolved_alerts': unresolved_alerts,
        'avg_reliability_score': round(reliability_avg, 1),
        'severity_breakdown': severity_breakdown,
        'recent_data': recent_data,
        'reliability_trend': reliability_trend,
        'recent_alerts': recent_alerts,
        'recommendations': recommendations,
    })
