from fastapi.testclient import TestClient
from warehouse_env.warehouse_env.server import app

client = TestClient(app)

print("Testing /manifest endpoint...")
r = client.get('/manifest')
print(f"Status: {r.status_code}")

if r.status_code == 200:
    m = r.json()
    graders = m.get('graders', [])
    print(f"Graders: {graders}")
    print(f"Count: {len(graders)}")
    
    # Check task_specs
    task_specs = m.get('task_specs', {})
    for task_id, spec in task_specs.items():
        has_grader = spec.get('has_grader')
        print(f"  {task_id}: has_grader={has_grader}")
else:
    print(f"Error: {r.text}")
