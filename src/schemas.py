from pydantic import BaseModel

class PredictionInput(BaseModel):
    sepal_length: float
    sepal_width: float
    petal_length: float
    petal_width: float

class PredictionOutput(BaseModel):
    prediction: int
    class_name: str
    confidence: float

class HealthOutput(BaseModel):
    status: str
    model_loaded: bool

class ErrorOutput(BaseModel):
    error: str