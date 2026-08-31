"""
Netra-X Alert Manager
"""

from datetime import datetime
from typing import Dict, Any, Optional
from queue import Queue
import logging

from config import SEVERITY_THRESHOLDS
from database.database import Database

logger = logging.getLogger(__name__)

class AlertManager:
    def __init__(self, db: Database, alert_queue: Optional[Queue] = None):
        self.db = db
        self.alert_queue = alert_queue or Queue()
        self.alert_count = 0
        
    def create_alert(self, is_anomalous: bool, score: float, reason: str, 
                     details: Dict, features: Dict) -> Optional[Dict]:
        if not is_anomalous:
            return None
            
        severity = self._determine_severity(score)
        
        alert_data = {
            'timestamp': datetime.now().isoformat(),
            'source_ip': features.get('src_ip', 'unknown'),
            'dest_ip': features.get('dst_ip', 'unknown'),
            'alert_type': details.get('alert_type', 'ANOMALOUS_BEHAVIOR'),
            'severity': severity,
            'anomaly_score': score,
            'reason': reason,
            'features': features
        }
        
        alert_id = self.db.save_alert(alert_data)
        alert_data['id'] = alert_id
        self.alert_count += 1
        self.alert_queue.put(alert_data)
        
        logger.warning(f"ALERT: {severity} - {reason[:50]}")
        return alert_data
    
    def _determine_severity(self, score: float) -> str:
        for severity, threshold in SEVERITY_THRESHOLDS.items():
            if score >= threshold:
                return severity
        return 'LOW'
