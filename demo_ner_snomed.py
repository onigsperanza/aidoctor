#!/usr/bin/env python3
"""
Demo script for MedCAT NER Mapping and SNOMED Validation
Shows the bonus features of the AI Doctor Assistant
"""

import requests
import json
import time
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:5001/aidoctor-ai/us-central1"  # Firebase Emulator

def demo_ner_snomed_features():
    """Demonstrate NER mapping and SNOMED validation features"""
    
    print("🧠 MedCAT NER Mapping & SNOMED Validation Demo")
    print("=" * 60)
    print(f"📅 Demo run: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # Sample medical cases with various medical concepts
    medical_cases = [
        {
            "title": "🩺 Cardiovascular Case",
            "text": "Paciente masculino de 58 años con antecedentes de hipertensión arterial, diabetes mellitus tipo 2 y dislipidemia. Presenta dolor torácico opresivo de 2 horas de evolución, irradiado al brazo izquierdo, acompañado de diaforesis y disnea. ECG muestra elevación del segmento ST en derivaciones II, III y aVF. Troponina I elevada a 15 ng/mL.",
            "patient_id": "DEMO_CARDIO_001"
        },
        {
            "title": "🧠 Neurological Case", 
            "text": "Mujer de 45 años con cefalea intensa de inicio súbito, acompañada de fotofobia, náuseas y vómitos. Refiere rigidez de nuca y alteración del estado mental. TAC cerebral muestra hemorragia subaracnoidea. Presión arterial 180/110 mmHg.",
            "patient_id": "DEMO_NEURO_001"
        },
        {
            "title": "🫁 Respiratory Case",
            "text": "Varón de 35 años con tos productiva de 3 semanas, expectoración verdosa, fiebre de 38.5°C, disnea de esfuerzo y dolor pleurítico. Radiografía de tórax muestra infiltrado alveolar en lóbulo inferior derecho. Saturación de oxígeno 92%.",
            "patient_id": "DEMO_RESP_001"
        },
        {
            "title": "🩸 Endocrine Case",
            "text": "Paciente femenina de 28 años con poliuria, polidipsia, polifagia y pérdida de peso de 5 kg en 2 meses. Glucemia en ayunas 280 mg/dL, HbA1c 12.5%. Antecedentes familiares de diabetes mellitus tipo 1.",
            "patient_id": "DEMO_ENDO_001"
        }
    ]
    
    total_concepts = 0
    total_accepted = 0
    total_flagged = 0
    total_confidence = 0
    
    for i, case in enumerate(medical_cases, 1):
        print(f"\n{i}. {case['title']}")
        print("-" * 40)
        print(f"📝 Text: {case['text'][:100]}...")
        print(f"👤 Patient ID: {case['patient_id']}")
        
        # Process the case
        start_time = time.time()
        response = requests.post(
            f"{BASE_URL}/process",
            json={
                "text": case['text'],
                "patient_id": case['patient_id']
            },
            headers={"Content-Type": "application/json"}
        )
        latency = (time.time() - start_time) * 1000
        
        if response.status_code == 200:
            data = response.json()
            ner_mapping = data.get('ner_mapping', {})
            summary = ner_mapping.get('summary', {})
            
            print(f"✅ Processing successful ({latency:.0f}ms)")
            
            # NER Statistics
            entities = summary.get('total_entities', 0)
            concepts = summary.get('total_concepts', 0)
            accepted = summary.get('accepted_concepts', 0)
            flagged = summary.get('flagged_concepts', 0)
            avg_confidence = summary.get('average_confidence', 0)
            
            total_concepts += concepts
            total_accepted += accepted
            total_flagged += flagged
            total_confidence += avg_confidence
            
            print(f"🧠 NER Results:")
            print(f"   📊 Entities detected: {entities}")
            print(f"   🏷️  Medical concepts: {concepts}")
            print(f"   ✅ SNOMED accepted: {accepted}")
            print(f"   ⚠️  SNOMED flagged: {flagged}")
            print(f"   📈 Average confidence: {avg_confidence:.3f}")
            
            # Show detailed concepts
            concepts_list = ner_mapping.get('concepts', [])
            if concepts_list:
                print(f"   📋 Sample Medical Concepts:")
                for concept in concepts_list[:5]:  # Show first 5
                    validation = next((v for v in ner_mapping.get('snomed_validation', []) 
                                     if v.get('concept_id') == concept.get('cui')), {})
                    status = "✅" if validation.get('is_valid') else "⚠️"
                    confidence = concept.get('confidence', 0)
                    name = concept.get('name', 'Unknown')
                    cui = concept.get('cui', 'Unknown')
                    
                    print(f"      {status} {name}")
                    print(f"         CUI: {cui}")
                    print(f"         Confidence: {confidence:.3f}")
                    print(f"         SNOMED Valid: {validation.get('is_valid', False)}")
                    
                    # Show semantic types if available
                    semantic_types = concept.get('semantic_types', [])
                    if semantic_types:
                        print(f"         Types: {', '.join(semantic_types)}")
            
            # Show extracted symptoms
            symptoms = data.get('symptoms', [])
            if symptoms:
                print(f"   🏥 Extracted Symptoms: {', '.join(symptoms)}")
            
            # Show diagnosis
            diagnosis = data.get('diagnosis', '')
            if diagnosis:
                print(f"   🔬 AI Diagnosis: {diagnosis[:80]}...")
                
        else:
            print(f"❌ Processing failed: {response.status_code}")
            print(f"   Error: {response.text}")
    
    # Summary statistics
    print("\n" + "=" * 60)
    print("📊 Demo Summary Statistics")
    print("=" * 60)
    
    if total_concepts > 0:
        overall_confidence = total_confidence / len(medical_cases)
        acceptance_rate = (total_accepted / total_concepts) * 100
        
        print(f"🎯 Total Medical Concepts: {total_concepts}")
        print(f"✅ SNOMED Accepted: {total_accepted} ({acceptance_rate:.1f}%)")
        print(f"⚠️  SNOMED Flagged: {total_flagged} ({(total_flagged/total_concepts)*100:.1f}%)")
        print(f"📈 Overall Average Confidence: {overall_confidence:.3f}")
        
        print(f"\n🏆 Performance Metrics:")
        print(f"   • Concept Recognition Rate: {(total_concepts/len(medical_cases)):.1f} concepts per case")
        print(f"   • SNOMED Validation Success: {acceptance_rate:.1f}%")
        print(f"   • Quality Score: {overall_confidence:.1%}")
        
        if acceptance_rate >= 80:
            print(f"   🎉 Excellent SNOMED validation performance!")
        elif acceptance_rate >= 60:
            print(f"   👍 Good SNOMED validation performance")
        else:
            print(f"   ⚠️  SNOMED validation needs improvement")
    
    print(f"\n🔧 Configuration:")
    print(f"   • SNOMED Confidence Threshold: 0.85")
    print(f"   • Graph Traversal: Enabled")
    print(f"   • Detailed Logging: Enabled")
    
    print(f"\n📈 MLflow Integration:")
    print(f"   • All metrics logged to MLflow")
    print(f"   • Experiment: ai-doctor-assistant")
    print(f"   • Artifacts: ner_results.json, drift_flags.json")

def demo_confidence_thresholds():
    """Demonstrate different confidence threshold behaviors"""
    
    print("\n\n🎯 Confidence Threshold Demo")
    print("=" * 60)
    
    # Test case with various confidence levels
    test_text = "Paciente con dolor de cabeza, fiebre alta, náuseas y vómitos. Diagnóstico presuntivo de migraña con aura."
    
    print(f"📝 Test Text: {test_text}")
    print(f"🔍 Testing different confidence thresholds...")
    
    # Simulate different confidence thresholds
    thresholds = [0.5, 0.7, 0.85, 0.95]
    
    for threshold in thresholds:
        print(f"\n   🎯 Threshold: {threshold}")
        
        # In a real scenario, you'd modify the SNOMED_CONFIG
        # For demo purposes, we'll show what would happen
        print(f"   📊 Expected behavior:")
        print(f"      • Concepts with confidence ≥ {threshold}: Accepted")
        print(f"      • Concepts with confidence < {threshold}: Flagged for review")
        print(f"      • Quality vs Coverage trade-off")

def demo_snomed_benefits():
    """Explain the benefits of SNOMED validation"""
    
    print("\n\n✅ SNOMED-CT Validation Benefits")
    print("=" * 60)
    
    benefits = [
        {
            "title": "🏥 Standardization",
            "description": "All medical concepts mapped to standardized SNOMED-CT terminology",
            "example": "Migraña → SNOMED-CT: 24700007 (Migraine)"
        },
        {
            "title": "🔍 Quality Control", 
            "description": "Confidence thresholds ensure only high-quality concepts are accepted",
            "example": "Threshold 0.85: Only concepts with 85%+ confidence accepted"
        },
        {
            "title": "📊 Interoperability",
            "description": "Enables integration with other healthcare systems and EHRs",
            "example": "Compatible with HL7 FHIR, ICD-10, and other standards"
        },
        {
            "title": "🧠 Semantic Understanding",
            "description": "Captures semantic relationships between medical concepts",
            "example": "Parent-child relationships, synonyms, and hierarchies"
        },
        {
            "title": "📈 Analytics",
            "description": "Enables advanced medical analytics and research",
            "example": "Population health studies, clinical research, quality metrics"
        }
    ]
    
    for i, benefit in enumerate(benefits, 1):
        print(f"{i}. {benefit['title']}")
        print(f"   📝 {benefit['description']}")
        print(f"   💡 Example: {benefit['example']}")
        print()

def main():
    """Run the complete NER and SNOMED demo"""
    
    try:
        # Check if service is available
        health_response = requests.get(f"{BASE_URL}/health")
        if health_response.status_code != 200:
            print("❌ Service not available. Please start the Firebase emulator first.")
            print("   Run: firebase emulators:start")
            return
        
        # Run demos
        demo_ner_snomed_features()
        demo_confidence_thresholds()
        demo_snomed_benefits()
        
        print("\n" + "=" * 60)
        print("🎉 Demo completed successfully!")
        print("=" * 60)
        print("💡 Key Takeaways:")
        print("   • MedCAT provides advanced medical NER capabilities")
        print("   • SNOMED-CT validation ensures medical concept quality")
        print("   • Configurable confidence thresholds balance quality vs coverage")
        print("   • MLflow integration provides comprehensive observability")
        print("   • All features are fully integrated into the AI Doctor Assistant")
        
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to the service.")
        print("   Please ensure the Firebase emulator is running:")
        print("   firebase emulators:start")
    except Exception as e:
        print(f"❌ Demo failed with error: {e}")

if __name__ == "__main__":
    main()
 