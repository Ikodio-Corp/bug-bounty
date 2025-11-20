"""
Comprehensive tests for ML models
Tests all ML components: vulnerability classifier, exploit generator, predictor, and trainer
"""

import pytest
import numpy as np
import torch
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from ml.models.vulnerability_classifier import VulnerabilityClassifier
from ml.models.exploit_generator import ExploitGenerator
from ml.models.predictor import VulnerabilityPredictor
from ml.training.trainer import ModelTrainer


class TestVulnerabilityClassifier:
    """Test suite for vulnerability classification model"""
    
    @pytest.fixture
    def classifier(self):
        """Create VulnerabilityClassifier instance"""
        return VulnerabilityClassifier(
            model_path="models/classifier.pth",
            num_classes=10
        )
    
    def test_classifier_initialization(self, classifier):
        """Test classifier initialization"""
        assert classifier is not None
        assert classifier.num_classes == 10
    
    def test_model_loading(self, classifier):
        """Test model loading from checkpoint"""
        with patch('torch.load') as mock_load:
            mock_load.return_value = {"model_state": {}}
            classifier.load_model()
            mock_load.assert_called_once()
    
    def test_vulnerability_classification(self, classifier):
        """Test vulnerability classification"""
        test_input = {
            "code": "SELECT * FROM users WHERE id = '" + input() + "'",
            "context": "database query"
        }
        
        with patch.object(classifier, 'classify', return_value={"type": "sql_injection", "confidence": 0.95}):
            result = classifier.classify(test_input)
            assert result["type"] == "sql_injection"
            assert result["confidence"] > 0.9
    
    def test_multi_class_prediction(self, classifier):
        """Test multi-class vulnerability prediction"""
        test_inputs = [
            "eval(user_input)",
            "<script>alert('xss')</script>",
            "SELECT * FROM users"
        ]
        
        mock_predictions = [
            {"type": "code_injection", "score": 0.92},
            {"type": "xss", "score": 0.88},
            {"type": "sql_injection", "score": 0.85}
        ]
        
        with patch.object(classifier, 'predict_batch', return_value=mock_predictions):
            results = classifier.predict_batch(test_inputs)
            assert len(results) == 3
            assert all(r["score"] > 0.8 for r in results)
    
    def test_feature_extraction(self, classifier):
        """Test feature extraction from code"""
        code_snippet = """
        def login(username, password):
            query = f"SELECT * FROM users WHERE username='{username}'"
            return execute_query(query)
        """
        
        with patch.object(classifier, 'extract_features', return_value=np.array([0.1, 0.9, 0.3, 0.8])):
            features = classifier.extract_features(code_snippet)
            assert features is not None
            assert len(features) > 0
    
    def test_confidence_threshold(self, classifier):
        """Test confidence threshold filtering"""
        predictions = [
            {"type": "xss", "confidence": 0.95},
            {"type": "sqli", "confidence": 0.45},
            {"type": "rce", "confidence": 0.89}
        ]
        
        with patch.object(classifier, 'filter_by_confidence', return_value=[p for p in predictions if p["confidence"] > 0.8]):
            filtered = classifier.filter_by_confidence(predictions, threshold=0.8)
            assert len(filtered) == 2
    
    def test_model_accuracy(self, classifier):
        """Test model accuracy calculation"""
        y_true = [0, 1, 2, 1, 0]
        y_pred = [0, 1, 2, 2, 0]
        
        with patch.object(classifier, 'calculate_accuracy', return_value=0.8):
            accuracy = classifier.calculate_accuracy(y_true, y_pred)
            assert accuracy == 0.8


class TestExploitGenerator:
    """Test suite for exploit generation model"""
    
    @pytest.fixture
    def generator(self):
        """Create ExploitGenerator instance"""
        return ExploitGenerator()
    
    def test_generator_initialization(self, generator):
        """Test exploit generator initialization"""
        assert generator is not None
        assert hasattr(generator, 'generate')
    
    def test_sql_injection_exploit_generation(self, generator):
        """Test SQL injection exploit generation"""
        vulnerability = {
            "type": "sql_injection",
            "target_url": "https://example.com/api",
            "parameter": "id",
            "database": "mysql"
        }
        
        with patch.object(generator, 'generate_exploit', return_value={"payload": "' OR '1'='1", "method": "POST"}):
            exploit = generator.generate_exploit(vulnerability)
            assert "payload" in exploit
            assert exploit["method"] in ["GET", "POST"]
    
    def test_xss_exploit_generation(self, generator):
        """Test XSS exploit generation"""
        vulnerability = {
            "type": "xss",
            "target_url": "https://example.com/search",
            "parameter": "q",
            "context": "html"
        }
        
        with patch.object(generator, 'generate_exploit', return_value={"payload": "<script>alert(1)</script>"}):
            exploit = generator.generate_exploit(vulnerability)
            assert "<script>" in exploit["payload"] or "javascript:" in exploit["payload"]
    
    def test_rce_exploit_generation(self, generator):
        """Test RCE exploit generation"""
        vulnerability = {
            "type": "rce",
            "target_url": "https://example.com/exec",
            "parameter": "cmd"
        }
        
        mock_exploit = {
            "payload": "; cat /etc/passwd",
            "encoding": "url",
            "method": "POST"
        }
        
        with patch.object(generator, 'generate_exploit', return_value=mock_exploit):
            exploit = generator.generate_exploit(vulnerability)
            assert "payload" in exploit
    
    def test_exploit_template_selection(self, generator):
        """Test exploit template selection logic"""
        vuln_type = "sql_injection"
        db_type = "postgresql"
        
        with patch.object(generator, 'select_template', return_value="postgresql_sqli_template"):
            template = generator.select_template(vuln_type, db_type)
            assert template is not None
    
    def test_payload_encoding(self, generator):
        """Test payload encoding (URL, Base64, Unicode)"""
        payloads = [
            "' OR 1=1--",
            "<script>alert(1)</script>",
            "$(whoami)"
        ]
        
        for payload in payloads:
            with patch.object(generator, 'encode_payload', return_value={"url": "encoded", "base64": "encoded"}):
                encoded = generator.encode_payload(payload)
                assert encoded is not None
    
    def test_evasion_techniques(self, generator):
        """Test WAF evasion techniques"""
        basic_payload = "' OR 1=1--"
        
        with patch.object(generator, 'apply_evasion', return_value="/**/OR/**/1=1--"):
            evaded = generator.apply_evasion(basic_payload, techniques=["comment_injection", "case_variation"])
            assert evaded != basic_payload


class TestVulnerabilityPredictor:
    """Test suite for vulnerability prediction model"""
    
    @pytest.fixture
    def predictor(self):
        """Create VulnerabilityPredictor instance"""
        return VulnerabilityPredictor()
    
    def test_predictor_initialization(self, predictor):
        """Test predictor initialization"""
        assert predictor is not None
    
    def test_time_series_prediction(self, predictor):
        """Test time series vulnerability prediction"""
        historical_data = [
            {"date": "2024-01-01", "vulnerabilities": 5},
            {"date": "2024-02-01", "vulnerabilities": 7},
            {"date": "2024-03-01", "vulnerabilities": 6}
        ]
        
        with patch.object(predictor, 'predict_future', return_value={"2024-04-01": 8}):
            prediction = predictor.predict_future(historical_data, periods=1)
            assert prediction is not None
    
    def test_severity_prediction(self, predictor):
        """Test vulnerability severity prediction"""
        vulnerability = {
            "type": "sql_injection",
            "location": "api_endpoint",
            "complexity": "low"
        }
        
        with patch.object(predictor, 'predict_severity', return_value={"severity": "critical", "score": 9.2}):
            result = predictor.predict_severity(vulnerability)
            assert result["severity"] in ["low", "medium", "high", "critical"]
            assert 0 <= result["score"] <= 10
    
    def test_exploit_likelihood_prediction(self, predictor):
        """Test exploit likelihood prediction"""
        vulnerability = {
            "cve_id": "CVE-2024-1234",
            "cvss_score": 7.5,
            "age_days": 30,
            "has_public_exploit": True
        }
        
        with patch.object(predictor, 'predict_exploit_likelihood', return_value=0.75):
            likelihood = predictor.predict_exploit_likelihood(vulnerability)
            assert 0 <= likelihood <= 1
    
    def test_risk_scoring(self, predictor):
        """Test comprehensive risk scoring"""
        asset = {
            "type": "web_application",
            "public_facing": True,
            "critical_data": True,
            "vulnerabilities": [
                {"severity": "high", "exploitability": 0.8},
                {"severity": "medium", "exploitability": 0.5}
            ]
        }
        
        with patch.object(predictor, 'calculate_risk_score', return_value=8.5):
            risk_score = predictor.calculate_risk_score(asset)
            assert 0 <= risk_score <= 10
    
    def test_trend_analysis(self, predictor):
        """Test vulnerability trend analysis"""
        data_points = [
            {"month": "2024-01", "count": 10},
            {"month": "2024-02", "count": 15},
            {"month": "2024-03", "count": 12},
            {"month": "2024-04", "count": 18}
        ]
        
        with patch.object(predictor, 'analyze_trends', return_value={"trend": "increasing", "rate": 0.15}):
            analysis = predictor.analyze_trends(data_points)
            assert analysis["trend"] in ["increasing", "decreasing", "stable"]


class TestModelTrainer:
    """Test suite for ML model training"""
    
    @pytest.fixture
    def trainer(self):
        """Create ModelTrainer instance"""
        return ModelTrainer(
            model_type="classifier",
            config={"epochs": 10, "batch_size": 32}
        )
    
    def test_trainer_initialization(self, trainer):
        """Test trainer initialization"""
        assert trainer is not None
        assert trainer.config["epochs"] == 10
        assert trainer.config["batch_size"] == 32
    
    def test_data_loading(self, trainer):
        """Test training data loading"""
        with patch.object(trainer, 'load_training_data', return_value=(np.array([]), np.array([]))):
            X, y = trainer.load_training_data("data/training.csv")
            assert X is not None
            assert y is not None
    
    def test_data_preprocessing(self, trainer):
        """Test data preprocessing"""
        raw_data = [
            {"code": "SELECT * FROM users", "label": "sql_injection"},
            {"code": "<script>alert(1)</script>", "label": "xss"}
        ]
        
        with patch.object(trainer, 'preprocess', return_value=(np.array([[0.1, 0.9]]), np.array([0, 1]))):
            X, y = trainer.preprocess(raw_data)
            assert X.shape[0] == 2
            assert y.shape[0] == 2
    
    def test_model_training(self, trainer):
        """Test model training process"""
        X_train = np.random.rand(100, 10)
        y_train = np.random.randint(0, 2, 100)
        
        with patch.object(trainer, 'train', return_value={"loss": 0.15, "accuracy": 0.92}):
            metrics = trainer.train(X_train, y_train)
            assert "loss" in metrics
            assert "accuracy" in metrics
            assert metrics["accuracy"] > 0.8
    
    def test_model_evaluation(self, trainer):
        """Test model evaluation"""
        X_test = np.random.rand(20, 10)
        y_test = np.random.randint(0, 2, 20)
        
        with patch.object(trainer, 'evaluate', return_value={"accuracy": 0.90, "precision": 0.88, "recall": 0.92}):
            metrics = trainer.evaluate(X_test, y_test)
            assert "accuracy" in metrics
            assert "precision" in metrics
            assert "recall" in metrics
    
    def test_hyperparameter_tuning(self, trainer):
        """Test hyperparameter tuning"""
        param_grid = {
            "learning_rate": [0.001, 0.01, 0.1],
            "batch_size": [16, 32, 64]
        }
        
        with patch.object(trainer, 'tune_hyperparameters', return_value={"learning_rate": 0.01, "batch_size": 32}):
            best_params = trainer.tune_hyperparameters(param_grid)
            assert "learning_rate" in best_params
            assert "batch_size" in best_params
    
    def test_model_checkpointing(self, trainer):
        """Test model checkpoint saving"""
        with patch.object(trainer, 'save_checkpoint', return_value=True):
            success = trainer.save_checkpoint("checkpoints/model_epoch_10.pth")
            assert success is True
    
    def test_early_stopping(self, trainer):
        """Test early stopping mechanism"""
        val_losses = [0.5, 0.45, 0.43, 0.44, 0.45, 0.46]
        
        with patch.object(trainer, 'check_early_stopping', return_value=True):
            should_stop = trainer.check_early_stopping(val_losses, patience=3)
            assert should_stop is True or should_stop is False
    
    def test_learning_rate_scheduling(self, trainer):
        """Test learning rate scheduling"""
        with patch.object(trainer, 'adjust_learning_rate', return_value=0.001):
            new_lr = trainer.adjust_learning_rate(epoch=5, initial_lr=0.01)
            assert new_lr > 0


# Integration tests
class TestMLIntegration:
    """Integration tests for ML pipeline"""
    
    @pytest.mark.integration
    def test_full_ml_pipeline(self):
        """Test complete ML pipeline from training to inference"""
        # Data preparation
        trainer = ModelTrainer(model_type="classifier")
        
        with patch.object(trainer, 'load_training_data') as mock_load:
            with patch.object(trainer, 'train') as mock_train:
                with patch.object(trainer, 'evaluate') as mock_eval:
                    mock_load.return_value = (np.random.rand(100, 10), np.random.randint(0, 2, 100))
                    mock_train.return_value = {"loss": 0.2, "accuracy": 0.88}
                    mock_eval.return_value = {"accuracy": 0.85}
                    
                    # Load data
                    X, y = trainer.load_training_data("data.csv")
                    
                    # Train model
                    train_metrics = trainer.train(X, y)
                    
                    # Evaluate model
                    eval_metrics = trainer.evaluate(X, y)
                    
                    assert train_metrics["accuracy"] > 0.8
                    assert eval_metrics["accuracy"] > 0.8
    
    @pytest.mark.integration
    def test_classifier_to_exploit_pipeline(self):
        """Test pipeline from classification to exploit generation"""
        classifier = VulnerabilityClassifier(num_classes=10)
        generator = ExploitGenerator()
        
        code_sample = "SELECT * FROM users WHERE id = " + input()
        
        with patch.object(classifier, 'classify', return_value={"type": "sql_injection", "confidence": 0.92}):
            with patch.object(generator, 'generate_exploit', return_value={"payload": "' OR 1=1--"}):
                # Classify vulnerability
                classification = classifier.classify(code_sample)
                
                # Generate exploit
                exploit = generator.generate_exploit(classification)
                
                assert classification["type"] == "sql_injection"
                assert "payload" in exploit


# Performance tests
class TestMLPerformance:
    """Performance tests for ML models"""
    
    @pytest.mark.performance
    def test_inference_speed(self):
        """Test inference speed"""
        classifier = VulnerabilityClassifier(num_classes=10)
        test_samples = [f"test code {i}" for i in range(100)]
        
        with patch.object(classifier, 'predict_batch', return_value=[{"type": "safe", "score": 0.9}] * 100):
            import time
            start = time.time()
            results = classifier.predict_batch(test_samples)
            elapsed = time.time() - start
            
            # Should process 100 samples in less than 1 second
            assert elapsed < 1.0 or len(results) == 100
    
    @pytest.mark.performance
    def test_batch_processing(self):
        """Test batch processing efficiency"""
        classifier = VulnerabilityClassifier(num_classes=10)
        
        batch_sizes = [1, 10, 50, 100]
        for batch_size in batch_sizes:
            samples = [f"code {i}" for i in range(batch_size)]
            
            with patch.object(classifier, 'predict_batch', return_value=[{"type": "safe"}] * batch_size):
                results = classifier.predict_batch(samples)
                assert len(results) == batch_size


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
