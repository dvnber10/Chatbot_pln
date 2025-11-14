from pydantic import BaseModel
from typing import Optional, Dict, Any
from enum import Enum
from datetime import datetime

class MessageType(str, Enum):
    USER = "user"
    BOT = "bot"

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    session_id: str
    category: str
    matched_keyword: Optional[str] = None
    timestamp: datetime
    processing_time: float

class ChatSession(BaseModel):
    session_id: str
    messages: list
    created_at: datetime
    last_activity: datetime

class NLPAnalysis(BaseModel):
    tokens: list[str]
    lemmas: list[str]
    pos_tags: list[tuple[str, str, str]]  # (texto, lemma, POS)
    processed_message: str

class HealthCheck(BaseModel):
    status: str
    nlp_models_loaded: bool
    timestamp: datetime