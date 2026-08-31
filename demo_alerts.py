#!/usr/bin/env python3
"""
Generate multiple test alerts for demo
"""

import sys
import time
import json
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))

from database.database import Database

db = Database()

print("=" * 50)
print("Generating demo alerts...")
print("=" * 50)

alerts = [
    {
        'source_ip': '192.168.1.100',
        'dest_ip': '10.0.0.1',
        'alert_type': 'ABNORMAL_SYN_ACTIVITY',
        'severity': 'CRITICAL',
        'anomaly_score': 0.95,
        'reason': 'Abnormally high SYN packet count - port scan in progress'
    },
    {
        'source_ip': '192.168.1.101',
        'dest_ip': '10.0.0.5',
        'alert_type': 'HIGH_PORT_DIVERSITY',
        'severity': 'HIGH',
        'anomaly_score': 0.85,
        'reason': 'Unusually high number of destination ports contacted'
    },
    {
        'source_ip': '10.0.0.50',
        'dest_ip': '192.168.1.200',
        'alert_type': 'BURST_TRAFFIC',
        'severity': 'MEDIUM',
        'anomaly_score': 0.72,
        'reason': 'Traffic burst significantly above normal'
    },
    {
        'source_ip': '192.168.1.50',
        'dest_ip': '8.8.8.8',
        'alert_type': 'SCAN_PATTERN',
        'severity': 'HIGH',
        'anomaly_score': 0.82,
        'reason': 'Possible port scanning behavior detected'
    },
    {
        'source_ip': '10.0.0.10',
        'dest_ip': '192.168.1.50',
        'alert_type': 'ANOMALOUS_BEHAVIOR',
        'severity': 'CRITICAL',
        'anomaly_score': 0.92,
        'reason': 'Traffic behavior differs significantly from baseline'
    }
]

for i, alert_data in enumerate(alerts, 1):
    alert = {
        'timestamp': datetime.now().isoformat(),
        'source_ip': alert_data['source_ip'],
        'dest_ip': alert_data['dest_ip'],
        'alert_type': alert_data['alert_type'],
        'severity': alert_data['severity'],
        'anomaly_score': alert_data['anomaly_score'],
        'reason': alert_data['reason'],
        'features': json.dumps({'test': 'demo'})
    }
    
    alert_id = db.save_alert(alert)
    print(f"{i}. ✅ {alert_data['severity']}: {alert_data['reason'][:40]}...")
    time.sleep(0.5)

print("\n" + "=" * 50)
print(f"✅ Generated {len(alerts)} alerts")
print("📊 Refresh the dashboard to see them!")
print("=" * 50)

# Try to send to dashboard queue
try:
    from dashboard.routes import alert_queue
    recent = db.get_recent_alerts_for_dashboard(limit=5)
    for alert in recent:
        alert_queue.put(alert)
    print("✅ Alerts sent to dashboard")
except Exception as e:
    print(f"⚠️ Dashboard queue: {e}")
