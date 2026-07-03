# app/main.py
from fastapi import FastAPI, HTTPException
from .schemas import CustomerInput, PredictionOutput
from .predict import predict_subscription


app = FastAPI(
    title="Bank Marketing Prediction API",
    description="Memprediksi apakah nasabah berpotensi subscribe term deposit,"
    " berdasarkan data direct marketing campaign.",
    version="1.0.0",
)


@app.get("/", tags=['Models API'])
def root():
    return {"message": "Bank Marketing Prediction API is running."
            "Visit /docs for interactive testing."}


@app.get("/health", tags=['Models API'])
def health_check():
    return {"status": "ok"}


@app.post("/predict", tags=['Models API'], response_model=PredictionOutput)
def predict(input_data: CustomerInput):
    try:
        result = predict_subscription(input_data.model_dump())
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
