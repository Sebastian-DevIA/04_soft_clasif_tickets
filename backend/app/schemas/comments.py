from datetime import datetime

from pydantic import BaseModel, ConfigDict


class CommentIn(BaseModel):
    text: str
    source: str = "api"


class PredictionOut(BaseModel):
    # protected_namespaces=(): 'model_version' colisiona con el namespace
    # reservado 'model_' de Pydantic v2; lo liberamos para nombrar el campo así.
    model_config = ConfigDict(from_attributes=True, protected_namespaces=())

    sentiment: str
    confidence: float
    model_version: str
    predicted_at: datetime


class CommentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    text: str
    source: str
    created_at: datetime
    prediction: PredictionOut | None
