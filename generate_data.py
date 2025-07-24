import random
from datetime import datetime, timedelta

import numpy as np
import pandas as pd


def generate_network_data(num_records=1000, num_locations=10):
    """Generates synthetic network performance data with optional anomalies."""
    data = []
    locations = [f"Mambakkam_Loc_{i+1}" for i in range(num_locations)]
    start_time = datetime.now() - timedelta(days=7) # Data from past week

    for _ in range(num_records):
        timestamp = start_time + timedelta(minutes=random.randint(0, 7*24*60))
        location_id = random.choice(locations)
        device_count = random.randint(10, 100)
        network_type = random.choice(['5G_FWA', '5G_Mobile', 'LTE'])

        # Baseline normal values
        signal_strength = random.uniform(-80, -60) # dBm, higher is better
        latency = random.uniform(10, 50) # ms
        throughput = random.uniform(50, 500) # Mbps
        packet_loss = random.uniform(0.1, 1.0) # percent

        anomaly_flag = 0

        # Introduce anomalies for a small percentage of data
        if random.random() < 0.05: # 5% chance of anomaly
            anomaly_type = random.choice(['signal_drop', 'latency_spike', 'throughput_dip', 'packet_loss_surge'])
            anomaly_flag = 1

            if anomaly_type == 'signal_drop':
                signal_strength = random.uniform(-100, -85) # Worse signal
            elif anomaly_type == 'latency_spike':
                latency = random.uniform(100, 500) # High latency
            elif anomaly_type == 'throughput_dip':
                throughput = random.uniform(5, 40) # Low throughput
            elif anomaly_type == 'packet_loss_surge':
                packet_loss = random.uniform(5.0, 20.0) # High packet loss

        data.append({
            'timestamp': timestamp,
            'location_id': location_id,
            'device_count': device_count,
            'signal_strength_dbm': signal_strength,
            'latency_ms': latency,
            'throughput_mbps': throughput,
            'packet_loss_percent': packet_loss,
            'network_type': network_type,
            'anomaly_flag': anomaly_flag # For practice, we know the truth
        })

    df = pd.DataFrame(data)
    return df

# Generate some data
simulated_data = generate_network_data(num_records=5000, num_locations=20)
print("Simulated Data Head:")
print(simulated_data.head())
print("\nAnomaly distribution:")
print(simulated_data['anomaly_flag'].value_counts())
print("\nData types:")
print(simulated_data.info())

# Save to CSV for easy loading in the next phase
simulated_data.to_csv('network_performance_data.csv', index=False)