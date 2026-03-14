"""
AI Anomaly Detection Pipeline
Implements Isolation Forest and Z-score anomaly detection.
"""
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from scipy import stats


FEATURE_COLS = [
    'cpu_usage', 'memory_usage', 'disk_io',
    'network_throughput', 'temperature', 'error_rate', 'response_time',
]


def queryset_to_dataframe(queryset):
    """Convert Django queryset to a pandas DataFrame."""
    values = queryset.values('id', *FEATURE_COLS)
    df = pd.DataFrame(list(values))
    return df


def run_isolation_forest(df, contamination=0.1):
    """
    Run Isolation Forest anomaly detection.
    Returns df with 'if_anomaly' (-1 = anomaly) and 'if_score' columns.
    """
    features = df[FEATURE_COLS].fillna(df[FEATURE_COLS].median())

    model = IsolationForest(
        n_estimators=100,
        contamination=contamination,
        random_state=42,
    )
    df = df.copy()
    df['if_anomaly'] = model.fit_predict(features)
    df['if_score'] = model.decision_function(features)
    return df


def run_zscore_detection(df, threshold=3.0):
    """
    Run Z-score based anomaly detection.
    A record is anomalous if any feature has |z-score| > threshold.
    """
    features = df[FEATURE_COLS].fillna(df[FEATURE_COLS].median())
    z_scores = np.abs(stats.zscore(features, nan_policy='omit'))

    df = df.copy()
    df['z_max'] = z_scores.max(axis=1)
    df['z_anomaly'] = (df['z_max'] > threshold).astype(int)

    z_cols = pd.DataFrame(z_scores, columns=[f'z_{c}' for c in FEATURE_COLS])
    for col in z_cols.columns:
        df[col] = z_cols[col].values
    return df


def determine_severity(if_score, z_max):
    """Assign severity based on combined scores."""
    if if_score < -0.3 or z_max > 5:
        return 'critical'
    elif if_score < -0.15 or z_max > 4:
        return 'high'
    elif if_score < -0.05 or z_max > 3:
        return 'medium'
    return 'low'


def get_affected_fields(row, z_threshold=2.5):
    """Return list of fields that contributed to the anomaly."""
    affected = []
    for col in FEATURE_COLS:
        z_col = f'z_{col}'
        if z_col in row and row[z_col] > z_threshold:
            affected.append(col)
    return affected


def generate_description(row, affected_fields):
    """Generate a human-readable anomaly description."""
    if not affected_fields:
        return "Statistical anomaly detected based on combined feature analysis."

    parts = []
    for field in affected_fields:
        val = row.get(field)
        if val is not None:
            parts.append(f"{field.replace('_', ' ').title()}: {val}")
    return f"Abnormal values detected – {'; '.join(parts)}"


def run_detection_pipeline(queryset, contamination=0.1, z_threshold=3.0):
    """
    Full anomaly detection pipeline:
    1. Convert queryset to DataFrame
    2. Run Isolation Forest
    3. Run Z-score detection
    4. Combine results
    Returns list of dicts with anomaly info.
    """
    df = queryset_to_dataframe(queryset)
    if df.empty or len(df) < 5:
        return []

    df = run_isolation_forest(df, contamination=contamination)
    df = run_zscore_detection(df, threshold=z_threshold)

    # Combine: anomaly if either algorithm flags it
    df['is_anomaly'] = ((df['if_anomaly'] == -1) | (df['z_anomaly'] == 1)).astype(int)

    anomalies = df[df['is_anomaly'] == 1]
    results = []

    for _, row in anomalies.iterrows():
        affected = get_affected_fields(row, z_threshold=2.5)
        severity = determine_severity(row.get('if_score', 0), row.get('z_max', 0))
        description = generate_description(row, affected)

        algo = 'combined'
        if row.get('if_anomaly') == -1 and row.get('z_anomaly') == 0:
            algo = 'isolation_forest'
        elif row.get('if_anomaly') != -1 and row.get('z_anomaly') == 1:
            algo = 'zscore'

        results.append({
            'data_record_id': int(row['id']),
            'algorithm': algo,
            'severity': severity,
            'anomaly_score': round(float(row.get('if_score', 0)), 4),
            'affected_fields': affected,
            'description': description,
        })

    return results
