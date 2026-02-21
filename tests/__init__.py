"""Test configuration for pytest."""

import sys
from pathlib import Path

# Add parent directory to path to allow importing envguard
sys.path.insert(0, str(Path(__file__).parent.parent))
