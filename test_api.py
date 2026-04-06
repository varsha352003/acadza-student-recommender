#!/usr/bin/env python3
"""Test FastAPI routes."""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi.testclient import TestClient
from app.main import app


def test_api():
    """Test all FastAPI endpoints."""
    client = TestClient(app)
    
    print("Testing FastAPI Routes...")
    
    # Test root endpoint
    print("\n1. Testing health endpoint...")
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    print(f"   ✓ GET / returns {response.status_code}")
    print(f"   ✓ Response: {data}")
    
    # Test analyze endpoint - valid student
    print("\n2. Testing analyze endpoint with valid student...")
    response = client.post("/analyze/STU_001")
    assert response.status_code == 200
    data = response.json()
    assert data['student_id'] == 'STU_001'
    assert 'average_score' in data
    assert 'weak_chapters' in data
    print(f"   ✓ POST /analyze/STU_001 returns {response.status_code}")
    print(f"   ✓ Student: {data['name']}")
    print(f"   ✓ Average score: {data['average_score']}")
    
    # Test analyze endpoint - invalid student
    print("\n3. Testing analyze endpoint with invalid student...")
    response = client.post("/analyze/INVALID_STU")
    assert response.status_code == 404
    print(f"   ✓ POST /analyze/INVALID_STU returns {response.status_code}")
    
    # Test recommend endpoint - valid student
    print("\n4. Testing recommend endpoint with valid student...")
    response = client.post("/recommend/STU_001")
    assert response.status_code == 200
    data = response.json()
    assert data['student_id'] == 'STU_001'
    assert 'summary' in data
    assert 'steps' in data
    assert len(data['steps']) > 0
    print(f"   ✓ POST /recommend/STU_001 returns {response.status_code}")
    print(f"   ✓ Focus area: {data['summary']['focus_area']}")
    print(f"   ✓ Generated {len(data['steps'])} recommendation steps:")
    for step in data['steps']:
        print(f"      - Step {step['step']}: {step['dost_type']} ({step['target_chapter']})")
    
    # Test recommend endpoint - invalid student
    print("\n5. Testing recommend endpoint with invalid student...")
    response = client.post("/recommend/INVALID_STU")
    assert response.status_code == 404
    print(f"   ✓ POST /recommend/INVALID_STU returns {response.status_code}")
    
    print("\n" + "="*60)
    print("✅ All FastAPI tests passed!")
    print("="*60)
    print("\nAPI is ready. Routes available:")
    print("  GET  /              - Health check")
    print("  POST /analyze/{student_id}    - Analyze student performance")
    print("  POST /recommend/{student_id}  - Generate recommendations")
    print("\nTo run the server:")
    print("  python -m uvicorn app.main:app --reload")


if __name__ == '__main__':
    try:
        test_api()
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
