from typing import Dict, List, Optional
import uuid
from datetime import datetime
from src.Models.chat_model import ChatSession

class ChatbotRepository:
    def __init__(self):
        # Sesiones de chat en memoria
        self.sessions: Dict[str, ChatSession] = {}
        
        # Estadísticas
        self.message_count = 0
        self.categories_count = {}

    def create_session(self) -> str:
        session_id = str(uuid.uuid4())
        now = datetime.now()
        
        self.sessions[session_id] = ChatSession(
            session_id=session_id,
            messages=[],
            created_at=now,
            last_activity=now
        )
        return session_id

    def get_session(self, session_id: str) -> Optional[ChatSession]:
        return self.sessions.get(session_id)

    def save_message(self, session_id: str, message: dict):
        if session_id not in self.sessions:
            self.create_session()
        
        session = self.sessions[session_id]
        session.messages.append(message)
        session.last_activity = datetime.now()
        
        # Actualizar estadísticas
        self.message_count += 1
        category = message.get('category', 'unknown')
        self.categories_count[category] = self.categories_count.get(category, 0) + 1

    def get_chat_history(self, session_id: str) -> List[dict]:
        session = self.get_session(session_id)
        return session.messages if session else []

    def get_all_sessions(self) -> List[ChatSession]:
        return list(self.sessions.values())

    def cleanup_old_sessions(self, hours: int = 24):
        """Eliminar sesiones inactivas por más de X horas"""
        now = datetime.now()
        sessions_to_delete = []
        
        for session_id, session in self.sessions.items():
            if (now - session.last_activity).total_seconds() > hours * 3600:
                sessions_to_delete.append(session_id)
        
        for session_id in sessions_to_delete:
            del self.sessions[session_id]

    def get_stats(self) -> dict:
        return {
            "total_sessions": len(self.sessions),
            "total_messages": self.message_count,
            "categories_count": self.categories_count,
            "active_sessions": len([s for s in self.sessions.values() 
                                  if (datetime.now() - s.last_activity).total_seconds() < 3600])
        }