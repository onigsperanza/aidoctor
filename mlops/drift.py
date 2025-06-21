import logging
from typing import Dict, Any, List
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import json
from datetime import datetime

logger = logging.getLogger(__name__)

class DriftDetector:
    def __init__(self):
        """Initialize drift detector with baseline data."""
        self.baseline_symptoms = []
        self.baseline_extractions = []
        self.drift_threshold = 0.8
        self.symptom_count_threshold = 2
        
    def check_drift(
        self,
        extraction_result: Dict[str, Any],
        diagnosis_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Check for data drift in extraction and diagnosis results.
        
        Args:
            extraction_result: Results from medical information extraction
            diagnosis_result: Results from diagnosis generation
            
        Returns:
            Dictionary with drift detection results
        """
        try:
            drift_results = {
                "timestamp": datetime.utcnow().isoformat(),
                "drift_detected": False,
                "drift_alerts": [],
                "metrics": {}
            }
            
            # Check schema field completeness
            schema_check = self._check_schema_completeness(extraction_result)
            if not schema_check["complete"]:
                drift_results["drift_detected"] = True
                drift_results["drift_alerts"].append(f"Schema drift: {schema_check['missing_fields']}")
            
            # Check symptom count variance
            symptom_check = self._check_symptom_count_variance(extraction_result)
            if symptom_check["anomalous"]:
                drift_results["drift_detected"] = True
                drift_results["drift_alerts"].append(f"Symptom count anomaly: {symptom_check['reason']}")
            
            # Check content similarity with baseline
            similarity_check = self._check_content_similarity(extraction_result, diagnosis_result)
            if similarity_check["low_similarity"]:
                drift_results["drift_detected"] = True
                drift_results["drift_alerts"].append(f"Content drift: similarity {similarity_check['similarity_score']:.3f}")
            
            # Update baseline
            self._update_baseline(extraction_result, diagnosis_result)
            
            # Store metrics
            drift_results["metrics"] = {
                "symptom_count": len(extraction_result.get("symptoms", [])),
                "similarity_score": similarity_check["similarity_score"],
                "schema_completeness": schema_check["completeness_score"]
            }
            
            if drift_results["drift_detected"]:
                logger.warning(f"Drift detected: {drift_results['drift_alerts']}")
            else:
                logger.info("No drift detected")
            
            return drift_results
            
        except Exception as e:
            logger.error(f"Error checking drift: {str(e)}")
            return {
                "timestamp": datetime.utcnow().isoformat(),
                "drift_detected": False,
                "drift_alerts": [f"Error in drift detection: {str(e)}"],
                "metrics": {}
            }
    
    def _check_schema_completeness(self, extraction_result: Dict[str, Any]) -> Dict[str, Any]:
        """Check if all required schema fields are present."""
        required_fields = ["patient_info", "symptoms", "motive"]
        patient_info_fields = ["name", "age"]
        
        missing_fields = []
        completeness_score = 1.0
        
        # Check top-level fields
        for field in required_fields:
            if field not in extraction_result:
                missing_fields.append(field)
                completeness_score -= 0.33
        
        # Check patient_info subfields
        if "patient_info" in extraction_result:
            patient_info = extraction_result["patient_info"]
            for field in patient_info_fields:
                if field not in patient_info:
                    missing_fields.append(f"patient_info.{field}")
                    completeness_score -= 0.1
        
        return {
            "complete": len(missing_fields) == 0,
            "missing_fields": missing_fields,
            "completeness_score": max(0.0, completeness_score)
        }
    
    def _check_symptom_count_variance(self, extraction_result: Dict[str, Any]) -> Dict[str, Any]:
        """Check if symptom count is within expected range."""
        symptoms = extraction_result.get("symptoms", [])
        symptom_count = len(symptoms)
        
        if len(self.baseline_symptoms) < 5:
            # Not enough baseline data yet
            return {"anomalous": False, "reason": "Insufficient baseline data"}
        
        # Calculate statistics from baseline
        baseline_counts = [len(symptoms) for symptoms in self.baseline_symptoms]
        mean_count = np.mean(baseline_counts)
        std_count = np.std(baseline_counts)
        
        # Check if current count is within 2 standard deviations
        z_score = abs(symptom_count - mean_count) / std_count if std_count > 0 else 0
        
        anomalous = z_score > 2 or symptom_count < self.symptom_count_threshold
        
        reason = ""
        if z_score > 2:
            reason = f"Count {symptom_count} is {z_score:.2f} std devs from mean {mean_count:.1f}"
        elif symptom_count < self.symptom_count_threshold:
            reason = f"Count {symptom_count} below threshold {self.symptom_count_threshold}"
        
        return {
            "anomalous": anomalous,
            "reason": reason,
            "z_score": z_score,
            "mean_count": mean_count,
            "std_count": std_count
        }
    
    def _check_content_similarity(
        self,
        extraction_result: Dict[str, Any],
        diagnosis_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Check content similarity with baseline using cosine similarity."""
        if len(self.baseline_extractions) < 3:
            # Not enough baseline data yet
            return {"low_similarity": False, "similarity_score": 1.0}
        
        # Create feature vector for current result
        current_features = self._extract_features(extraction_result, diagnosis_result)
        
        # Calculate similarity with baseline
        similarities = []
        for baseline in self.baseline_extractions:
            similarity = cosine_similarity([current_features], [baseline])[0][0]
            similarities.append(similarity)
        
        avg_similarity = np.mean(similarities)
        low_similarity = avg_similarity < self.drift_threshold
        
        return {
            "low_similarity": low_similarity,
            "similarity_score": avg_similarity,
            "min_similarity": min(similarities),
            "max_similarity": max(similarities)
        }
    
    def _extract_features(
        self,
        extraction_result: Dict[str, Any],
        diagnosis_result: Dict[str, Any]
    ) -> List[float]:
        """Extract numerical features for similarity comparison."""
        features = []
        
        # Symptom count
        features.append(len(extraction_result.get("symptoms", [])))
        
        # Text length features
        features.append(len(extraction_result.get("motive", "")))
        features.append(len(diagnosis_result.get("diagnosis", "")))
        features.append(len(diagnosis_result.get("treatment", "")))
        features.append(len(diagnosis_result.get("recommendations", "")))
        
        # Patient age (normalized)
        age = extraction_result.get("patient_info", {}).get("age", 0)
        features.append(age / 100.0)  # Normalize age
        
        # Word count features
        features.append(len(extraction_result.get("motive", "").split()))
        features.append(len(diagnosis_result.get("diagnosis", "").split()))
        
        return features
    
    def _update_baseline(
        self,
        extraction_result: Dict[str, Any],
        diagnosis_result: Dict[str, Any]
    ) -> None:
        """Update baseline data with current results."""
        # Keep only last 100 entries to prevent memory issues
        max_baseline_size = 100
        
        # Update symptoms baseline
        self.baseline_symptoms.append(extraction_result.get("symptoms", []))
        if len(self.baseline_symptoms) > max_baseline_size:
            self.baseline_symptoms = self.baseline_symptoms[-max_baseline_size:]
        
        # Update extraction baseline
        features = self._extract_features(extraction_result, diagnosis_result)
        self.baseline_extractions.append(features)
        if len(self.baseline_extractions) > max_baseline_size:
            self.baseline_extractions = self.baseline_extractions[-max_baseline_size:]
    
    def get_drift_summary(self) -> Dict[str, Any]:
        """Get summary of drift detection statistics."""
        return {
            "baseline_size": len(self.baseline_symptoms),
            "drift_threshold": self.drift_threshold,
            "symptom_count_threshold": self.symptom_count_threshold,
            "last_updated": datetime.utcnow().isoformat()
        } 