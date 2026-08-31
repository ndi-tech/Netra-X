#!/usr/bin/env python3
"""
Generate a test alert for Netra-X
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from database.database import Database
from alerts.alert_manager import AlertManager
from queue import Queue

# Create test alert
db = Database()
alert_queue = Queue()
alert_manager = AlertManager(db, alert_queue)

print("Generating test alert...")

# Test alert data
test_alert = {
    'timestamp': '2026-08-31T02:30:00',
    'source_ip': '192.168.1.100',
    'dest_ip': '10.0.0.1',
    'alert_type': 'ABNORMAL_SYN_ACTIVITY',
    'severity': 'CRITICAL',
    'anomaly_score': 0.95,
    'reason': 'Abnormally high SYN packet count detected - possible port scan in progress',
    'features': {
        'tcp_syn_count': 150,
        'unique_dest_ports': 45,
        'packets_per_second': 200
    }
}

# Save to database
alert_id = db.save_alert(test_alert)
test_alert['id'] = alert_id

# Send to queue for dashboard
alert_queue.put(test_alert)

print(f"Test alert created with ID: {alert_id}")
print(f"Source: {test_alert['source_ip']}")
print(f"Severity: {test_alert['severity']}")
print(f"Reason: {test_alert['reason']}")
