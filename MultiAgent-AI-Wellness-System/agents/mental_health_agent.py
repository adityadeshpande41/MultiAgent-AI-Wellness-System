# Mental health specialist agent
from openai import OpenAI
from app.config import settings

client = OpenAI(api_key=settings.OPENAI_API_KEY)
DISCLAIMER = "⚠️ I'm not a licensed therapist. This is educational only. Seek professional help for serious concerns."

class MentalHealthAgent:
    """Mental health specialist using dedicated mental health knowledge base."""

    def respond(self, message: str, user: str = None) -> str:
        # Get user profile for personalized advice
        profile_context = ""
        if user:
            try:
                from tools.db import get_session, UserProfile
                from sqlmodel import select
                
                with get_session() as s:
                    profile = s.exec(select(UserProfile).where(UserProfile.user == user)).first()
                    if profile:
                        profile_context = f"""
User Profile Context:
- Age: {profile.age}, Gender: {profile.gender}
- Stress Level: {profile.stress_level}
- Sleep: {profile.sleep_hours}h
- Health Conditions: {profile.health_conditions or 'none'}
- Medications: {profile.medications or 'none'}
- Activity Level: {profile.activity_level}
"""
            except Exception:
                pass
        
        # Try to retrieve context from mental health knowledge base
        context_docs = ""
        try:
            from tools.rag import search_mental_health
            context_docs = "\n".join(search_mental_health(message))
        except Exception:
            context_docs = "No additional context available."
        
        prompt = (
            f"You are a mental health specialist. {DISCLAIMER}\n\n"
            f"User says: '{message}'\n\n"
            f"{profile_context}\n"
            f"Context: {context_docs}\n\n"
            f"Give a compassionate, helpful response (2-3 sentences max). "
            f"Provide evidence-based coping strategies and techniques. "
            f"Always encourage professional help for serious concerns."
        )

        reply = client.chat.completions.create(
            model=settings.CHAT_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        ).choices[0].message.content

        reply = f"🧠 *[Mental Health Specialist]*\n{reply}"

        return reply