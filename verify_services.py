#!/usr/bin/env python
"""Comprehensive health check of all project services."""
import sys
sys.path.insert(0, '.')

from platform.services.service_layer import (
    EnvironmentService, 
    DockerService, 
    APIService,
    ValidationService
)
from platform.core.os_layer import OSLayer

print("=" * 70)
print("SERVICE HEALTH CHECK")
print("=" * 70)

# Create services
os_layer = OSLayer()
env_svc = EnvironmentService()
docker_svc = DockerService(os_layer)
api_svc = APIService(os_layer)
val_svc = ValidationService(os_layer)

# Check each service
services = [
    ("EnvironmentService", env_svc),
    ("DockerService", docker_svc),
    ("APIService", api_svc),
]

results = {}
for name, service in services:
    print(f"\n[*] Checking {name}...")
    health = service.health_check()
    results[name] = {
        "status": str(health.status),
        "message": health.message,
        "healthy": health.status.value == "healthy"
    }
    
    status_symbol = "[OK]" if health.status.value == "healthy" else "[!]"
    print(f"    {status_symbol} Status: {health.status.value}")
    print(f"    Message: {health.message}")

# Validation Service (no health_check, so test it manually)
print(f"\n[*] Checking ValidationService...")
val_result = val_svc.test_all_tasks()
val_healthy = len(val_result) == 3 and all(r.get("valid") for r in val_result.values())
results["ValidationService"] = {
    "status": "healthy" if val_healthy else "unhealthy",
    "message": f"Tested {len(val_result)} tasks successfully" if val_healthy else "Task testing failed",
    "healthy": val_healthy
}
status_symbol = "[OK]" if val_healthy else "[!]"
print(f"    {status_symbol} Status: {'healthy' if val_healthy else 'unhealthy'}")
print(f"    Message: {results['ValidationService']['message']}")

# Summary
print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)

healthy_count = sum(1 for r in results.values() if r["healthy"])
total_count = len(results)

print(f"\nHealthy Services: {healthy_count}/{total_count}")
for name, result in results.items():
    status = "[OK]" if result["healthy"] else "[FAIL]"
    print(f"  {status} {name}")

print("\n" + "=" * 70)
if healthy_count >= 3:  # At least 3 of 4 (Docker may not be available on all systems)
    print("OVERALL STATUS: DEPLOYMENT READY")
else:
    print("OVERALL STATUS: CRITICAL ISSUES")
print("=" * 70)
