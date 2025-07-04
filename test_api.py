#!/usr/bin/env python3
"""
Test script for AI Doctor Assistant API
Tests the integrated system with Firebase Functions as proxy to Python microservice
"""

import requests
import json
import time
from datetime import datetime

# Configuration
FIREBASE_FUNCTIONS_URL = "http://localhost:5001/aidoctor-xxxxx/us-central1"
PYTHON_SERVICE_URL = "http://localhost:8000"

def test_health_check():
    """Test health check endpoints"""
    print("🔍 Testing health checks...")
    
    # Test Firebase Functions health
    try:
        response = requests.get(f"{FIREBASE_FUNCTIONS_URL}/health")
        print(f"✅ Firebase Functions Health: {response.status_code}")
        if response.status_code == 200:
            print(f"   Status: {response.json()}")
    except Exception as e:
        print(f"❌ Firebase Functions Health failed: {e}")
    
    # Test Python microservice health
    try:
        response = requests.get(f"{PYTHON_SERVICE_URL}/health")
        print(f"✅ Python Service Health: {response.status_code}")
        if response.status_code == 200:
            print(f"   Status: {response.json()}")
    except Exception as e:
        print(f"❌ Python Service Health failed: {e}")

def test_complete_workflow():
    """Test the complete LangGraph workflow through Firebase Functions"""
    print("\n🔄 Testing complete workflow (LangGraph)...")
    
    test_cases = [
        {
            "text": "Tengo dolor de cabeza intenso desde hace 3 días, también tengo fiebre de 38°C y me siento muy cansado. Mi nombre es Juan Pérez y tengo 35 años.",
            "description": "Patient with headache, fever, and fatigue"
        },
        {
            "text": "Me duele el estómago después de comer, tengo náuseas y vómitos. Soy María García, 28 años.",
            "description": "Patient with stomach pain and nausea"
        },
        {
            "text": "Tengo dificultad para respirar y tos seca. Me llamo Carlos López, 45 años.",
            "description": "Patient with breathing difficulty and dry cough"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📋 Test Case {i}: {test_case['description']}")
        
        start_time = time.time()
        
        try:
            response = requests.post(
                f"{FIREBASE_FUNCTIONS_URL}/process",
                json={
                    "text": test_case["text"],
                    "patient_id": f"test_patient_{i}_{int(time.time())}",
                    "language": "es"
                },
                timeout=60
            )
            
            latency_ms = int((time.time() - start_time) * 1000)
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Success (Latency: {latency_ms}ms)")
                print(f"   Patient ID: {result.get('patient_id', 'N/A')}")
                print(f"   Symptoms: {len(result.get('symptoms', []))} found")
                print(f"   Diagnosis: {result.get('diagnosis', 'N/A')[:100]}...")
                print(f"   Treatment: {result.get('treatment', 'N/A')[:100]}...")
                print(f"   Recommendations: {len(result.get('recommendations', []))} items")
                print(f"   Drift Detected: {result.get('metadata', {}).get('drift_detected', False)}")
            else:
                print(f"❌ Failed: {response.status_code}")
                print(f"   Error: {response.text}")
                
        except Exception as e:
            print(f"❌ Exception: {e}")

def test_individual_services():
    """Test individual services through Firebase Functions"""
    print("\n🔧 Testing individual services...")
    
    # Test extraction
    print("\n📝 Testing extraction service...")
    try:
        response = requests.post(
            f"{FIREBASE_FUNCTIONS_URL}/extract",
            json={
                "text": "Tengo dolor de cabeza y fiebre. Mi nombre es Ana Martínez, 30 años.",
                "language": "es"
            }
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Extraction successful")
            print(f"   Patient Info: {result.get('extraction', {}).get('patient_info', {})}")
            print(f"   Symptoms: {result.get('extraction', {}).get('symptoms', [])}")
        else:
            print(f"❌ Extraction failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Extraction exception: {e}")
    
    # Test diagnosis
    print("\n🏥 Testing diagnosis service...")
    try:
        response = requests.post(
            f"{FIREBASE_FUNCTIONS_URL}/diagnose",
            json={
                "symptoms": "Dolor de cabeza intenso, fiebre de 38°C, fatiga",
                "model": "gpt-4",
                "language": "es"
            }
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Diagnosis successful")
            print(f"   Diagnosis: {result.get('diagnosis', {}).get('diagnosis', 'N/A')[:100]}...")
            print(f"   Treatment: {result.get('diagnosis', {}).get('treatment', 'N/A')[:100]}...")
        else:
            print(f"❌ Diagnosis failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Diagnosis exception: {e}")

def test_memory_operations():
    """Test memory operations"""
    print("\n🧠 Testing memory operations...")
    
    patient_id = f"test_memory_{int(time.time())}"
    
    # Test save to memory
    print("\n💾 Testing save to memory...")
    try:
        response = requests.post(
            f"{FIREBASE_FUNCTIONS_URL}/saveMemory",
            json={
                "patient_id": patient_id,
                "content": "Consulta anterior: Dolor de cabeza y fiebre. Diagnóstico: Migraña con fiebre viral.",
                "content_type": "consultation"
            }
        )
        
        if response.status_code == 200:
            print(f"✅ Memory save successful")
        else:
            print(f"❌ Memory save failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Memory save exception: {e}")
    
    # Test query memory
    print("\n🔍 Testing memory query...")
    try:
        response = requests.post(
            f"{FIREBASE_FUNCTIONS_URL}/queryMemory",
            json={
                "patient_id": patient_id,
                "query": "dolor de cabeza",
                "limit": 5
            }
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Memory query successful")
            print(f"   Results: {len(result.get('results', []))} found")
        else:
            print(f"❌ Memory query failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Memory query exception: {e}")

def test_mlops():
    """Test MLops operations"""
    print("\n📊 Testing MLops operations...")
    
    # Test MLflow logging
    print("\n📈 Testing MLflow logging...")
    try:
        response = requests.post(
            f"{FIREBASE_FUNCTIONS_URL}/logMLflow",
            json={
                "metric_name": "test_metric",
                "value": 0.95,
                "step": int(time.time()),
                "tags": {
                    "test": True,
                    "timestamp": datetime.now().isoformat()
                }
            }
        )
        
        if response.status_code == 200:
            print(f"✅ MLflow logging successful")
        else:
            print(f"❌ MLflow logging failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ MLflow logging exception: {e}")
    
    # Test drift detection
    print("\n🔍 Testing drift detection...")
    try:
        response = requests.post(
            f"{FIREBASE_FUNCTIONS_URL}/checkDrift",
            json={
                "current_data": {
                    "symptoms": ["dolor de cabeza", "fiebre"],
                    "patient_info": {"age": 30, "gender": "F"},
                    "extraction_confidence": 0.85
                },
                "reference_data": [],
                "threshold": 0.05
            }
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Drift detection successful")
            print(f"   Drift detected: {result.get('drift_detected', False)}")
            print(f"   Drift score: {result.get('drift_score', 0.0)}")
        else:
            print(f"❌ Drift detection failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Drift detection exception: {e}")

def test_direct_python_service():
    """Test direct Python microservice endpoints"""
    print("\n🐍 Testing direct Python microservice...")
    
    # Test the new /process endpoint
    print("\n🔄 Testing Python /process endpoint...")
    try:
        response = requests.post(
            f"{PYTHON_SERVICE_URL}/process",
            json={
                "text": "Tengo dolor de estómago y náuseas. Mi nombre es Pedro Sánchez, 40 años.",
                "language": "es"
            },
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Python /process successful")
            print(f"   Patient ID: {result.get('patient_id', 'N/A')}")
            print(f"   Symptoms: {len(result.get('symptoms', []))} found")
            print(f"   Diagnosis: {result.get('diagnosis', 'N/A')[:100]}...")
            print(f"   Workflow version: {result.get('metadata', {}).get('workflow_version', 'N/A')}")
        else:
            print(f"❌ Python /process failed: {response.status_code}")
            print(f"   Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Python /process exception: {e}")

def main():
    """Run all tests"""
    print("🚀 Starting AI Doctor Assistant API Tests")
    print("=" * 50)
    
    # Test health checks
    test_health_check()
    
    # Test complete workflow through Firebase Functions
    test_complete_workflow()
    
    # Test individual services
    test_individual_services()
    
    # Test memory operations
    test_memory_operations()
    
    # Test MLops
    test_mlops()
    
    # Test direct Python service
    test_direct_python_service()
    
    print("\n" + "=" * 50)
    print("✅ All tests completed!")

if __name__ == "__main__":
    main()
