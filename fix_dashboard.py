#!/usr/bin/env python3
"""
Fix dashboard to load existing alerts
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from database.database import Database
from dashboard.routes import alert_queue

print("=" * 50)
print("Pushing alerts to dashboard...")
print("=" * 50)

# Get alerts from database
db = Database()
alerts = db.get_recent_alerts_for_dashboard(limit=50)

print(f"Found {len(alerts)} alerts in database")

# Push to queue
count = 0
for alert in alerts:
    alert_queue.put(alert)
    count += 1

print(f"✅ Pushed {count} alerts to dashboard queue")
print("📊 Refresh your dashboard now (Ctrl+Shift+R)")

# Also print some stats
severity_counts = db.get_alert_counts()
print("\n📊 Alert Summary:")
for severity, count in severity_counts.items():
    if count > 0:
        print(f"   {severity}: {count}")

print("\n" + "=" * 50)
