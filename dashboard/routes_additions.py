# Add to dashboard/routes.py - these new endpoints

@app.route('/api/generate_alert', methods=['POST'])
def generate_alert():
    """Generate a test alert"""
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
        'anomaly_score': 0.5 + random.random() * 0.5,
        'reason': f"Random test alert - {severity} severity detected",
        'features': json.dumps({'test': True})
    }
    
    alert_id = db.save_alert(alert_data)
    alert_data['id'] = alert_id
    alert_queue.put(alert_data)
    
    return jsonify({'success': True, 'id': alert_id, 'source_ip': alert_data['source_ip'], 'reason': alert_data['reason']})

@app.route('/api/clear_alerts', methods=['POST'])
def clear_alerts():
    """Clear all alerts from database"""
    try:
        conn = sqlite3.connect(str(db.db_path))
        conn.execute('DELETE FROM alerts')
        conn.commit()
        conn.close()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})
