from django.db import models
from ingestion.models import OperationalData


class ReliabilityScore(models.Model):
    """Data reliability score for a batch or individual data point."""
    data_record = models.OneToOneField(
        OperationalData,
        on_delete=models.CASCADE,
        related_name='reliability_score',
        null=True,
        blank=True,
    )
    batch_id = models.CharField(max_length=100, blank=True, default='')
    completeness_score = models.FloatField(help_text="% of non-null fields (0-100)")
    consistency_score = models.FloatField(help_text="Score based on value range validation (0-100)")
    uniqueness_score = models.FloatField(help_text="Score penalizing duplicates (0-100)")
    overall_score = models.FloatField(help_text="Weighted average reliability score (0-100)")
    issues_found = models.JSONField(default=list, blank=True)
    calculated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'reliability_scores'
        ordering = ['-calculated_at']

    def __str__(self):
        return f"Reliability: {self.overall_score:.1f}% (record {self.data_record_id})"
