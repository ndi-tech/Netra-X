#!/usr/bin/env python3
"""
Netra-X System Test
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

print("=" * 60)
print("NETRA-X SYSTEM TEST")
print("=" * 60)

# Test 1: Database
print("\n1. Testing Database...")
try:
    from database.database import Database
    db = Database()
    print("   PASS - Database initialized")
except Exception as e:
    print(f"   FAIL - {e}")

# Test 2: Config
print("\n2. Testing Config...")
try:
    import config
    print("   PASS - Config loaded")
except Exception as e:
    print(f"   FAIL - {e}")

# Test 3: Feature Extractor
print("\n3. Testing Feature Extractor...")
try:
    from features.feature_extractor import FeatureExtractor
    fe = FeatureExtractor()
    print("   PASS - Feature Extractor ready")
except Exception as e:
    print(f"   FAIL - {e}")

# Test 4: Baseline
print("\n4. Testing Baseline Trainer...")
try:
    from detection.baseline import BaselineTrainer
    bt = BaselineTrainer()
    print("   PASS - Baseline Trainer ready")
except Exception as e:
    print(f"   FAIL - {e}")

# Test 5: Alert Manager
print("\n5. Testing Alert Manager...")
try:
    from alerts.alert_manager import AlertManager
    am = AlertManager(db)
    print("   PASS - Alert Manager ready")
except Exception as e:
    print(f"   FAIL - {e}")

# Test 6: Dashboard
print("\n6. Testing Dashboard...")
try:
    from dashboard.routes import app
    print("   PASS - Dashboard routes loaded")
except Exception as e:
    print(f"   FAIL - {e}")

print("\n" + "=" * 60)
print("TEST COMPLETE")
print("=" * 60)
