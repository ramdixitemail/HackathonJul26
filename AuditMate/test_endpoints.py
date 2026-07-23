#!/usr/bin/env python
import urllib.request
import urllib.parse
import json

BASE_URL = 'http://localhost:8001'

def test_health():
    print('=== Test 1: Health ===')
    try:
        response = urllib.request.urlopen(f'{BASE_URL}/api/health')
        data = json.loads(response.read().decode())
        print(json.dumps(data, indent=2))
        return True
    except Exception as e:
        print(f'Error: {e}')
        return False

def test_kpis():
    print('\n=== Test 2: KPIs ===')
    try:
        response = urllib.request.urlopen(f'{BASE_URL}/api/graph/kpis')
        data = json.loads(response.read().decode())
        print(json.dumps(data, indent=2))
        return True
    except Exception as e:
        print(f'Error: {e}')
        return False

def test_list_evidence():
    print('\n=== Test 3: List Evidence ===')
    try:
        response = urllib.request.urlopen(f'{BASE_URL}/api/evidence')
        data = json.loads(response.read().decode())
        print(json.dumps(data, indent=2))
        return True
    except Exception as e:
        print(f'Error: {e}')
        return False

def test_audit_intake():
    print('\n=== Test 4: Audit Intake ===')
    audit_request = {
        "audit_id": "AUD-2026-0142"
    }
    
    data = json.dumps(audit_request).encode('utf-8')
    req = urllib.request.Request(
        f'{BASE_URL}/api/audit-intake',
        data=data,
        headers={'Content-Type': 'application/json'},
        method='POST'
    )
    
    try:
        response = urllib.request.urlopen(req)
        result = json.loads(response.read().decode())
        print(f"Audit ID: {result['audit_id']}")
        print(f"Audit Points: {len(result['audit_points'])} points")
        for p in result['audit_points'][:3]:
            print(f"  - {p['id']}: {p['text'][:60]}...")
        return True
    except Exception as e:
        print(f'Error: {e}')
        return False

def test_graph_query():
    print('\n=== Test 5: Graph Query ===')
    query_text = "What are the high-severity SIIs that are overdue?"
    
    req = urllib.request.Request(
        f'{BASE_URL}/api/graph/query?question={urllib.parse.quote(query_text)}',
        data=b'',
        headers={'Content-Type': 'application/json'},
        method='POST'
    )
    
    try:
        response = urllib.request.urlopen(req)
        result = json.loads(response.read().decode())
        print(f"Narrative: {result['narrative']}")
        print(f"Records: {len(result['table'])} SIIs found")
        return True
    except Exception as e:
        print(f'Error: {e}')
        return False

def test_evidence_collection():
    print('\n=== Test 6: Evidence Collection ===')
    collection_request = {
        "request_id": "REQ-TEST-001",
        "requested_by": "test_user",
        "control_ref": "AUD-2026-0142",
        "instruction": "Collect evidence for CHG-000123. Trace the dbLink flow and show transaction control. Pull the design page. Capture the portal for APP-001.",
        "evidence_goals": [
            "last_pr_for_change",
            "data_from_dblink_only",
            "transaction_control"
        ],
        "agents": {
            "github": {
                "enabled": True,
                "input": {}
            },
            "doc_repo": {
                "enabled": True,
                "input": {}
            },
            "portal": {
                "enabled": True,
                "input": {}
            }
        },
        "application_id": "APP-001"
    }
    
    data = json.dumps(collection_request).encode('utf-8')
    req = urllib.request.Request(
        f'{BASE_URL}/api/evidence/collect',
        data=data,
        headers={'Content-Type': 'application/json'},
        method='POST'
    )
    
    try:
        response = urllib.request.urlopen(req)
        result = json.loads(response.read().decode())
        print(f"Request ID: {result['request_id']}")
        print(f"Total Items: {sum(result['counts'].values())}")
        for source, count in result['counts'].items():
            print(f"  - {source}: {count}")
        return True
    except Exception as e:
        print(f'Error: {e}')
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    results = {
        'health': test_health(),
        'kpis': test_kpis(),
        'list_evidence': test_list_evidence(),
        'audit_intake': test_audit_intake(),
        'graph_query': test_graph_query(),
        'evidence_collection': test_evidence_collection(),
    }
    
    print('\n=== Summary ===')
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    for test, status in results.items():
        mark = '✓ PASS' if status else '✗ FAIL'
        print(f'{mark}: {test}')
    print(f'\nTotal: {passed}/{total} passed')
