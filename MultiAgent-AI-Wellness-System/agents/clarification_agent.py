# Clarification agent for handling ambiguous queries
from typing import Dict, Optional
import streamlit as st

class ClarificationAgent:
    """
    Handles conversation flow when user queries are ambiguous and need clarification.
    Manages the state of clarification conversations.
    """
    
    def __init__(self):
        # Store pending clarifications (in a real app, this would be in a database)
        self.pending_clarifications = {}
    
    def is_clarification_response(self, user: str, message: str) -> bool:
        """
        Check if this message is a response to a pending clarification question.
        """
        return user in self.pending_clarifications
    
    def store_pending_clarification(self, user: str, original_message: str, scores: Dict[str, float]):
        """
        Store a pending clarification for a user.
        """
        import time
        self.pending_clarifications[user] = {
            "original_message": original_message,
            "scores": scores,
            "timestamp": time.time()
        }
        st.write(f"💾 CLARIFICATION: Stored pending clarification for user '{user}'")
    
    def get_pending_clarification(self, user: str) -> Optional[Dict]:
        """
        Get the pending clarification for a user.
        """
        return self.pending_clarifications.get(user)
    
    def clear_pending_clarification(self, user: str):
        """
        Clear the pending clarification for a user.
        """
        if user in self.pending_clarifications:
            del self.pending_clarifications[user]
            st.write(f"🗑️ CLARIFICATION: Cleared pending clarification for user '{user}'")
    
    def detect_clarification_intent(self, message: str, scores: Dict[str, float]) -> Optional[str]:
        """
        Detect if the user's response indicates a specific intent.
        Returns the detected intent or None if still unclear.
        """
        message_lower = message.lower()
        
        # Direct intent indicators
        intent_keywords = {
            "fitness": ["workout", "exercise", "fitness", "gym", "training", "physical", "sport"],
            "nutrition": ["food", "eat", "meal", "diet", "nutrition", "calorie", "hungry"],
            "health": ["health", "medical", "doctor", "symptom", "pain", "stress", "anxiety", "sleep"],
            "tracking": ["progress", "track", "summary", "analytics", "stats", "data"]
        }
        
        # Check for direct mentions
        for intent, keywords in intent_keywords.items():
            if any(keyword in message_lower for keyword in keywords):
                st.write(f"🎯 CLARIFICATION: Detected intent '{intent}' from keywords")
                return intent
        
        # Check for affirmative responses to top categories
        affirmative_words = ["yes", "yeah", "yep", "correct", "right", "exactly", "that's it"]
        negative_words = ["no", "nope", "not", "wrong", "different"]
        
        if any(word in message_lower for word in affirmative_words):
            # User is confirming the top category
            top_category = max(scores.keys(), key=lambda k: scores[k])
            st.write(f"✅ CLARIFICATION: User confirmed top category '{top_category}'")
            return top_category
        
        if any(word in message_lower for word in negative_words):
            # User is rejecting the top category, try second highest
            sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
            if len(sorted_scores) > 1:
                second_category = sorted_scores[1][0]
                st.write(f"❌ CLARIFICATION: User rejected top category, trying '{second_category}'")
                return second_category
        
        st.write("❓ CLARIFICATION: Could not detect clear intent from response")
        return None
    
    def generate_follow_up_question(self, message: str, previous_scores: Dict[str, float]) -> str:
        """
        Generate a follow-up question when the first clarification didn't work.
        """
        from openai import OpenAI
        from app.config import settings
        
        client = OpenAI(api_key=settings.OPENAI_API_KEY)
        
        # Get the top categories that are still unclear
        sorted_scores = sorted(previous_scores.items(), key=lambda x: x[1], reverse=True)
        top_categories = [cat for cat, score in sorted_scores[:2] if score > 0.1]
        
        prompt = f"""
The user said: "{message}"

I'm still not sure what they need help with. The top possibilities are: {', '.join(top_categories)}

Generate a very specific follow-up question with concrete examples to help clarify. 
Be friendly and offer 2-3 specific examples for each category.

Format: "Let me ask more specifically - are you looking for help with [specific examples]?"
Keep it conversational and under 2 sentences.
"""
        
        try:
            response = client.chat.completions.create(
                model=settings.CHAT_MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            st.write(f"❌ CLARIFICATION: Failed to generate follow-up: {e}")
            return "Could you be more specific about what you need help with? I can assist with fitness, nutrition, health, or tracking your progress."


# Global clarification agent instance
clarification_agent = ClarificationAgent()