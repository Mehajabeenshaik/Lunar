"""Test complete platform deployment (20-35 minutes)."""

import sys
import os

print("\n" + "="*70)
print("QUICK TEST 3: Full Platform Deployment (20-35 minutes)")
print("="*70 + "\n")

try:
    # Import platform
    sys.path.insert(0, '.')
    from platform.platform import WarehouseEnvPlatform
    
    # Initialize
    repo_path = os.path.dirname(os.path.abspath(__file__))
    print(f"Repository path: {repo_path}\n")
    
    print("[1/2] Initializing platform...")
    platform = WarehouseEnvPlatform(repo_path)
    print("      [+] Platform initialized\n")
    
    print("[2/2] Executing deployment pipeline...")
    print("      Running all workflows...\n")
    
    # Execute
    result = platform.execute_full_deployment()
    
    # Summary
    print("\n" + "="*70)
    if result['success']:
        print("[+] DEPLOYMENT SUCCESSFUL")
    else:
        print("[-] DEPLOYMENT FAILED")
    print("="*70)
    
    print(f"\nTotal Duration: {result['total_duration']:.2f}s")
    print(f"Workflows: {result['workflows_executed']}/{result['workflows_total']}")
    
    if result['failed_at']:
        print(f"Failed at: {result['failed_at']}")
    
    # Save report
    report_path = os.path.join(repo_path, "test_deployment_report.json")
    platform.save_report(report_path)
    print(f"\nReport saved to: {report_path}")
    
except Exception as e:
    print(f"[-] TEST FAILED: {e}")
    import traceback
    traceback.print_exc()

print()
