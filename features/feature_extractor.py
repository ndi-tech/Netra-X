"""
Netra-X Feature Extractor
"""

import time
import threading
from collections import defaultdict, deque
from datetime import datetime
from typing import Dict, List, Any, Optional
import logging
import numpy as np

from config import WINDOW_SIZE, FEATURE_NAMES

logger = logging.getLogger(__name__)

class FeatureExtractor:
    def __init__(self, window_size: int = WINDOW_SIZE):
        self.window_size = window_size
        self.current_window = []
        self.window_start = time.time()
        self.feature_buffer = deque(maxlen=100)
        self.lock = threading.Lock()
        self.active_connections = defaultdict(set)
        
    def process_packet(self, packet_info: Dict[str, Any]):
        with self.lock:
            self.current_window.append(packet_info)
            if time.time() - self.window_start >= self.window_size:
                self._process_window()
                self._reset_window()
                
    def _process_window(self):
        if not self.current_window:
            return
        features = self._calculate_features(self.current_window)
        if features:
            features['timestamp'] = datetime.now().isoformat()
            self.feature_buffer.append(features)
            
    def _calculate_features(self, window: List[Dict]) -> Dict[str, float]:
        if not window:
            return {}
            
        n_packets = len(window)
        total_bytes = sum(p.get('length', 0) for p in window)
        duration = self.window_size
        
        protocols = [p.get('protocol', 'OTHER') for p in window]
        tcp_count = protocols.count('TCP')
        udp_count = protocols.count('UDP')
        other_count = n_packets - tcp_count - udp_count
        
        src_ips = set(p.get('src_ip') for p in window if p.get('src_ip'))
        dst_ips = set(p.get('dst_ip') for p in window if p.get('dst_ip'))
        dst_ports = set(p.get('dst_port') for p in window if p.get('dst_port'))
        
        syn_count = sum(1 for p in window if p.get('tcp_flags', {}).get('SYN', False))
        rst_count = sum(1 for p in window if p.get('tcp_flags', {}).get('RST', False))
        
        packet_sizes = [p.get('length', 0) for p in window]
        avg_size = np.mean(packet_sizes) if packet_sizes else 0
        size_variance = np.var(packet_sizes) if len(packet_sizes) > 1 else 0
        
        features = {
            'packets_per_second': n_packets / duration,
            'connections_per_second': len(src_ips) / duration,
            'unique_dest_ports': len(dst_ports),
            'unique_dest_ips': len(dst_ips),
            'avg_packet_size': avg_size,
            'total_bytes': total_bytes,
            'tcp_syn_count': syn_count,
            'tcp_rst_count': rst_count,
            'connection_frequency': len(src_ips) / max(1, len(dst_ips)),
            'protocol_distribution_udp': udp_count / max(1, n_packets),
            'protocol_distribution_tcp': tcp_count / max(1, n_packets),
            'protocol_distribution_other': other_count / max(1, n_packets),
            'bytes_per_packet_ratio': total_bytes / max(1, n_packets),
            'packet_size_variance': size_variance,
            'port_diversity_score': len(dst_ports) / max(1, n_packets),
            'connection_burstiness': n_packets / max(1, len(src_ips)),
            'ip_diversity_ratio': len(dst_ips) / max(1, len(src_ips)),
            'syn_rst_ratio': syn_count / max(1, rst_count),
            'packet_rate_stability': 0
        }
        return features
        
    def _reset_window(self):
        self.current_window = []
        self.window_start = time.time()
    
    def get_latest_features(self) -> Optional[Dict]:
        with self.lock:
            if self.feature_buffer:
                return self.feature_buffer[-1]
            return None
    
    def get_all_features(self) -> List[Dict]:
        with self.lock:
            return list(self.feature_buffer)
