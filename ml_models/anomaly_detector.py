"""
Standalone ML models module for anomaly detection.
Can be used independently of Django for model training and evaluation.
"""
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from scipy import stats
import json
import os


FEATURE_COLS = [
    'cpu_usage', 'memory_usage', 'disk_io',
    'network_throughput', 'temperature', 'error_rate', 'response_time',
]


class AnomalyDetector:
    """
    Combined anomaly detection using Isolation Forest and Z-score methods.
    """

    def __init__(self, contamination=0.1, z_threshold=3.0):
        self.contamination = contamination
        self.z_threshold = z_threshold
        self.model = IsolationForest(
            n_estimators=100,
            contamination=contamination,
            random_state=42,
        )
        self.scaler = StandardScaler()
        self.is_fitted = False

    def fit(self, df: pd.DataFrame):
        """Fit the model on training data."""
        features = df[FEATURE_COLS].fillna(df[FEATURE_COLS].median())
        self.scaler.fit(features)
        scaled = self.scaler.transform(features)
        self.model.fit(scaled)
        self.is_fitted = True
        return self

    def predict(self, df: pd.DataFrame):
        """Predict anomalies on new data."""
        if not self.is_fitted:
            raise ValueError("Model not fitted. Call fit() first.")

        features = df[FEATURE_COLS].fillna(df[FEATURE_COLS].median())
        scaled = self.scaler.transform(features)

        # Isolation Forest
        if_predictions = self.model.predict(scaled)
        if_scores = self.model.decision_function(scaled)

        # Z-score
        z_scores = np.abs(stats.zscore(features, nan_policy='omit'))
        z_max = z_scores.max(axis=1)
        z_anomalies = (z_max > self.z_threshold).astype(int)

        # Combine: anomaly if either flags it
        combined = ((if_predictions == -1) | (z_anomalies == 1)).astype(int)

        results = df.copy()
        results['is_anomaly'] = combined
        results['if_score'] = if_scores
        results['z_max'] = z_max

        return results

    def get_stats(self, results: pd.DataFrame):
        """Get summary statistics from prediction results."""
        total = len(results)
        anomalies = results['is_anomaly'].sum()
        return {
            'total_records': total,
            'anomalies_detected': int(anomalies),
            'anomaly_rate': round(anomalies / total * 100, 2) if total else 0,
            'avg_if_score': round(results['if_score'].mean(), 4),
            'avg_z_max': round(results['z_max'].mean(), 4),
        }


def generate_sample_data(n=200, anomaly_rate=0.1):
    """Generate synthetic operational data for testing."""
    np.random.seed(42)
    n_normal = int(n * (1 - anomaly_rate))
    n_anomaly = n - n_normal

    normal = pd.DataFrame({
        'cpu_usage': np.random.normal(45, 15, n_normal).clip(5, 90),
        'memory_usage': np.random.normal(55, 12, n_normal).clip(10, 85),
        'disk_io': np.random.normal(30, 10, n_normal).clip(2, 70),
        'network_throughput': np.random.normal(5000, 2000, n_normal).clip(100, 9500),
        'temperature': np.random.normal(55, 8, n_normal).clip(30, 75),
        'error_rate': np.random.exponential(2, n_normal).clip(0, 10),
        'response_time': np.random.normal(100, 30, n_normal).clip(5, 250),
    })

    anomalous = pd.DataFrame({
        'cpu_usage': np.random.normal(92, 5, n_anomaly).clip(85, 100),
        'memory_usage': np.random.normal(90, 5, n_anomaly).clip(80, 100),
        'disk_io': np.random.normal(85, 8, n_anomaly).clip(70, 100),
        'network_throughput': np.random.normal(500, 300, n_anomaly).clip(0, 1500),
        'temperature': np.random.normal(95, 10, n_anomaly).clip(80, 130),
        'error_rate': np.random.normal(30, 10, n_anomaly).clip(10, 60),
        'response_time': np.random.normal(2000, 800, n_anomaly).clip(500, 5000),
    })

    df = pd.concat([normal, anomalous], ignore_index=True)
    df = df.sample(frac=1, random_state=42).reset_index(drop=True)
    df = df.round(2)

    # Add timestamps
    timestamps = pd.date_range(end=pd.Timestamp.now(), periods=n, freq='5min')
    df.insert(0, 'timestamp', timestamps)
    df.insert(1, 'source_name', [f'sensor_{chr(65 + i % 4)}' for i in range(n)])
    df.insert(2, 'source_type', 'iot')

    return df


if __name__ == '__main__':
    print("=== ReliAIbleOps ML Anomaly Detection Demo ===\n")

    df = generate_sample_data(200, anomaly_rate=0.1)
    print(f"Generated {len(df)} data points.\n")

    detector = AnomalyDetector(contamination=0.1, z_threshold=3.0)
    detector.fit(df)
    results = detector.predict(df)
    stats_info = detector.get_stats(results)

    print("Detection Results:")
    for k, v in stats_info.items():
        print(f"  {k}: {v}")

    # Save to CSV
    os.makedirs('../datasets', exist_ok=True)
    df.to_csv('../datasets/sample_operational_data.csv', index=False)
    print("\nSample data saved to datasets/sample_operational_data.csv")
