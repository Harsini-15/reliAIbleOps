import requests
import json
import io

BASE_URL = 'http://localhost:8000/api'
print("Starting Comprehensive API Stress Test...")

def print_result(name, res):
    if res.status_code >= 500:
        print(f"❌ [FAIL - 500] {name}: {res.text[:100]}")
    elif res.status_code >= 400:
        print(f"✅ [PASS - Handled Error {res.status_code}] {name}: {res.text[:100]}")
    else:
        print(f"✅ [PASS - {res.status_code}] {name}")

# TEST 1: Simulate IoT Data with negative count
res = requests.post(f"{BASE_URL}/ingestion/simulate-iot/", json={"count": -10})
print_result("Simulate IoT (Negative count)", res)

# TEST 2: Simulate IoT Data with massive count
res = requests.post(f"{BASE_URL}/ingestion/simulate-iot/", json={"count": 10000})
print_result("Simulate IoT (10,000 count)", res)

# TEST 3: Upload Empty CSV
empty_csv = io.BytesIO(b"timestamp,metric_name,value,unit\n")
res = requests.post(
    f"{BASE_URL}/ingestion/upload-csv/", 
    files={'file': ('empty.csv', empty_csv, 'text/csv')},
    data={'source_name': 'empty_test'}
)
print_result("Upload Empty CSV", res)

# TEST 4: Upload Malformed CSV (Missing columns)
bad_csv = io.BytesIO(b"timestamp,value\n2023-01-01,100\n")
res = requests.post(
    f"{BASE_URL}/ingestion/upload-csv/", 
    files={'file': ('bad.csv', bad_csv, 'text/csv')},
    data={'source_name': 'bad_test'}
)
print_result("Upload Malformed CSV", res)

# TEST 5: Run Validation (Should handle potentially empty state)
res = requests.post(f"{BASE_URL}/validation/run/")
print_result("Run Validation", res)

# TEST 6: Run Anomaly Detection with invalid contamination
res = requests.post(f"{BASE_URL}/anomaly-detection/run/", json={"contamination": 1.5})
print_result("Anomaly Detection (Contamination > 0.5)", res)

res = requests.post(f"{BASE_URL}/anomaly-detection/run/", json={"contamination": -0.1})
print_result("Anomaly Detection (Contamination < 0)", res)

# TEST 7: Generate Alerts
res = requests.post(f"{BASE_URL}/alerts/generate/")
print_result("Generate Alerts", res)

# TEST 8: Resolve invalid alert ID
res = requests.post(f"{BASE_URL}/alerts/resolve/99999/")
print_result("Resolve Invalid Alert", res)

# TEST 9: Dashboard Overview
res = requests.get(f"{BASE_URL}/alerts/dashboard/")
print_result("Dashboard Overview", res)

print("Test complete.")
