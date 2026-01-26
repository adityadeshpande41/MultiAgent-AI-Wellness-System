from openai import OpenAI
from app.config import settings
from tools.db import Workout, get_session

client = OpenAI(api_key=settings.OPENAI_API_KEY)

class FitnessCoachAgent:
    """Motivational fitness coach providing workout guidance and training advice."""

    def respond(self, user: str, message: str) -> str:
        # Get user profile for personalized advice
        profile_context = ""
        try:
            from tools.db import get_session, UserProfile
            from sqlmodel import select
            
            with get_session() as s:
                profile = s.exec(select(UserProfile).where(UserProfile.user == user)).first()
                if profile:
                    bmi_display = f"{profile.bmi:.1f}" if profile.bmi is not None else "unknown"
                    profile_context = f"""
User Profile Context:
- Age: {profile.age}, Gender: {profile.gender}
- Fitness Level: {profile.fitness_experience}
- Primary Goal: {profile.primary_goal}
- Activity Level: {profile.activity_level}
- BMI: {bmi_display}
- Health Conditions: {profile.health_conditions or 'none'}
"""
        except Exception:
            pass
        
        # Try to retrieve relevant fitness context from fitness-specific knowledge bases
        context_docs = ""
        try:
            from tools.rag import search_fitness
            context_docs = "\n".join(search_fitness(message))
        except Exception:
            context_docs = "No additional context available."
        
        prompt = (
            f"You are a fitness coach. User says: '{message}'\n\n"
            f"{profile_context}\n"
            f"Context: {context_docs}\n\n"
            f"Give a concise, actionable response (2-3 sentences max). "
            f"Be specific and encouraging. Tailor to their fitness level and goals. "
            f"Focus on safety and proper form."
        )
        
        reply = client.chat.completions.create(
            model=settings.CHAT_MODEL,
            messages=[{"role": "user", "content": prompt}]
        ).choices[0].message.content

        reply = f"🏋️ *[Fitness Coach]*\n{reply}"

        # Try to log workout entry
        try:
            with get_session() as s:
                s.add(Workout(user=user, description=message.strip()))
                s.commit()
        except Exception:
            pass

        return reply