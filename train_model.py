import joblib  # For saving/loading model
import pandas as pd
from sklearn.ensemble import IsolationForest

# Load the simulated data
try:
    data = pd.read_csv('network_performance_data.csv')
    data['timestamp'] = pd.to_datetime(data['timestamp'])
except FileNotFoundError:
    print("network_performance_data.csv not found. Please run the data generation script first.")
    # Exit or regenerate data if needed for testing
    data = generate_network_data(num_records=5000, num_locations=20)
    data.to_csv('network_performance_data.csv', index=False)
    data['timestamp'] = pd.to_datetime(data['timestamp'])

print("\nData loaded for AI model:")
print(data.head())

# --- Option 1: Rule-Based Anomaly Detection (Quicker for 6 hours) ---
def detect_anomalies_rule_based(df):
    df['predicted_anomaly_rules'] = 0
    df['anomaly_reason'] = ''

    # Define thresholds
    BAD_SIGNAL_THRESHOLD = -85 # dBm
    HIGH_LATENCY_THRESHOLD = 100 # ms
    LOW_THROUGHPUT_THRESHOLD = 40 # Mbps
    HIGH_PACKET_LOSS_THRESHOLD = 3.0 # percent

    for index, row in df.iterrows():
        reasons = []
        if row['signal_strength_dbm'] < BAD_SIGNAL_THRESHOLD:
            reasons.append('Low Signal')
        if row['latency_ms'] > HIGH_LATENCY_THRESHOLD:
            reasons.append('High Latency')
        if row['throughput_mbps'] < LOW_THROUGHPUT_THRESHOLD:
            reasons.append('Low Throughput')
        if row['packet_loss_percent'] > HIGH_PACKET_LOSS_THRESHOLD:
            reasons.append('High Packet Loss')

        if len(reasons) >= 2: # At least two conditions indicate a significant anomaly
            df.loc[index, 'predicted_anomaly_rules'] = 1
            df.loc[index, 'anomaly_reason'] = ", ".join(reasons)
        elif len(reasons) == 1 and row['throughput_mbps'] < 10: # Special case for extremely low throughput
             df.loc[index, 'predicted_anomaly_rules'] = 1
             df.loc[index, 'anomaly_reason'] = "Critical Low Throughput"

    return df

data_with_rule_anomalies = detect_anomalies_rule_based(data.copy())
print("\nRule-Based Anomaly Detection Results (first 10 anomalies):")
print(data_with_rule_anomalies[data_with_rule_anomalies['predicted_anomaly_rules'] == 1].head(10))
print(f"Total rule-based anomalies detected: {data_with_rule_anomalies['predicted_anomaly_rules'].sum()}")

# --- Option 2: Basic ML-Based Anomaly Detection (More "AI", but might take longer to tune) ---
# For IsolationForest, it works best on continuous numerical data.
# It assigns an anomaly score; typically, -1 indicates an anomaly, 1 indicates normal.

features = ['signal_strength_dbm', 'latency_ms', 'throughput_mbps', 'packet_loss_percent', 'device_count']

# Ensure all features are numeric, handle potential NaNs if any (not expected with synthetic data)
for col in features:
    data[col] = pd.to_numeric(data[col], errors='coerce').fillna(data[col].mean())


# Train Isolation Forest model (unsupervised learning)
# `contamination` parameter is important: it's the proportion of outliers in the dataset (we know it's ~0.05 from generation)
model = IsolationForest(contamination=0.05, random_state=42) # Adjust contamination based on expected anomaly rate
model.fit(data[features])

# Predict anomalies (-1 for anomaly, 1 for normal)
data['anomaly_score'] = model.decision_function(data[features])
data['predicted_anomaly_ml'] = model.predict(data[features])

# Convert -1 to 1 for anomaly, 1 to 0 for normal to match our flag
data['predicted_anomaly_ml'] = data['predicted_anomaly_ml'].apply(lambda x: 1 if x == -1 else 0)

print("\nML-Based (Isolation Forest) Anomaly Detection Results (first 10 anomalies):")
print(data[data['predicted_anomaly_ml'] == 1].head(10))
print(f"Total ML-based anomalies detected: {data['predicted_anomaly_ml'].sum()}")

# For techathon, focus on one approach. The rule-based is simpler to explain clearly.
# If using ML, discuss how it learns patterns rather than relying on fixed thresholds.

# Save the trained model for demonstration (optional but good practice)
joblib.dump(model, 'isolation_forest_model.pkl')