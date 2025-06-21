import logging
import mlflow
import os
from typing import Dict, Any
from datetime import datetime
import json

logger = logging.getLogger(__name__)

class MLOpsLogger:
    def __init__(self):
        """Initialize MLOps logger with MLflow and Firestore."""
        # Configure MLflow
        mlflow.set_tracking_uri(os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5000"))
        self.experiment_name = "ai-doctor-assistant"
        
        # Ensure experiment exists
        try:
            mlflow.get_experiment_by_name(self.experiment_name)
        except:
            mlflow.create_experiment(self.experiment_name)
        
        mlflow.set_experiment(self.experiment_name)
        
    def log_request(
        self,
        request_id: str,
        input_type: str,
        model: str,
        prompt_version: str,
        latency_ms: int,
        extraction_result: Dict[str, Any],
        diagnosis_result: Dict[str, Any]
    ) -> None:
        """
        Log request details to MLflow and Firestore.
        
        Args:
            request_id: Unique request identifier
            input_type: Type of input (audio/text)
            model: LLM model used
            prompt_version: Version of prompts used
            latency_ms: Request latency in milliseconds
            extraction_result: Results from medical information extraction
            diagnosis_result: Results from diagnosis generation
        """
        try:
            # Log to MLflow
            with mlflow.start_run(run_name=f"request_{request_id}"):
                # Log parameters
                mlflow.log_param("request_id", request_id)
                mlflow.log_param("input_type", input_type)
                mlflow.log_param("model", model)
                mlflow.log_param("prompt_version", prompt_version)
                
                # Log metrics
                mlflow.log_metric("latency_ms", latency_ms)
                mlflow.log_metric("symptoms_count", len(extraction_result.get("symptoms", [])))
                mlflow.log_metric("extraction_success", 1)
                mlflow.log_metric("diagnosis_success", 1)
                
                # Log artifacts
                self._log_artifacts(extraction_result, diagnosis_result)
                
            # Log to Firestore (if configured)
            self._log_to_firestore(
                request_id, input_type, model, prompt_version, 
                latency_ms, extraction_result, diagnosis_result
            )
            
            logger.info(f"Successfully logged request {request_id}")
            
        except Exception as e:
            logger.error(f"Error logging request {request_id}: {str(e)}")
    
    def log_error(
        self,
        request_id: str,
        error_message: str,
        latency_ms: int
    ) -> None:
        """
        Log error details.
        
        Args:
            request_id: Unique request identifier
            error_message: Error message
            latency_ms: Request latency in milliseconds
        """
        try:
            with mlflow.start_run(run_name=f"error_{request_id}"):
                mlflow.log_param("request_id", request_id)
                mlflow.log_param("error", error_message)
                mlflow.log_metric("latency_ms", latency_ms)
                mlflow.log_metric("success", 0)
            
            logger.error(f"Logged error for request {request_id}: {error_message}")
            
        except Exception as e:
            logger.error(f"Error logging error for request {request_id}: {str(e)}")
    
    def _log_artifacts(
        self,
        extraction_result: Dict[str, Any],
        diagnosis_result: Dict[str, Any]
    ) -> None:
        """Log artifacts to MLflow."""
        try:
            # Save extraction result
            with open("extraction_result.json", "w") as f:
                json.dump(extraction_result, f, indent=2)
            mlflow.log_artifact("extraction_result.json")
            
            # Save diagnosis result
            with open("diagnosis_result.json", "w") as f:
                json.dump(diagnosis_result, f, indent=2)
            mlflow.log_artifact("diagnosis_result.json")
            
            # Clean up temporary files
            os.remove("extraction_result.json")
            os.remove("diagnosis_result.json")
            
        except Exception as e:
            logger.error(f"Error logging artifacts: {str(e)}")
    
    def _log_to_firestore(
        self,
        request_id: str,
        input_type: str,
        model: str,
        prompt_version: str,
        latency_ms: int,
        extraction_result: Dict[str, Any],
        diagnosis_result: Dict[str, Any]
    ) -> None:
        """Log to Firestore (if configured)."""
        try:
            # This would connect to Firestore in production
            # For now, we'll just log that we would do this
            firestore_data = {
                "request_id": request_id,
                "timestamp": datetime.utcnow().isoformat(),
                "input_type": input_type,
                "model": model,
                "prompt_version": prompt_version,
                "latency_ms": latency_ms,
                "extraction_result": extraction_result,
                "diagnosis_result": diagnosis_result
            }
            
            logger.info(f"Would log to Firestore: {json.dumps(firestore_data, indent=2)}")
            
        except Exception as e:
            logger.error(f"Error logging to Firestore: {str(e)}")
    
    def get_experiment_metrics(self, experiment_name: str = None) -> Dict[str, Any]:
        """
        Get metrics from MLflow experiment.
        
        Args:
            experiment_name: Name of experiment to query
            
        Returns:
            Dictionary of experiment metrics
        """
        try:
            if experiment_name is None:
                experiment_name = self.experiment_name
            
            experiment = mlflow.get_experiment_by_name(experiment_name)
            if experiment is None:
                return {"error": "Experiment not found"}
            
            runs = mlflow.search_runs(experiment_ids=[experiment.experiment_id])
            
            metrics = {
                "total_runs": len(runs),
                "avg_latency": runs["metrics.latency_ms"].mean() if "metrics.latency_ms" in runs.columns else 0,
                "success_rate": runs["metrics.success"].mean() if "metrics.success" in runs.columns else 0,
                "avg_symptoms_count": runs["metrics.symptoms_count"].mean() if "metrics.symptoms_count" in runs.columns else 0
            }
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error getting experiment metrics: {str(e)}")
            return {"error": str(e)} 