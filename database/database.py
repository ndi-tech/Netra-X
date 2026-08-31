"""
Netra-X Database Layer
"""

import sqlite3
import json
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any
import logging

logger = logging.getLogger(__name__)

class Database:
    def __init__(self, db_path: Path = Path("data/netrax.db")):
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()
    
    def _init_db(self):
        conn = sqlite3.connect(str(self.db_path))
        conn.execute("""
            CREATE TABLE IF NOT EXISTS alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                source_ip TEXT,
                dest_ip TEXT,
                alert_type TEXT NOT NULL,
                severity TEXT NOT NULL,
                anomaly_score REAL NOT NULL,
                reason TEXT NOT NULL,
                features TEXT,
                status TEXT DEFAULT "active"
            )
        """)
        conn.commit()
        conn.close()
        logger.info("Database initialized")
    
    def save_alert(self, alert_data: Dict[str, Any]) -> int:
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.execute("""
            INSERT INTO alerts (timestamp, source_ip, dest_ip, alert_type, severity, anomaly_score, reason, features)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            alert_data.get("timestamp", datetime.now().isoformat()),
            alert_data.get("source_ip"),
            alert_data.get("dest_ip"),
            alert_data.get("alert_type"),
            alert_data.get("severity"),
            alert_data.get("anomaly_score"),
            alert_data.get("reason"),
            json.dumps(alert_data.get("features", {}))
        ))
        conn.commit()
        alert_id = cursor.lastrowid
        conn.close()
        return alert_id
    
    def get_alerts(self, limit: int = 50, severity: Optional[str] = None) -> List[Dict[str, Any]]:
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        query = "SELECT * FROM alerts"
        params = []
        if severity:
            query += " WHERE severity = ?"
            params.append(severity.upper())
        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)
        cursor = conn.execute(query, params)
        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return results
    
    def get_total_alerts(self) -> int:
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.execute("SELECT COUNT(*) as count FROM alerts")
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else 0
    
    def get_high_severity_alerts(self) -> int:
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.execute("SELECT COUNT(*) as count FROM alerts WHERE severity IN ('HIGH', 'CRITICAL')")
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else 0
    
    def get_alert_counts(self) -> Dict[str, int]:
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.execute("SELECT severity, COUNT(*) as count FROM alerts GROUP BY severity")
        results = {row[0]: row[1] for row in cursor.fetchall()}
        conn.close()
        for severity in ['LOW', 'MEDIUM', 'HIGH', 'CRITICAL']:
            if severity not in results:
                results[severity] = 0
        return results
    
    def get_recent_alerts_for_dashboard(self, limit: int = 20) -> List[Dict[str, Any]]:
        return self.get_alerts(limit=limit)
