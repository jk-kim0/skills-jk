import sys
import os

# Ensure lib/ is on sys.path before any test imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "lib"))
