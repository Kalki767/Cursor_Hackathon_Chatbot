from sqlalchemy.orm import Session
from models import Conversation, Message
from typing import List, Optional
from datetime import datetime

class DatabaseService:
    def __init__(self, db: Session):
        self.db = db
    
    def get_or_create_conversation(self, user_id: str) -> Conversation:
        """Get existing conversation or create a new one for a specific user"""
        conversation = self.db.query(Conversation).filter(
            Conversation.user_id == user_id
        ).first()
        
        if not conversation:
            conversation = Conversation(user_id=user_id)
            self.db.add(conversation)
            self.db.commit()
            self.db.refresh(conversation)
        return conversation
    
    def save_message(self, user_id: str, conversation_id: int, role: str, content: str) -> Message:
        """Save a new message to the conversation with user_id"""
        message = Message(
            user_id=user_id,
            conversation_id=conversation_id,
            role=role,
            content=content
        )
        self.db.add(message)
        self.db.commit()
        self.db.refresh(message)
        return message
    
    def get_conversation_history(self, user_id: str, limit: int = 10) -> List[dict]:
        """Get recent conversation history for a specific user"""
        conversation = self.db.query(Conversation).filter(
            Conversation.user_id == user_id
        ).first()
        
        if not conversation:
            return []
        
        messages = (
            self.db.query(Message)
            .filter(Message.conversation_id == conversation.id)
            .order_by(Message.timestamp.desc())
            .limit(limit)
            .all()
        )
        
        # Return in chronological order (oldest first)
        return [
            {
                "role": msg.role,
                "content": msg.content,
                "timestamp": msg.timestamp
            }
            for msg in reversed(messages)
        ]
    
    def get_user_all_conversations(self, user_id: str, limit: int = 50) -> List[dict]:
        """Get all recent messages for a user (single conversation)"""
        return self.get_conversation_history(user_id, limit=limit)
    
    def get_user_sentiment_history(self, user_id: str) -> dict:
        """Analyze user's conversation patterns and sentiment for their single conversation"""
        conversation = self.db.query(Conversation).filter(
            Conversation.user_id == user_id
        ).first()
        
        if not conversation:
            return {"message_count": 0, "topics": [], "sentiment": "neutral"}
        
        user_messages = (
            self.db.query(Message)
            .filter(
                Message.conversation_id == conversation.id,
                Message.role == "user"
            )
            .order_by(Message.timestamp.desc())
            .limit(50)
            .all()
        )
        
        message_count = len(user_messages)
        if message_count == 0:
            return {"message_count": 0, "topics": [], "sentiment": "neutral"}
        
        all_text = " ".join([msg.content.lower() for msg in user_messages])
        words = all_text.split()
        word_freq = {}
        for word in words:
            if len(word) > 3:
                word_freq[word] = word_freq.get(word, 0) + 1
        topics = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:5]
        topics = [topic[0] for topic in topics]
        positive_words = ["good", "great", "happy", "better", "improved", "thanks", "helpful", "positive", "progress"]
        negative_words = ["bad", "sad", "depressed", "anxious", "worried", "struggling", "difficult", "negative", "hopeless"]
        positive_count = sum(1 for word in words if word in positive_words)
        negative_count = sum(1 for word in words if word in negative_words)
        if positive_count > negative_count:
            sentiment = "positive"
        elif negative_count > positive_count:
            sentiment = "negative"
        else:
            sentiment = "neutral"
        total_messages = (
            self.db.query(Message)
            .filter(Message.user_id == user_id)
            .count()
        )
        return {
            "message_count": message_count,
            "total_messages": total_messages,
            "topics": topics,
            "sentiment": sentiment,
            "last_message_time": user_messages[0].timestamp if user_messages else None,
            "engagement_level": "high" if total_messages > 20 else "medium" if total_messages > 10 else "low"
        }
    
    def get_user_conversation_summary(self, user_id: str) -> dict:
        conversation = self.db.query(Conversation).filter(
            Conversation.user_id == user_id
        ).first()
        if not conversation:
            return {
                "total_conversations": 0,
                "total_messages": 0,
                "first_conversation": None,
                "last_conversation": None
            }
        message_count = (
            self.db.query(Message)
            .filter(Message.conversation_id == conversation.id)
            .count()
        )
        return {
            "total_conversations": 1,
            "total_messages": message_count,
            "first_conversation": conversation.created_at,
            "last_conversation": conversation.updated_at
        } 