from django.db import models


class OperationalData(models.Model):
    """Raw operational data from engineering systems."""
    SOURCE_CHOICES = [
        ('csv', 'CSV Upload'),
        ('iot', 'IoT Sensor'),
        ('server', 'Server Log'),
        ('network', 'Network Monitor'),
    ]

    source_type = models.CharField(max_length=20, choices=SOURCE_CHOICES)
    source_name = models.CharField(max_length=200)
    timestamp = models.DateTimeField()
    cpu_usage = models.FloatField(null=True, blank=True)
    memory_usage = models.FloatField(null=True, blank=True)
    disk_io = models.FloatField(null=True, blank=True)
    network_throughput = models.FloatField(null=True, blank=True)
    temperature = models.FloatField(null=True, blank=True)
    error_rate = models.FloatField(null=True, blank=True)
    response_time = models.FloatField(null=True, blank=True)
    status_code = models.IntegerField(null=True, blank=True)
    raw_payload = models.JSONField(default=dict, blank=True)
    is_validated = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'operational_data'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['timestamp']),
            models.Index(fields=['source_type']),
            models.Index(fields=['is_validated']),
        ]

    def __str__(self):
        return f"{self.source_name} @ {self.timestamp}"


class SystemMetric(models.Model):
    """Aggregated system metrics computed periodically."""
    metric_name = models.CharField(max_length=100)
    metric_value = models.FloatField()
    unit = models.CharField(max_length=30, default='')
    source = models.CharField(max_length=200, default='system')
    timestamp = models.DateTimeField()
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'system_metrics'
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.metric_name}: {self.metric_value} {self.unit}"
