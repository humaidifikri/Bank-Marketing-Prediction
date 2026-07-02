from pydantic import BaseModel, Field
from typing import Literal


class CustomerInput(BaseModel):
    age: int = Field(..., ge=18, le=100, example=35)
    job: Literal['admin.', 'blue-collar', 'entrepreneur', 'housemaid',
                 'management', 'retired', 'self-employed', 'services',
                 'student', 'technician', 'unemployed', 'unknown']
    marital: Literal['divorced', 'married', 'single', 'unknown']
    education: Literal['primary', 'secondary', 'tertiary', 'unknown']
    default: Literal['yes', 'no']
    balance: int = Field(..., example=1500)
    housing: Literal['yes', 'no']
    loan: Literal['yes', 'no']
    contact: Literal['cellular', 'telephone', 'unknown']
    month: Literal['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul',
                   'aug', 'sep', 'oct', 'nov', 'dec']
    campaign: int = Field(..., ge=1, example=2)
    pdays: int = Field(..., example=-1)
    previous: int = Field(..., ge=0, example=0)
    poutcome: Literal['failure', 'other', 'success', 'unknown']


class PredictionOutput(BaseModel):
    prediction: Literal['yes', 'no']
    probability: float
    threshold_used: float

