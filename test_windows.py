#!/usr/bin/env python3
"""
Netra-X Windows Test
"""

import sys
import time
from pathlib import Path

# Add project root
sys.path.insert(0, str(Path(__file__).parent))

from database.database import Database
from features.feature_extractor import FeatureExtractor
from detection.baseline import BaselineTrainer

print("=" * 70)
print("🔵 NETRA-X WINDOWS TEST")
print("=" * 70)

# Test Database
print("\n1. Testing Database...")
try:
    db = Database()
    print("   ✅ Database initialized")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test Feature Extractor
print("\n2. Testing Feature Extractor...")
try:
    fe = FeatureExtractor()
    print(f"   ✅ Feature Extractor ready (window: {fe.window_size}s)")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test Baseline
print("\n3. Testing Baseline Trainer...")
try:
    bt = BaselineTrainer()
    print(f"   ✅ Baseline Trainer ready")
except Exception as e:
    print(f"   ❌ Error: {e}")

print("\n" + "=" * 70)
print("🛡️  Netra-X ready for action!")
print("=" * 70)
print("\nTo capture packets, you may need to run as Administrator.")
print("For testing, use: python netrax.py --interface lo --mode baseline")