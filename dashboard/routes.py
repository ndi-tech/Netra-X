"""
Netra-X Dashboard Routes
"""

import time
import json
import logging
import sqlite3
from queue import Queue, Empty
from flask import Flask, render_template, Response, jsonify, request
from flask_cors import CORS

from database.database import Database

logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)
db = Database()
alert_queue = Queue()

# Load existing alerts on startup
def load_existing_alerts():
    try:
        alerts = db.get_recent_alerts_for_dashboard(limit=50)
        count = 0
        for alert in alerts:
            alert_queue.put(alert)
            count += 1
        if count > 0:
            print(f"✅ Loaded {count} existing alerts into dashboard queue")
    except Exception as e:
        print(f"⚠️ Error loading alerts: {e}")

load_existing_alerts()

# Traffic stats
traffic_stats = {
    'packets_per_sec': 0,
    'bandwidth': '0 B/s',
    'protocols': 'TCP: 0 | UDP: 0',
    'top_source': '-',
    'top_dest': '-',
    'port_diversity': 0,
    'active_connections': 0,
    'alert_rate': '0/min',
    'total_packets': 0
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/alerts/stream')
def alert_stream():
    def generate():
        last_alert_id = 0
        while True:
            try:
                try:
                    alert = alert_queue.get(timeout=1)
                    if alert:
                        yield f"data: {json.dumps(alert)}\n\n"
                        continue
                except Empty:
                    pass
                
                try:
                    recent = db.get_recent_alerts_for_dashboard(limit=1)
                    if recent and recent[0].get('id', 0) > last_alert_id:
                        alert = recent[0]
                        last_alert_id = alert.get('id', 0)
                        yield f"data: {json.dumps(alert)}\n\n"
                        continue
                except:
                    pass
                
                yield f"data: {json.dumps({'type': 'heartbeat'})}\n\n"
                time.sleep(1)
                
            except Exception as e:
                logger.error(f"SSE error: {e}")
                time.sleep(1)
                
    return Response(generate(), mimetype='text/event-stream')

@app.route('/api/stats')
def get_stats():
    try:
        return jsonify({
            'total_alerts': db.get_total_alerts(),
            'high_severity': db.get_high_severity_alerts(),
            'critical_alerts': db.get_alert_counts().get('CRITICAL', 0),
            'alerts': db.get_recent_alerts_for_dashboard(limit=20)
        })
    except Exception as e:
        logger.error(f"Stats error: {e}")
        return jsonify({'total_alerts': 0, 'high_severity': 0, 'critical_alerts': 0, 'alerts': []})

@app.route('/api/traffic')
def get_traffic_stats():
    return jsonify(traffic_stats)

@app.route('/api/generate_alert', methods=['POST'])
def generate_alert():
    import random
    from datetime import datetime
    
    severities = ['LOW', 'MEDIUM', 'HIGH', 'CRITICAL']
    severity = random.choice(severities)
    
    alert_data = {
        'timestamp': datetime.now().isoformat(),
        'source_ip': f"192.168.1.{random.randint(1, 254)}",
        'dest_ip': f"10.0.0.{random.randint(1, 254)}",
        'alert_type': random.choice(['ABNORMAL_SYN_ACTIVITY', 'HIGH_PORT_DIVERSITY', 'BURST_TRAFFIC', 'SCAN_PATTERN']),
        'severity': severity,
        'anomaly_score': round(0.5 + random.random() * 0.5, 3),
        'reason': f"Random test alert - {severity} severity detected",
        'features': json.dumps({'test': True})
    }
    
    alert_id = db.save_alert(alert_data)
    alert_data['id'] = alert_id
    alert_queue.put(alert_data)
    
    return jsonify({'success': True, 'id': alert_id, 'source_ip': alert_data['source_ip'], 'reason': alert_data['reason']})

@app.route('/api/clear_alerts', methods=['POST'])
def clear_alerts():
    try:
        conn = sqlite3.connect(str(db.db_path))
        conn.execute('DELETE FROM alerts')
        conn.commit()
        conn.close()
        # Clear queue
        while not alert_queue.empty():
            try:
                alert_queue.get_nowait()
            except:
                pass
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

def update_traffic_stats(packets_per_sec=0, bandwidth=0, tcp=0, udp=0, top_source='-', active_connections=0):
    global traffic_stats
    traffic_stats['packets_per_sec'] = packets_per_sec
    if bandwidth < 1024:
        traffic_stats['bandwidth'] = f"{bandwidth} B/s"
    else:
        traffic_stats['bandwidth'] = f"{bandwidth/1024:.1f} KB/s"
    traffic_stats['protocols'] = f"TCP: {tcp} | UDP: {udp}"
    traffic_stats['top_source'] = top_source
    traffic_stats['active_connections'] = active_connections

print("✅ Dashboard routes loaded successfully!")
