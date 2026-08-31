"""
Netra-X Configuration
"""

from pathlib import Path

# Paths
BASE_DIR = Path(__file__).parent
MODELS_DIR = BASE_DIR / "models"
LOGS_DIR = BASE_DIR / "logs"
DATA_DIR = BASE_DIR / "data"

# Create directories
for d in [MODELS_DIR, LOGS_DIR, DATA_DIR]:
    d.mkdir(exist_ok=True)

# Network settings
DEFAULT_INTERFACE = "lo"
WINDOW_SIZE = 60
BASELINE_DURATION = 60  # 1 minute for testing

# Detection settings
ANOMALY_THRESHOLD = 0.6

# Severity thresholds
SEVERITY_THRESHOLDS = {
    "LOW": 0.6,
    "MEDIUM": 0.7,
    "HIGH": 0.8,
    "CRITICAL": 0.9
}

# Baseline settings
MIN_BASELINE_SAMPLES = 10

# Feature names
FEATURE_NAMES = [
    "packets_per_second",
    "connections_per_second",
    "unique_dest_ports",
    "unique_dest_ips",
    "avg_packet_size",
    "total_bytes",
    "tcp_syn_count",
    "tcp_rst_count",
    "connection_frequency",
    "protocol_distribution_udp",
    "protocol_distribution_tcp",
    "protocol_distribution_other",
    "bytes_per_packet_ratio",
    "packet_size_variance",
    "port_diversity_score",
    "connection_burstiness",
    "ip_diversity_ratio",
    "syn_rst_ratio",
    "packet_rate_stability"
]

# Alert types
ALERT_TYPES = {
    "HIGH_PORT_DIVERSITY": "Unusually high number of destination ports contacted",
    "HIGH_CONNECTION_RATE": "Connection rate significantly above baseline",
    "ABNORMAL_SYN_ACTIVITY": "Abnormally high SYN packet count",
    "PROTOCOL_ANOMALY": "Unusual protocol distribution detected",
    "PACKET_SIZE_ANOMALY": "Abnormal packet size patterns",
    "BURST_TRAFFIC": "Traffic burst significantly above normal",
    "IP_DIVERSITY_ANOMALY": "Unusually high number of unique destinations",
    "SCAN_PATTERN": "Possible port scanning behavior detected",
    "ANOMALOUS_BEHAVIOR": "Traffic behavior differs significantly from baseline"
}

# Dashboard settings
DASHBOARD_HOST = "0.0.0.0"
DASHBOARD_PORT = 5000

# Database
DB_PATH = DATA_DIR / "netrax.db"
