import csv
import io
from datetime import datetime

from rest_framework import viewsets, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.utils import timezone

from .models import OperationalData, SystemMetric
from .serializers import (
    OperationalDataSerializer,
    OperationalDataCreateSerializer,
    CSVUploadSerializer,
    SystemMetricSerializer,
)


class OperationalDataViewSet(viewsets.ModelViewSet):
    queryset = OperationalData.objects.all()
    serializer_class = OperationalDataSerializer

    def get_serializer_class(self):
        if self.action == 'create':
            return OperationalDataCreateSerializer
        return OperationalDataSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        source_type = self.request.query_params.get('source_type')
        validated = self.request.query_params.get('validated')
        start = self.request.query_params.get('start')
        end = self.request.query_params.get('end')

        if source_type:
            qs = qs.filter(source_type=source_type)
        if validated is not None:
            qs = qs.filter(is_validated=validated.lower() == 'true')
        if start:
            qs = qs.filter(timestamp__gte=start)
        if end:
            qs = qs.filter(timestamp__lte=end)
        return qs


class SystemMetricViewSet(viewsets.ModelViewSet):
    queryset = SystemMetric.objects.all()
    serializer_class = SystemMetricSerializer


@api_view(['POST'])
def upload_csv(request):
    """Upload a CSV file containing operational data."""
    serializer = CSVUploadSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    csv_file = serializer.validated_data['file']
    source_name = serializer.validated_data.get('source_name', 'csv_upload')

    if not csv_file.name.endswith('.csv'):
        return Response(
            {'error': 'File must be a CSV'},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        decoded = csv_file.read().decode('utf-8')
        reader = csv.DictReader(io.StringIO(decoded))
        records = []

        field_map = {
            'cpu_usage': float,
            'memory_usage': float,
            'disk_io': float,
            'network_throughput': float,
            'temperature': float,
            'error_rate': float,
            'response_time': float,
            'status_code': int,
        }

        for row in reader:
            ts_str = row.get('timestamp', '')
            try:
                ts = datetime.fromisoformat(ts_str)
            except (ValueError, TypeError):
                ts = timezone.now()

            record = OperationalData(
                source_type='csv',
                source_name=source_name,
                timestamp=ts,
            )
            for field, cast in field_map.items():
                val = row.get(field, '')
                if val not in ('', None, 'null', 'NaN', 'nan'):
                    try:
                        setattr(record, field, cast(val))
                    except (ValueError, TypeError):
                        pass
            records.append(record)

        created = OperationalData.objects.bulk_create(records)
        return Response(
            {'message': f'Successfully ingested {len(created)} records.', 'count': len(created)},
            status=status.HTTP_201_CREATED
        )

    except Exception as e:
        return Response(
            {'error': f'Failed to process CSV: {str(e)}'},
            status=status.HTTP_400_BAD_REQUEST
        )


@api_view(['POST'])
def simulate_iot_data(request):
    """Generate simulated IoT sensor data for demonstration."""
    import random

    try:
        count = int(request.data.get('count', 50))
        if count <= 0:
            return Response({'error': 'Count must be greater than 0.'}, status=status.HTTP_400_BAD_REQUEST)
        count = min(count, 500)  # Cap at 500
    except (ValueError, TypeError):
        return Response({'error': 'Invalid count parameter.'}, status=status.HTTP_400_BAD_REQUEST)
    records = []

    for i in range(count):
        ts = timezone.now() - timezone.timedelta(minutes=count - i)
        record = OperationalData(
            source_type='iot',
            source_name=f"sensor_{random.choice(['A', 'B', 'C', 'D'])}",
            timestamp=ts,
            cpu_usage=round(random.uniform(10, 95), 2),
            memory_usage=round(random.uniform(20, 90), 2),
            disk_io=round(random.uniform(5, 80), 2),
            network_throughput=round(random.uniform(100, 10000), 2),
            temperature=round(random.uniform(30, 85), 2),
            error_rate=round(random.uniform(0, 15), 4),
            response_time=round(random.uniform(1, 500), 2),
            status_code=random.choice([200, 200, 200, 200, 500, 503, 408]),
        )
        # Inject some anomalies (about 10%)
        if random.random() < 0.1:
            record.cpu_usage = round(random.uniform(95, 100), 2)
            record.temperature = round(random.uniform(85, 120), 2)
            record.error_rate = round(random.uniform(15, 50), 4)
            record.response_time = round(random.uniform(800, 5000), 2)

        records.append(record)

    created = OperationalData.objects.bulk_create(records)
    return Response(
        {'message': f'Simulated {len(created)} IoT data points.', 'count': len(created)},
        status=status.HTTP_201_CREATED
    )


@api_view(['GET'])
def data_summary(request):
    """Return summary statistics about ingested data."""
    from django.db.models import Count, Avg, Max, Min

    total = OperationalData.objects.count()
    validated = OperationalData.objects.filter(is_validated=True).count()
    by_source = list(
        OperationalData.objects.values('source_type')
        .annotate(count=Count('id'))
        .order_by('-count')
    )
    stats = OperationalData.objects.aggregate(
        avg_cpu=Avg('cpu_usage'),
        max_cpu=Max('cpu_usage'),
        avg_memory=Avg('memory_usage'),
        avg_temp=Avg('temperature'),
        max_temp=Max('temperature'),
        avg_error_rate=Avg('error_rate'),
        avg_response_time=Avg('response_time'),
    )

    return Response({
        'total_records': total,
        'validated_records': validated,
        'unvalidated_records': total - validated,
        'by_source': by_source,
        'statistics': stats,
    })
