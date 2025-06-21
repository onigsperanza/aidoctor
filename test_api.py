#!/usr/bin/env python3
"""
Test script for AI Doctor Assistant API
"""

import requests
import json
import time

def test_health_check():
    """Test the health check endpoint."""
    print("Testing health check...")
    try:
        response = requests.get("http://localhost:8000/health")
        if response.status_code == 200:
            print("✅ Health check passed")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def test_process_endpoint():
    """Test the main process endpoint."""
    print("\nTesting process endpoint...")
    
    # Sample medical text
    test_data = {
        "text": "Patient Sarah Johnson, age 28, experiencing severe migraine headaches for the past week. She also reports sensitivity to light and nausea. No fever or other symptoms.",
        "model": "gpt-4"
    }
    
    try:
        start_time = time.time()
        response = requests.post(
            "http://localhost:8000/api/v1/process",
            headers={"Content-Type": "application/json"},
            json=test_data
        )
        end_time = time.time()
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Process endpoint successful")
            print(f"⏱️  Response time: {(end_time - start_time)*1000:.0f}ms")
            print(f"📊 API latency: {result['metadata']['latency_ms']}ms")
            print(f"👤 Patient: {result['patient_info']['name']}, Age: {result['patient_info']['age']}")
            print(f"🏥 Symptoms: {', '.join(result['symptoms'])}")
            print(f"🔍 Diagnosis: {result['diagnosis'][:100]}...")
            return True
        else:
            print(f"❌ Process endpoint failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Process endpoint error: {e}")
        return False

def test_error_handling():
    """Test error handling with invalid input."""
    print("\nTesting error handling...")
    
    # Test with no input
    test_data = {}
    
    try:
        response = requests.post(
            "http://localhost:8000/api/v1/process",
            headers={"Content-Type": "application/json"},
            json=test_data
        )
        
        if response.status_code == 400:
            print("✅ Error handling working correctly")
            return True
        else:
            print(f"❌ Unexpected response: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error handling test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🚀 AI Doctor Assistant API Tests")
    print("=" * 40)
    
    # Check if server is running
    if not test_health_check():
        print("\n❌ Server is not running. Please start the server first:")
        print("   python main.py")
        return
    
    # Run tests
    tests = [
        test_process_endpoint,
        test_error_handling
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "=" * 40)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The API is working correctly.")
    else:
        print("⚠️  Some tests failed. Please check the server logs.")

if __name__ == "__main__":
    main() 