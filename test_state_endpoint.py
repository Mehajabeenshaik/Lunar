from fastapi.testclient import TestClient
from warehouse_env.warehouse_env.server import app

client = TestClient(app)

# Test reset
r = client.post('/reset', json={'task': 'warehouse_easy'})
print(f"Reset status: {r.status_code}")
print(f"Response: {r.json()}")

if r.status_code == 200:
    sid = r.json()['session_id']
    print(f"Session ID: {sid}")
    
    # Test /state/{session_id}
    r2 = client.get(f'/state/{sid}')
    print(f"\n/state/{{sid}} status: {r2.status_code}")
    if r2.status_code == 200:
        print("✓ /state/{session_id} endpoint works!")
    else:
        print(f"✗ Error: {r2.text}")
