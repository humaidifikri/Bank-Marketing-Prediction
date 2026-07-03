import sys
sys.path.append('../app')
from app.predict import predict_subscription

sample_input = {
    "age": 35, "job": "technician", "marital": "married", "education": "secondary",
    "default": "no", "balance": 1500, "housing": "yes", "loan": "no",
    "contact": "cellular", "month": "may", "campaign": 2, "pdays": -1,
    "previous": 0, "poutcome": "unknown"
}

result = predict_subscription(sample_input)
print(result)

sample_positive = {
    "age": 70, "job": "retired", "marital": "married", "education": "tertiary",
    "default": "no", "balance": 5000, "housing": "no", "loan": "no",
    "contact": "cellular", "month": "mar", "campaign": 1, "pdays": 95,
    "previous": 2, "poutcome": "success"
}
result2 = predict_subscription(sample_positive)
print(result2)
