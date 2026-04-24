import pickle
import os
import logging

logger = logging.getLogger(__name__)

class ModelLoader:
    def __init__(self, model_path: str):
        self.model_path = model_path
        self.model = None

    def load(self):
        if not os.path.exists(self.model_path):
            logger.error(f"Model file not found at {self.model_path}")
            raise FileNotFoundError(f"Model file not found at {self.model_path}")
        
        with open(self.model_path, "rb") as f:
            self.model = pickle.load(f)
        logger.info("Model loaded successfully!")
        return self.model