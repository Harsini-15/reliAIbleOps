from rest_framework import viewsets, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db.models import Avg

from .models import ReliabilityScore
from .serializers import ReliabilityScoreSerializer
from .engine import validate_all_unvalidated


class ReliabilityScoreViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ReliabilityScore.objects.select_related('data_record').all()
    serializer_class = ReliabilityScoreSerializer


@api_view(['POST'])
def run_validation(request):
    """Trigger validation on all unvalidated records."""
    results = validate_all_unvalidated()
    return Response({
        'message': f'Validated {len(results)} records.',
        'count': len(results),
        'avg_score': round(
            sum(r.overall_score for r in results) / len(results), 2
        ) if results else 0,
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
def reliability_summary(request):
    """Return aggregate reliability stats."""
    agg = ReliabilityScore.objects.aggregate(
        avg_overall=Avg('overall_score'),
        avg_completeness=Avg('completeness_score'),
        avg_consistency=Avg('consistency_score'),
        avg_uniqueness=Avg('uniqueness_score'),
    )
    total = ReliabilityScore.objects.count()
    high = ReliabilityScore.objects.filter(overall_score__gte=80).count()
    medium = ReliabilityScore.objects.filter(overall_score__gte=50, overall_score__lt=80).count()
    low = ReliabilityScore.objects.filter(overall_score__lt=50).count()

    return Response({
        'total_scored': total,
        'averages': agg,
        'distribution': {
            'high': high,
            'medium': medium,
            'low': low,
        }
    })
