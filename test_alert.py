#!/usr/bin/env python3
"""
Simple test alert generator
"""

import sys
import json
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))

from database.database import Database

db = Database()

print("=" * 50)
print("Generating test alert...")
print("=" * 50)

test_alert = {
    'timestamp': datetime.now().isoformat(),
    'source_ip': '192.168.1.100',
    'dest_ip': '10.0.0.1',
    'alert_type': 'ABNORMAL_SYN_ACTIVITY',
    'severity': 'CRITICAL',
    'anomaly_score': 0.95,
    'reason': 'Abnormally high SYN packet count detected - possible port scan in progress',
    'features': json.dumps({
        'tcp_syn_count': 150,
        'unique_dest_ports': 45,
        'packets_per_second': 200
    })
}

alert_id = db.save_alert(test_alert)
print(f"✅ Test alert created with ID: {alert_id}")
print(f"   Source: {test_alert['source_ip']}")
print(f"   Severity: {test_alert['severity']}")
print(f"   Reason: {test_alert['reason']}")

# Try to send to dashboard queue
try:
    from dashboard.routes import alert_queue
    alert_queue.put(test_alert)
    print("✅ Alert sent to dashboard queue")
except Exception as e:
    print(f"⚠️ Could not send to dashboard queue: {e}")

print(f"\n📊 Total alerts in database: {db.get_total_alerts()}")
