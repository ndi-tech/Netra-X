#!/usr/bin/env python3
"""
Netra-X - Network Intrusion Detection System
"""

import argparse
import sys
import time
import threading
import logging
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from config import DEFAULT_INTERFACE, WINDOW_SIZE, BASELINE_DURATION
from capture.packet_capture import PacketCapture
from features.feature_extractor import FeatureExtractor
from detection.baseline import BaselineTrainer
from detection.detector import Detector
from alerts.alert_manager import AlertManager
from database.database import Database
from demo.traffic_generator import TrafficGenerator

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class NetraX:
    def __init__(self, interface: str = DEFAULT_INTERFACE):
        self.interface = interface
        self.is_running = False
        self.db = Database()
        self.feature_extractor = FeatureExtractor(window_size=WINDOW_SIZE)
        self.baseline_trainer = BaselineTrainer()
        self.alert_manager = AlertManager(self.db)
        
        self.baseline_trainer.load_model()
        if self.baseline_trainer.model:
            self.detector = Detector(self.baseline_trainer)
            
        self.capture = PacketCapture(interface=interface, callback=self._packet_callback)
        
    def _packet_callback(self, packet_info):
        self.feature_extractor.process_packet(packet_info)
        
    def run_baseline_mode(self):
        logger.info(f"BASELINE MODE on {self.interface}")
        self.is_running = True
        self.capture.start_capture()
        samples = self.baseline_trainer.collect_training_data(self.feature_extractor, duration=BASELINE_DURATION)
        if samples >= 10:
            self.baseline_trainer.train_model()
            logger.info("Baseline trained successfully")
        else:
            logger.error(f"Not enough samples: {samples}")
        self.capture.stop_capture()
        
    def run_detection_mode(self):
        if not self.baseline_trainer.model:
            logger.error("No baseline model. Run baseline first.")
            return
        logger.info(f"DETECTION MODE on {self.interface}")
        self.detector = Detector(self.baseline_trainer)
        self.is_running = True
        self.capture.start_capture()
        try:
            while self.is_running:
                features = self.feature_extractor.get_latest_features()
                if features:
                    is_anomalous, score, reason, details = self.detector.detect_anomaly(features)
                    if is_anomalous:
                        self.alert_manager.create_alert(is_anomalous, score, reason, details, features)
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Stopping...")
        finally:
            self.capture.stop_capture()
            
    def run_demo_mode(self):
        logger.info("DEMO MODE - Generating test traffic")
        demo = TrafficGenerator(interface="lo", duration=30)
        demo_thread = threading.Thread(target=demo.generate_test_traffic, daemon=True)
        demo_thread.start()
        self.run_detection_mode()

def main():
    parser = argparse.ArgumentParser(description="Netra-X NIDS")
    parser.add_argument('--interface', '-i', default='lo', help='Network interface')
    parser.add_argument('--mode', '-m', choices=['baseline', 'detect', 'demo'], help='Operation mode')
    args = parser.parse_args()
    
    if not args.mode:
        parser.print_help()
        return
        
    netrax = NetraX(interface=args.interface)
    try:
        if args.mode == 'baseline':
            netrax.run_baseline_mode()
        elif args.mode == 'detect':
            netrax.run_detection_mode()
        elif args.mode == 'demo':
            netrax.run_demo_mode()
    except KeyboardInterrupt:
        print("
Stopping Netra-X...")
        netrax.is_running = False
        netrax.capture.stop_capture()

if __name__ == "__main__":
    main()
