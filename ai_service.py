import google.generativeai as genai
from config import GEMINI_API_KEY
from database_service import DatabaseService
from typing import List, Dict
import json

# Configure Gemini
genai.configure(api_key=GEMINI_API_KEY)

class AIService:
    def __init__(self):
        self.model = genai.GenerativeModel(
            model_name="models/gemini-2.0-flash",
            generation_config={
                "temperature": 0.7,
                "top_p": 1,
                "top_k": 1,
                "max_output_tokens": 800,
            }
        )
    
    def build_contextual_prompt(self, user_id: str, user_message: str, conversation_history: List[Dict], user_analysis: Dict, db_service: DatabaseService) -> str:
        """Build a contextual prompt based on user's conversation history and analysis"""
        system_prompt = (
            "You are a warm, supportive, and helpful assistant trained to support users with mental health "
            "and addiction recovery. You are not a therapist, but you offer empathetic, kind, and motivating conversation. "
            "Always maintain a supportive and non-judgmental tone. Personalize your responses based on the user's history and patterns."
        )
        context_parts = [system_prompt]
        context_parts.append(f"\nUser Profile (ID: {user_id}):")
        if user_analysis["total_messages"] > 0:
            context_parts.append(f"- Total messages: {user_analysis['total_messages']}")
            context_parts.append(f"- Engagement level: {user_analysis['engagement_level']}")
            context_parts.append(f"- Overall sentiment trend: {user_analysis['sentiment']}")
            if user_analysis["topics"]:
                context_parts.append(f"- Common topics discussed: {', '.join(user_analysis['topics'])}")
            if user_analysis["last_message_time"]:
                context_parts.append(f"- Last message was sent recently")
        user_summary = db_service.get_user_conversation_summary(user_id)
        if user_summary["total_conversations"] > 0:
            context_parts.append(f"- User has {user_summary['total_conversations']} total conversations")
        if conversation_history:
            context_parts.append("\nRecent Conversation History:")
            for msg in conversation_history[-6:]:
                role = "User" if msg["role"] == "user" else "Assistant"
                context_parts.append(f"{role}: {msg['content']}")
        context_parts.append(f"\nCurrent User Message: {user_message}")
        context_parts.append("\nAssistant:")
        return "\n".join(context_parts)
    
    def generate_response(self, user_id: str, user_message: str, conversation_history: List[Dict], user_analysis: Dict, db_service: DatabaseService) -> str:
        try:
            full_prompt = self.build_contextual_prompt(user_id, user_message, conversation_history, user_analysis, db_service)
            response = self.model.generate_content(full_prompt)
            ai_response = response.text.strip()
            if not ai_response or len(ai_response) < 10:
                ai_response = "I understand what you're saying. Could you tell me more about how you're feeling?"
            return ai_response
        except Exception as e:
            return (
                "I'm here to listen and support you. I'm experiencing some technical difficulties right now, "
                "but I want you to know that your feelings are valid and important. "
                "Would you like to try sharing again?"
            )
    
    def analyze_user_message(self, message: str) -> Dict:
        message_lower = message.lower()
        crisis_keywords = ["suicide", "kill myself", "end it all", "don't want to live", "give up", "no reason to live"]
        is_crisis = any(keyword in message_lower for keyword in crisis_keywords)
        urgent_keywords = ["emergency", "urgent", "help now", "crisis", "panic", "overwhelmed", "can't cope"]
        is_urgent = any(keyword in message_lower for keyword in urgent_keywords)
        positive_keywords = ["better", "improved", "happy", "good", "progress", "achievement", "positive", "grateful"]
        is_positive = any(keyword in message_lower for keyword in positive_keywords)
        negative_keywords = ["sad", "depressed", "anxious", "worried", "struggling", "difficult", "negative", "hopeless"]
        is_negative = any(keyword in message_lower for keyword in negative_keywords)
        wellness_keywords = ["therapy", "meditation", "exercise", "breathing", "coping", "recovery", "treatment"]
        is_wellness = any(keyword in message_lower for keyword in wellness_keywords)
        return {
            "is_crisis": is_crisis,
            "is_urgent": is_urgent,
            "is_positive": is_positive,
            "is_negative": is_negative,
            "is_wellness": is_wellness,
            "message_length": len(message),
            "has_question": "?" in message,
            "urgency_level": "high" if is_crisis else "medium" if is_urgent else "low"
        }
    
    def get_personalized_greeting(self, user_id: str, user_analysis: Dict) -> str:
        if user_analysis["total_messages"] == 0:
            return "Hello! I'm here to support you. How are you feeling today?"
        if user_analysis["engagement_level"] == "high":
            return "Welcome back! I'm glad to see you again. How have you been since we last talked?"
        elif user_analysis["sentiment"] == "positive":
            return "Hello! I noticed you've been in a positive mood lately. How are you doing today?"
        elif user_analysis["sentiment"] == "negative":
            return "Hi there. I'm here to listen and support you. What's on your mind today?"
        else:
            return "Hello! How are you feeling today? I'm here to listen and support you." 