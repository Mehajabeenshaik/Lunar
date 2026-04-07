#!/usr/bin/env python
"""Platform Quick Start - Initialize and run deployment."""

import sys
import os

# Add platform to path
sys.path.insert(0, os.path.dirname(__file__))

from platform.platform import WarehouseEnvPlatform
import json


def main():
    """Run full deployment pipeline."""
    repo_path = os.path.dirname(os.path.abspath(__file__))
    
    print("\n" + "=" * 70)
    print("  WAREHOUSE ENVIRONMENT - AI AGENT PLATFORM")
    print("  Autonomous Deployment & Orchestration System")
    print("=" * 70 + "\n")
    
    # Initialize platform
    print("[1/4] Initializing platform...")
    try:
        platform = WarehouseEnvPlatform(repo_path)
        print("      Platform initialized successfully")
    except Exception as e:
        print(f"      ERROR: Failed to initialize platform: {e}")
        return 1
    
    # Show platform status
    print("\n[2/4] Checking platform status...")
    status = platform.get_status()
    system_info = platform.os_layer.get_system_info()
    print(f"      OS: {system_info.os_platform}")
    print(f"      Python: {system_info.python_version}")
    print(f"      CPU Cores: {system_info.cpu_count}")
    print(f"      Memory: {system_info.memory_mb}MB")
    
    # Execute full deployment
    print("\n[3/4] Executing deployment pipeline...")
    print("      This will:")
    print("      - Setup environment (install dependencies)")
    print("      - Build Docker image")
    print("      - Validate all 3 warehouse tasks")
    print("      - Run baseline inference script")
    print("      - Perform health monitoring")
    print()
    
    result = platform.execute_full_deployment()
    
    # Generate report
    print("\n[4/4] Generating deployment report...")
    report_path = os.path.join(repo_path, "deployment_report.json")
    platform.save_report(report_path)
    print(f"      Report saved to: {report_path}")
    
    # Print results
    print("\n" + "=" * 70)
    if result['success']:
        print("  DEPLOYMENT SUCCESSFUL")
    else:
        print("  DEPLOYMENT FAILED")
    print("=" * 70)
    
    print(f"\nTotal Duration: {result['total_duration']:.2f} seconds")
    print(f"Workflows Executed: {result['workflows_executed']}/{result['workflows_total']}")
    
    if not result['success'] and result['failed_at']:
        print(f"Failed At: {result['failed_at']}")
    
    # Summary
    print("\n" + "-" * 70)
    print("SUMMARY")
    print("-" * 70)
    
    for workflow_name, workflow_result in result['results'].items():
        if isinstance(workflow_result, dict) and 'success' in workflow_result:
            status_str = "✓ PASS" if workflow_result['success'] else "✗ FAIL"
            duration = workflow_result.get('total_duration', 0)
            print(f"{status_str:8} | {workflow_name:30} | {duration:8.2f}s")
    
    print("\n" + "=" * 70)
    
    # Print next steps
    if result['success']:
        print("\nNext Steps:")
        print("1. Review deployment report: deployment_report.json")
        print("2. Test API: curl http://localhost:5000/health")
        print("3. Deploy to HF Spaces (see HF_SPACES_DEPLOYMENT.md)")
        print("4. Run: python -m platform.cli --help (for more options)")
    else:
        print("\nTroubleshooting:")
        print("1. Check deployment_report.json for details")
        print("2. Review logs in the report")
        print("3. Run: python -m platform.cli validate --repo .")
        print("4. See PLATFORM_ARCHITECTURE.md for details")
    
    print()
    return 0 if result['success'] else 1


if __name__ == "__main__":
    sys.exit(main())
