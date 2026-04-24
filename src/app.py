from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, HTTPException
from schemas import PredictionInput, PredictionOutput, HealthOutput, ErrorOutput
from model_loader import ModelLoader
import numpy as np
import yaml
import os

def load_config():
    config_path = os.path.join(os.path.dirname(__file__), "config.yml")
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)
    return config

config = load_config()
MODEL_PATH = os.path.join(os.path.dirname(__file__), config["model"]["model_dir"], config["model"]["model_name"])
loader = ModelLoader(MODEL_PATH)
model = None

def load_model():
    global model
    model = loader.load()
    return model

@asynccontextmanager
async def lifespan(app: FastAPI):
    load_model()
    yield

app = FastAPI(
    lifespan=lifespan,
    title=config["metadata"]["title_app"],
    version=config["metadata"]["version"],
    description=config["metadata"]["description"]
)

@app.get("/")
async def root():
    return {
        "message": config["metadata"]["title_app"],
        "version": config["metadata"]["version"],
        "description": config["metadata"]["description"],
        "status": "running",
        "endpoints": {
            "health": "/health",
            "predict": "/predict",
            "docs": "/docs"
        }
    }

@app.get("/health", response_model=HealthOutput)
async def health():
    return {
        "status": "healthy",
        "model_loaded": model is not None
    }

@app.post("/predict", response_model=PredictionOutput)
async def predict(input_data: PredictionInput):
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    # Prepare the input data for the model
    input_features = np.array([[ 
        input_data.sepal_length, 
        input_data.sepal_width, 
        input_data.petal_length, 
        input_data.petal_width
    ]])

    # Make the prediction
    prediction = model.predict(input_features)[0]
    prediction_proba = model.predict_proba(input_features)[0]
    confidence = float(np.max(prediction_proba))

    # Class name
    class_names = ["setosa", "versicolor", "virginica"]

    # Return the prediction
    return PredictionOutput(
        prediction=int(prediction),
        class_name=class_names[prediction],
        confidence=confidence
    )

if __name__ == "__main__":
    import uvicorn

    # Get the host and port from the config file
    host = config["server"]["host"]
    port = config["server"]["port"]

    # Run the FastAPI app
    uvicorn.run(app, host=host, port=port)
