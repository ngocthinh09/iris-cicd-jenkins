import pytest
import pickle
import os
import sys
import numpy as np
from sklearn.datasets import load_iris
from sklearn.ensemble import RandomForestClassifier

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from src.train_model import train_and_save_model, MODEL_DIR


class TestModelTraining:

    @pytest.fixture(autouse=True)
    def setup_and_teardown(self):
        os.makedirs(MODEL_DIR, exist_ok=True)
        yield

    def test_train_model_success(self):
        accuracy = train_and_save_model()
        assert accuracy is not None
        assert isinstance(accuracy, (float, np.floating))
        assert 0 <= accuracy <= 1

    def test_model_accuracy_threshold(self):
        accuracy = train_and_save_model()
        assert accuracy >= 0.90, f"Model accuracy {accuracy:.2%} is below 90% threshold"

    def test_model_file_created(self):
        train_and_save_model()
        model_path = os.path.join(MODEL_DIR, "iris_model.pkl")
        assert os.path.exists(model_path)
        assert os.path.getsize(model_path) > 0

    def test_model_can_be_loaded(self):
        train_and_save_model()
        model_path = os.path.join(MODEL_DIR, "iris_model.pkl")
        with open(model_path, "rb") as f:
            model = pickle.load(f)
        assert isinstance(model, RandomForestClassifier)
        assert hasattr(model, 'predict')
        assert hasattr(model, 'predict_proba')

    def test_loaded_model_can_predict(self):
        train_and_save_model()
        model_path = os.path.join(MODEL_DIR, "iris_model.pkl")
        with open(model_path, "rb") as f:
            model = pickle.load(f)
        iris = load_iris()
        X_sample = iris.data[:5]

        predictions = model.predict(X_sample)
        probabilities = model.predict_proba(X_sample)

        assert len(predictions) == 5
        assert all(pred in [0, 1, 2] for pred in predictions)
        assert probabilities.shape == (5, 3)
        assert all(np.isclose(prob.sum(), 1.0) for prob in probabilities)

    def test_model_parameters(self):
        train_and_save_model()
        model_path = os.path.join(MODEL_DIR, "iris_model.pkl")
        with open(model_path, "rb") as f:
            model = pickle.load(f)
        assert model.n_estimators == 100
        assert model.random_state == 42
        assert model.n_classes_ == 3
        assert model.n_features_in_ == 4

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
