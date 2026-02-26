#!/usr/bin/env python
"""Quick test to verify space_invaders package can be imported"""
import sys
print("Python path:", sys.executable)

try:
    import space_invaders
    print("✓ space_invaders module imported successfully!")
    print("Module location:", space_invaders.__file__)
    
    # Check if run function exists
    if hasattr(space_invaders, 'run'):
        print("✓ space_invaders.run() function found")
    else:
        print("✗ space_invaders.run() function NOT found")
        print("Available attributes:", dir(space_invaders))
        
except ImportError as e:
    print("✗ Failed to import space_invaders:", e)
    print("Try installing: pip install space-invaders-pygame")
except Exception as e:
    print("✗ Unexpected error:", type(e).__name__, e)
