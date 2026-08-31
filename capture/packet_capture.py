"""
Netra-X Packet Capture (Windows Compatible)
"""

import time
import threading
import subprocess
import platform
from typing import Optional, Callable, Dict, Any
from datetime import datetime
import logging

from scapy.all import sniff, IP, TCP, UDP, ICMP

from config import DEFAULT_INTERFACE

logger = logging.getLogger(__name__)

class PacketCapture:
    def __init__(self, interface: str = DEFAULT_INTERFACE, callback: Optional[Callable] = None):
        self.interface = interface
        self.callback = callback
        self.is_capturing = False
        self.packet_count = 0
        self.start_time = None
        self.capture_thread = None
        self.stats = {'packets_captured': 0, 'bytes_captured': 0}
        
    def _packet_handler(self, packet):
        if not self.is_capturing:
            return
        self.packet_count += 1
        self.stats['packets_captured'] += 1
        
        packet_info = self._extract_packet_info(packet)
        self.stats['bytes_captured'] += packet_info.get('length', 0)
        
        if self.callback and callable(self.callback):
            self.callback(packet_info)
            
    def _extract_packet_info(self, packet) -> Dict[str, Any]:
        info = {
            'timestamp': datetime.now().isoformat(),
            'length': len(packet),
            'src_ip': None,
            'dst_ip': None,
            'src_port': None,
            'dst_port': None,
            'protocol': None,
            'tcp_flags': None
        }
        
        if packet.haslayer(IP):
            ip = packet[IP]
            info['src_ip'] = ip.src
            info['dst_ip'] = ip.dst
            
            if packet.haslayer(TCP):
                tcp = packet[TCP]
                info['protocol'] = 'TCP'
                info['src_port'] = tcp.sport
                info['dst_port'] = tcp.dport
                info['tcp_flags'] = {
                    'SYN': bool(tcp.flags & 0x02),
                    'ACK': bool(tcp.flags & 0x10),
                    'RST': bool(tcp.flags & 0x04)
                }
            elif packet.haslayer(UDP):
                udp = packet[UDP]
                info['protocol'] = 'UDP'
                info['src_port'] = udp.sport
                info['dst_port'] = udp.dport
            elif packet.haslayer(ICMP):
                info['protocol'] = 'ICMP'
        return info
    
    def start_capture(self):
        if self.is_capturing:
            return
        self.is_capturing = True
        self.start_time = time.time()
        self.capture_thread = threading.Thread(target=self._capture_loop, daemon=True)
        self.capture_thread.start()
        logger.info(f"Started capture on {self.interface}")
        
    def _capture_loop(self):
        try:
            sniff(iface=self.interface, prn=self._packet_handler, store=False)
        except Exception as e:
            logger.error(f"Capture error: {e}")
            self.is_capturing = False
            
    def stop_capture(self):
        self.is_capturing = False
        if self.capture_thread:
            self.capture_thread.join(timeout=2)
        logger.info(f"Stopped capture. Packets: {self.packet_count}")
