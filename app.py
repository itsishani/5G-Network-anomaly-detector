from datetime import datetime, timedelta

import joblib  # To load our ML model if we use it
import pandas as pd
from flask import Flask, jsonify, render_template

app = Flask(__name__)

# Re-run or load data with detection results (using the rule-based for simplicity)
# For a real application, this would be a continuous data stream
def get_current_anomalies():
    # Simulate receiving "new" data or processing a batch
    data = pd.read_csv('network_performance_data.csv')
    data['timestamp'] = pd.to_datetime(data['timestamp'])

    # Apply rule-based detection from Phase 2
    data_with_detection = detect_anomalies_rule_based(data.copy()) # Make sure detect_anomalies_rule_based is defined or imported

    # Filter for recent anomalies for the "dashboard"
    # For a real-time system, this would be from a live stream
    recent_anomalies = data_with_detection[
        (data_with_detection['predicted_anomaly_rules'] == 1) &
        (data_with_detection['timestamp'] > datetime.now() - timedelta(minutes=120)) # Anomalies in last 2 hours
    ].sort_values(by='timestamp', ascending=False)

    # Prepare data for JSON response
    anomalies_list = recent_anomalies[[
        'timestamp', 'location_id', 'network_type',
        'signal_strength_dbm', 'latency_ms', 'throughput_mbps', 'packet_loss_percent',
        'anomaly_reason' # Add the reason
    ]].to_dict(orient='records')
    return anomalies_list

# Make sure detect_anomalies_rule_based is available (copy-paste or import from a utils.py)
def detect_anomalies_rule_based(df):
    df['predicted_anomaly_rules'] = 0
    df['anomaly_reason'] = ''

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

        if len(reasons) >= 2:
            df.loc[index, 'predicted_anomaly_rules'] = 1
            df.loc[index, 'anomaly_reason'] = ", ".join(reasons)
        elif len(reasons) == 1 and row['throughput_mbps'] < 10:
             df.loc[index, 'predicted_anomaly_rules'] = 1
             df.loc[index, 'anomaly_reason'] = "Critical Low Throughput"
    return df

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/anomalies')
def anomalies():
    anomalies_data = get_current_anomalies()
    return jsonify(anomalies_data)

if __name__ == '__main__':
    # Generate data if not already present for quick start
    try:
        pd.read_csv('network_performance_data.csv')
    except FileNotFoundError:
        print("Generating initial data for web app...")
        simulated_data = generate_network_data(num_records=5000, num_locations=20)
        simulated_data.to_csv('network_performance_data.csv', index=False)
        print("Data generated.")

    app.run(debug=True, port=5000)