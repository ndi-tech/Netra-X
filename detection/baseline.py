"""
Netra-X Baseline Trainer
"""

import pickle
import time
import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.ensemble import IsolationForest
import logging

from config import MODELS_DIR, BASELINE_DURATION, MIN_BASELINE_SAMPLES, FEATURE_NAMES

logger = logging.getLogger(__name__)

class BaselineTrainer:
    def __init__(self, model_name: str = "netrax_baseline.pkl"):
        self.model_name = model_name
        self.model_path = MODELS_DIR / model_name
        self.model = None
        self.feature_names = FEATURE_NAMES
        self.training_data = []
        
    def collect_training_data(self, feature_extractor, duration: int = BASELINE_DURATION):
        logger.info(f"Collecting baseline data for {duration} seconds...")
        start_time = time.time()
        window_count = 0
        
        while time.time() - start_time < duration:
            features = feature_extractor.get_latest_features()
            if features:
                feature_values = [features.get(name, 0) for name in self.feature_names]
                if not all(v == 0 for v in feature_values):
                    self.training_data.append(feature_values)
                    window_count += 1
                    if window_count % 5 == 0:
                        logger.info(f"Collected {window_count} windows")
            time.sleep(1)
        
        logger.info(f"Collected {len(self.training_data)} windows")
        return len(self.training_data)
    
    def train_model(self) -> bool:
        if len(self.training_data) < MIN_BASELINE_SAMPLES:
            logger.error(f"Need {MIN_BASELINE_SAMPLES} samples, got {len(self.training_data)}")
            return False
        
        df = pd.DataFrame(self.training_data, columns=self.feature_names)
        df = df.replace([np.inf, -np.inf], np.nan)
        df = df.fillna(0)
        
        logger.info("Training Isolation Forest...")
        self.model = IsolationForest(contamination=0.1, random_state=42)
        self.model.fit(df)
        self.save_model()
        logger.info(f"Model saved to {self.model_path}")
        return True
    
    def save_model(self):
        if self.model:
            with open(self.model_path, 'wb') as f:
                pickle.dump({
                    'model': self.model,
                    'feature_names': self.feature_names,
                    'training_samples': len(self.training_data)
                }, f)
                
    def load_model(self) -> bool:
        if not self.model_path.exists():
            return False
        try:
            with open(self.model_path, 'rb') as f:
                data = pickle.load(f)
                self.model = data['model']
                self.feature_names = data.get('feature_names', self.feature_names)
                return True
        except:
            return False
