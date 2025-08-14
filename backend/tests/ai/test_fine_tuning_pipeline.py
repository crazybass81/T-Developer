"""
FineTuningPipeline Tests - Day 32
Tests for model fine-tuning pipeline
"""

import pytest

from src.ai.fine_tuning_pipeline import FineTuningPipeline


class TestFineTuningPipeline:
    """Tests for FineTuningPipeline"""

    @pytest.fixture
    def pipeline(self):
        """Create FineTuningPipeline instance"""
        return FineTuningPipeline()

    @pytest.fixture
    def training_data(self):
        """Sample training data"""
        return [
            {"prompt": "Write a function", "completion": "def example(): pass"},
            {"prompt": "Create a class", "completion": "class Example: pass"},
            {"prompt": "Import numpy", "completion": "import numpy as np"},
        ]

    def test_pipeline_initialization(self, pipeline):
        """Test FineTuningPipeline initialization"""
        assert pipeline is not None
        assert hasattr(pipeline, "datasets")
        assert hasattr(pipeline, "models")

    def test_prepare_dataset(self, pipeline, training_data):
        """Test dataset preparation"""
        dataset = pipeline.prepare_dataset(training_data)

        assert "train" in dataset
        assert "validation" in dataset
        assert len(dataset["train"]) > 0

    def test_data_validation(self, pipeline):
        """Test training data validation"""
        valid_data = [{"prompt": "test", "completion": "result"}]
        invalid_data = [{"prompt": "test"}]  # Missing completion

        assert pipeline.validate_data(valid_data) is True
        assert pipeline.validate_data(invalid_data) is False

    def test_data_augmentation(self, pipeline, training_data):
        """Test data augmentation"""
        augmented = pipeline.augment_data(training_data)

        assert len(augmented) >= len(training_data)
        assert all("prompt" in item for item in augmented)

    def test_create_training_job(self, pipeline, training_data):
        """Test training job creation"""
        job = pipeline.create_training_job(training_data, model="gpt-3.5", epochs=3)

        assert "job_id" in job
        assert job["status"] == "created"
        assert job["epochs"] == 3

    def test_monitor_training(self, pipeline):
        """Test training monitoring"""
        job_id = "test_job_123"
        status = pipeline.get_training_status(job_id)

        assert "status" in status
        assert status["status"] in ["pending", "running", "completed", "failed"]

    def test_evaluate_model(self, pipeline):
        """Test model evaluation"""
        model_id = "test_model"
        test_data = [{"prompt": "test", "expected": "output"}]

        metrics = pipeline.evaluate_model(model_id, test_data)

        assert "accuracy" in metrics
        assert "loss" in metrics
        assert 0 <= metrics["accuracy"] <= 1

    def test_hyperparameter_tuning(self, pipeline):
        """Test hyperparameter tuning"""
        params = {
            "learning_rate": [0.001, 0.01],
            "batch_size": [16, 32],
            "epochs": [3, 5],
        }

        best_params = pipeline.tune_hyperparameters(params)

        assert "learning_rate" in best_params
        assert "batch_size" in best_params
        assert best_params["learning_rate"] in params["learning_rate"]

    def test_model_deployment(self, pipeline):
        """Test model deployment"""
        model_id = "trained_model"
        deployment = pipeline.deploy_model(model_id)

        assert deployment["deployed"] is True
        assert "endpoint" in deployment
        assert "version" in deployment

    def test_batch_inference(self, pipeline):
        """Test batch inference"""
        model_id = "deployed_model"
        prompts = ["prompt1", "prompt2", "prompt3"]

        results = pipeline.batch_inference(model_id, prompts)

        assert len(results) == len(prompts)
        assert all("completion" in r for r in results)

    def test_model_versioning(self, pipeline):
        """Test model versioning"""
        model_id = "test_model"
        version = pipeline.create_version(model_id, "v1.0")

        assert version["version"] == "v1.0"
        assert version["model_id"] == model_id

        versions = pipeline.list_versions(model_id)
        assert len(versions) >= 1

    def test_training_data_split(self, pipeline, training_data):
        """Test data splitting"""
        splits = pipeline.split_data(training_data, train_ratio=0.8)

        assert "train" in splits
        assert "test" in splits
        assert len(splits["train"]) > len(splits["test"])

    def test_checkpoint_management(self, pipeline):
        """Test checkpoint saving and loading"""
        job_id = "test_job"
        checkpoint_data = {"epoch": 5, "loss": 0.25}

        pipeline.save_checkpoint(job_id, checkpoint_data)
        loaded = pipeline.load_checkpoint(job_id)

        assert loaded["epoch"] == 5
        assert loaded["loss"] == 0.25

    def test_early_stopping(self, pipeline):
        """Test early stopping logic"""
        metrics_history = [
            {"epoch": 1, "val_loss": 0.5},
            {"epoch": 2, "val_loss": 0.4},
            {"epoch": 3, "val_loss": 0.41},  # No improvement
            {"epoch": 4, "val_loss": 0.42},  # Getting worse
        ]

        should_stop = pipeline.check_early_stopping(metrics_history, patience=2)
        assert should_stop is True

    def test_data_preprocessing(self, pipeline):
        """Test data preprocessing"""
        raw_data = [
            {"prompt": "  Write code  ", "completion": "\n\ndef func():\n    pass\n"},
        ]

        processed = pipeline.preprocess_data(raw_data)

        assert processed[0]["prompt"] == "Write code"
        assert "\n\n" not in processed[0]["completion"]

    def test_model_export(self, pipeline):
        """Test model export"""
        model_id = "test_model"
        export_path = pipeline.export_model(model_id, format="onnx")

        assert export_path.endswith(".onnx")
        assert pipeline.validate_export(export_path) is True

    def test_distributed_training(self, pipeline):
        """Test distributed training setup"""
        config = pipeline.setup_distributed_training(num_gpus=2)

        assert config["distributed"] is True
        assert config["num_gpus"] == 2
        assert "strategy" in config

    def test_training_cost_estimation(self, pipeline, training_data):
        """Test training cost estimation"""
        cost = pipeline.estimate_training_cost(training_data, epochs=10, model="gpt-3.5")

        assert "total_cost" in cost
        assert "compute_hours" in cost
        assert cost["total_cost"] > 0
