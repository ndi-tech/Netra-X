"""
Netra-X Detector
"""

import numpy as np
from typing import Dict, Any, Tuple
import logging

from config import ANOMALY_THRESHOLD, ALERT_TYPES

logger = logging.getLogger(__name__)

class Detector:
    def __init__(self, baseline_trainer):
        self.baseline = baseline_trainer
        self.model = baseline_trainer.model
        self.feature_names = baseline_trainer.feature_names
        self.threshold = ANOMALY_THRESHOLD
        
    def detect_anomaly(self, features: Dict[str, float]) -> Tuple[bool, float, str, Dict]:
        if not self.model:
            return False, 0.0, "No model loaded", {}
            
        feature_values = [features.get(name, 0) for name in self.feature_names]
        feature_values = np.array(feature_values).reshape(1, -1)
        feature_values = np.nan_to_num(feature_values, nan=0.0)
        
        try:
            prediction = self.model.predict(feature_values)
            anomaly_score = self.model.decision_function(feature_values)[0]
            anomaly_score_norm = 1 / (1 + np.exp(anomaly_score))
            
            is_anomalous = prediction[0] == -1 and anomaly_score_norm >= self.threshold
            
            reason = "Traffic appears normal"
            details = {'score': anomaly_score_norm}
            
            if is_anomalous:
                reason = "Traffic behavior differs significantly from baseline"
                details['alert_type'] = 'ANOMALOUS_BEHAVIOR'
                
            return is_anomalous, anomaly_score_norm, reason, details
            
        except Exception as e:
            logger.error(f"Detection error: {e}")
            return False, 0.0, f"Error: {e}", {}
