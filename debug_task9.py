#!/usr/bin/env python3
"""Debug Task 9 initialization"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from content_moderation_env import ContentModerationEnv

print("Creating environment for Task 9...")
try:
    env = ContentModerationEnv(task_id=9)
    print("✓ Environment created")
    
    print("Calling reset()...")
    obs = env.reset()
    print(f"✓ Reset successful")
    print(f"Observation keys: {list(obs.keys())}")
    
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
