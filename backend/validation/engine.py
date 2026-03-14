"""
Data Reliability Engine – validates and scores operational data.
"""
from ingestion.models import OperationalData
from validation.models import ReliabilityScore


NUMERIC_FIELDS = [
    'cpu_usage', 'memory_usage', 'disk_io',
    'network_throughput', 'temperature', 'error_rate', 'response_time',
]

# Expected reasonable ranges for consistency checks
VALID_RANGES = {
    'cpu_usage': (0, 100),
    'memory_usage': (0, 100),
    'disk_io': (0, 100),
    'network_throughput': (0, 100000),
    'temperature': (-40, 150),
    'error_rate': (0, 100),
    'response_time': (0, 60000),
}


def compute_completeness(record: OperationalData):
    """Compute % of non-null numeric fields."""
    filled = sum(1 for f in NUMERIC_FIELDS if getattr(record, f) is not None)
    return round((filled / len(NUMERIC_FIELDS)) * 100, 2)


def compute_consistency(record: OperationalData):
    """Check if values fall within expected ranges."""
    issues = []
    checked = 0
    valid = 0
    for field in NUMERIC_FIELDS:
        val = getattr(record, field)
        if val is None:
            continue
        checked += 1
        lo, hi = VALID_RANGES.get(field, (None, None))
        if lo is not None and hi is not None:
            if lo <= val <= hi:
                valid += 1
            else:
                issues.append(f"{field}={val} outside range [{lo}, {hi}]")
        else:
            valid += 1
    score = (valid / checked * 100) if checked > 0 else 100
    return round(score, 2), issues


def compute_uniqueness_batch(queryset):
    """Return uniqueness score across a batch (penalize duplicates)."""
    total = queryset.count()
    if total == 0:
        return 100.0

    unique = queryset.values(
        'timestamp', 'source_name', 'cpu_usage', 'memory_usage'
    ).distinct().count()

    return round((unique / total) * 100, 2)


def validate_record(record: OperationalData, uniqueness=100.0):
    """Validate a single record and create a ReliabilityScore."""
    completeness = compute_completeness(record)
    consistency, issues = compute_consistency(record)

    overall = round(
        completeness * 0.4 + consistency * 0.35 + uniqueness * 0.25,
        2,
    )

    score, created = ReliabilityScore.objects.update_or_create(
        data_record=record,
        defaults={
            'completeness_score': completeness,
            'consistency_score': consistency,
            'uniqueness_score': uniqueness,
            'overall_score': overall,
            'issues_found': issues,
        }
    )
    record.is_validated = True
    record.save(update_fields=['is_validated'])
    return score


def validate_all_unvalidated():
    """Validate all unvalidated records in bulk."""
    qs = OperationalData.objects.filter(is_validated=False)
    uniqueness = compute_uniqueness_batch(qs)
    results = []
    for record in qs.iterator():
        r = validate_record(record, uniqueness=uniqueness)
        results.append(r)
    return results
