#!/usr/bin/env python3
"""
AI Doctor Assistant - Firebase Emulator Test Script
Tests the Firebase Functions running in the emulator
"""

import requests
import json
import time
import os
from datetime import datetime

# Firebase Emulator Configuration
FIREBASE_EMULATOR_BASE_URL = "http://localhost:5001"
PROJECT_ID = "demo-aidoctor"  # This should match your Firebase project ID

# Test endpoints
ENDPOINTS = {
    "extract": f"{FIREBASE_EMULATOR_BASE_URL}/{PROJECT_ID}/us-central1/extract",
    "diagnose": f"{FIREBASE_EMULATOR_BASE_URL}/{PROJECT_ID}/us-central1/diagnose",
    "transcribe": f"{FIREBASE_EMULATOR_BASE_URL}/{PROJECT_ID}/us-central1/transcribe",
    "process": f"{FIREBASE_EMULATOR_BASE_URL}/{PROJECT_ID}/us-central1/process"
}

# Test data
TEST_CASES = {
    "spanish_extraction": {
        "text": "Paciente: María González, 35 años. Síntomas: dolor de cabeza intenso, náuseas, sensibilidad a la luz. Duración: 3 días. Sin antecedentes médicos relevantes.",
        "patient_id": "test_patient_001"
    },
    "spanish_diagnosis": {
        "symptoms": ["dolor de cabeza intenso", "náuseas", "sensibilidad a la luz"],
        "patient_info": {
            "name": "María González",
            "age": 35,
            "gender": "F"
        },
        "patient_id": "test_patient_001"
    },
    "english_extraction": {
        "text": "Patient: John Smith, 45 years old. Symptoms: chest pain, shortness of breath, fatigue. Duration: 2 days. History: hypertension.",
        "patient_id": "test_patient_002"
    },
    "english_diagnosis": {
        "symptoms": ["chest pain", "shortness of breath", "fatigue"],
        "patient_info": {
            "name": "John Smith",
            "age": 45,
            "gender": "M"
        },
        "patient_id": "test_patient_002"
    }
}

def test_endpoint(endpoint_name, url, data=None, files=None, method="POST"):
    """Test a specific endpoint"""
    print(f"\n🔍 Testing {endpoint_name} endpoint...")
    print(f"URL: {url}")
    
    try:
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        if method == "POST":
            if files:
                # Remove Content-Type for file uploads
                headers.pop('Content-Type', None)
                response = requests.post(url, files=files, headers=headers, timeout=30)
            else:
                response = requests.post(url, json=data, headers=headers, timeout=30)
        else:
            response = requests.get(url, headers=headers, timeout=30)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            try:
                result = response.json()
                print("✅ Success!")
                print(f"Response: {json.dumps(result, indent=2, ensure_ascii=False)}")
                return True, result
            except json.JSONDecodeError:
                print("⚠️  Response is not JSON:")
                print(response.text)
                return True, response.text
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text}")
            return False, response.text
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Make sure Firebase emulator is running")
        print("   Run: firebase emulators:start")
        return False, "Connection Error"
    except requests.exceptions.Timeout:
        print("❌ Timeout: Request took too long")
        return False, "Timeout"
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        return False, str(e)

def test_extract_endpoint():
    """Test the extract endpoint"""
    print("\n" + "="*60)
    print("🧪 TESTING EXTRACT ENDPOINT")
    print("="*60)
    
    # Test Spanish extraction
    spanish_data = TEST_CASES["spanish_extraction"]
    success, result = test_endpoint(
        "Extract (Spanish)", 
        ENDPOINTS["extract"], 
        spanish_data
    )
    
    if success:
        print("\n✅ Spanish extraction test completed")
    
    # Test English extraction
    english_data = TEST_CASES["english_extraction"]
    success, result = test_endpoint(
        "Extract (English)", 
        ENDPOINTS["extract"], 
        english_data
    )
    
    if success:
        print("\n✅ English extraction test completed")

def test_diagnose_endpoint():
    """Test the diagnose endpoint"""
    print("\n" + "="*60)
    print("🧪 TESTING DIAGNOSE ENDPOINT")
    print("="*60)
    
    # Test Spanish diagnosis
    spanish_data = TEST_CASES["spanish_diagnosis"]
    success, result = test_endpoint(
        "Diagnose (Spanish)", 
        ENDPOINTS["diagnose"], 
        spanish_data
    )
    
    if success:
        print("\n✅ Spanish diagnosis test completed")
    
    # Test English diagnosis
    english_data = TEST_CASES["english_diagnosis"]
    success, result = test_endpoint(
        "Diagnose (English)", 
        ENDPOINTS["diagnose"], 
        english_data
    )
    
    if success:
        print("\n✅ English diagnosis test completed")

def test_process_endpoint():
    """Test the process endpoint (full workflow)"""
    print("\n" + "="*60)
    print("🧪 TESTING PROCESS ENDPOINT (FULL WORKFLOW)")
    print("="*60)
    
    # Test Spanish full workflow
    spanish_data = TEST_CASES["spanish_extraction"]
    success, result = test_endpoint(
        "Process (Spanish)", 
        ENDPOINTS["process"], 
        spanish_data
    )
    
    if success:
        print("\n✅ Spanish full workflow test completed")
    
    # Test English full workflow
    english_data = TEST_CASES["english_extraction"]
    success, result = test_endpoint(
        "Process (English)", 
        ENDPOINTS["process"], 
        english_data
    )
    
    if success:
        print("\n✅ English full workflow test completed")

def test_emulator_health():
    """Test if Firebase emulator is running"""
    print("\n" + "="*60)
    print("🏥 TESTING FIREBASE EMULATOR HEALTH")
    print("="*60)
    
    # Test emulator UI
    try:
        response = requests.get("http://localhost:4000", timeout=5)
        if response.status_code == 200:
            print("✅ Firebase Emulator UI is running at http://localhost:4000")
        else:
            print("⚠️  Firebase Emulator UI responded with status:", response.status_code)
    except:
        print("❌ Firebase Emulator UI is not accessible")
    
    # Test functions endpoint
    try:
        response = requests.get(f"{FIREBASE_EMULATOR_BASE_URL}", timeout=5)
        print(f"✅ Firebase Functions emulator is running at {FIREBASE_EMULATOR_BASE_URL}")
    except:
        print("❌ Firebase Functions emulator is not accessible")
        print("   Make sure to run: firebase emulators:start")

def main():
    """Main test function"""
    print("🚀 AI Doctor Assistant - Firebase Emulator Test Suite")
    print(f"📅 Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🎯 Target: Firebase Emulator at {FIREBASE_EMULATOR_BASE_URL}")
    
    # Check if environment variables are set
    print("\n🔧 Environment Check:")
    if os.getenv("OPENAI_API_KEY"):
        print("✅ OPENAI_API_KEY is set")
    else:
        print("⚠️  OPENAI_API_KEY is not set (functions may fail)")
    
    if os.getenv("GOOGLE_API_KEY"):
        print("✅ GOOGLE_API_KEY is set")
    else:
        print("ℹ️  GOOGLE_API_KEY is not set (Gemini features will be disabled)")
    
    # Test emulator health
    test_emulator_health()
    
    # Run endpoint tests
    test_extract_endpoint()
    test_diagnose_endpoint()
    test_process_endpoint()
    
    print("\n" + "="*60)
    print("🎉 TEST SUITE COMPLETED")
    print("="*60)
    print("\n📋 Summary:")
    print("- Firebase Emulator UI: http://localhost:4000")
    print("- Functions Endpoint: http://localhost:5001")
    print("- Project ID: demo-aidoctor")
    print("\n🔗 Available endpoints:")
    for name, url in ENDPOINTS.items():
        print(f"  - {name}: {url}")
    
    print("\n💡 Tips:")
    print("- If tests fail, make sure Firebase emulator is running")
    print("- Check functions/.env for API keys")
    print("- View logs in the Firebase Emulator UI")

if __name__ == "__main__":
    main() 