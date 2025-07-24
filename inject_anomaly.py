import random
from datetime import datetime, timedelta

import pandas as pd


def inject_new_anomaly():
    try:
        df = pd.read_csv('network_performance_data.csv')
        df['timestamp'] = pd.to_datetime(df['timestamp'])
    except FileNotFoundError:
        print("Data file not found. Please generate initial data first.")
        return

    new_timestamp = datetime.now() + timedelta(minutes=random.randint(-5, 5)) # Make it very recent
    location_id = random.choice(df['location_id'].unique())

    # Create a clear anomaly
    new_anomaly_row = {
        'timestamp': new_timestamp,
        'location_id': location_id,
        'device_count': random.randint(50, 150),
        'signal_strength_dbm': random.uniform(-100, -90), # Very bad signal
        'latency_ms': random.uniform(200, 500),         # Very high latency
        'throughput_mbps': random.uniform(1, 10),       # Very low throughput
        'packet_loss_percent': random.uniform(10.0, 30.0), # High packet loss
        'network_type': random.choice(['5G_FWA', '5G_Mobile']),
        'anomaly_flag': 1 # We know it's an anomaly
    }
    new_anomaly_df = pd.DataFrame([new_anomaly_row])

    # Append the new anomaly to the existing CSV
    # Use mode='a' for append, header=False to not write header again
    new_anomaly_df.to_csv('network_performance_data.csv', mode='a', header=False, index=False)
    print(f"Injected new anomaly for {location_id} at {new_timestamp}")

if __name__ == '__main__':
    inject_new_anomaly()