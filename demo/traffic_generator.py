"""
Netra-X Demo Traffic Generator
"""

import time
import socket
import random
import logging

logger = logging.getLogger(__name__)

class TrafficGenerator:
    def __init__(self, interface: str = "lo", duration: int = 30):
        self.interface = interface
        self.duration = duration
        self.is_running = False
        
    def generate_test_traffic(self):
        self.is_running = True
        logger.info("Generating test traffic...")
        start_time = time.time()
        
        while self.is_running and time.time() - start_time < self.duration:
            elapsed = time.time() - start_time
            
            if elapsed < 10:
                # Normal traffic
                for _ in range(3):
                    try:
                        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                        sock.sendto(b"Normal", ("127.0.0.1", random.randint(1000, 2000)))
                        sock.close()
                    except:
                        pass
            elif elapsed < 20:
                # Scan pattern
                for port in range(20, 30):
                    try:
                        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                        sock.sendto(b"Scan", ("127.0.0.1", port))
                        sock.close()
                    except:
                        pass
            else:
                # Burst
                for _ in range(10):
                    try:
                        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                        sock.sendto(b"Burst", ("127.0.0.1", random.randint(1, 1000)))
                        sock.close()
                    except:
                        pass
            time.sleep(0.1)
        logger.info("Traffic generation complete")
