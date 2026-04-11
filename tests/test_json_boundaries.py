#!/usr/bin/env python3
"""Quick test: Which JSON values produce problematic boundaries?"""

import json

# Test values that might be at boundaries
test_values = [
    0.0, 0.001, 0.01, 0.5, 0.99, 0.999, 0.9999, 0.99999, 1.0,
    # Also test values that might round problematically
    0.9999500, 0.9999999, 0.0000001, 1.0000001
]

print("JSON Boundary Serialization Test")
print("="*70)

failures = []

for val in test_values:
    # Simulate JSON round-trip
    json_str = json.dumps({"reward": val})
    parsed = json.loads(json_str)
    parsed_val = parsed["reward"]
    
    # Check if it's still exactly 0.0 or 1.0
    is_boundary = (parsed_val == 0.0 or parsed_val == 1.0)
    is_outside = parsed_val < 0 or parsed_val > 1
    
    status = "❌ FAIL" if (is_boundary or is_outside) else "✓ PASS"
    
    print(f"{status}: Original={val}, Parsed={parsed_val}, String={json_str}")
    
    if is_boundary or is_outside:
        failures.append((val, parsed_val))

print("\n" + "="*70)
if failures:
    print(f"❌ Found {len(failures)} problematic values:")
    for orig, parsed in failures:
        print(f"  {orig} -> {parsed}")
else:
    print("✅ All JSON serialization is boundary-safe")
