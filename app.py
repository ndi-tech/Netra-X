#!/usr/bin/env python3
"""
Netra-X Dashboard Launcher
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from dashboard.routes import app
from config import DASHBOARD_HOST, DASHBOARD_PORT

if __name__ == "__main__":
    print("=" * 50)
    print("NETRA-X DASHBOARD")
    print("=" * 50)
    print(f"Dashboard: http://localhost:{DASHBOARD_PORT}")
    app.run(host=DASHBOARD_HOST, port=DASHBOARD_PORT, debug=True, threaded=True)
