from tools.db import get_session, Meal, Workout
from sqlmodel import select
from openai import OpenAI
from app.config import settings

client = OpenAI(api_key=settings.OPENAI_API_KEY)

class TrackingAgent:
    """Aggregates meals and workouts for progress summaries with intelligent insights."""

    def summarize(self, user: str) -> str:
        try:
            with get_session() as s:
                meals = s.exec(select(Meal).where(Meal.user == user)).all()
                workouts = s.exec(select(Workout).where(Workout.user == user)).all()
            
            total_meals = len(meals)
            total_workouts = len(workouts)
            
            # Get recent activity details for better insights
            recent_meals = [meal.description for meal in meals[-5:]] if meals else []
            recent_workouts = [workout.description for workout in workouts[-5:]] if workouts else []
            
            # Get user profile for personalized insights
            profile_context = ""
            try:
                from tools.db import UserProfile
                profile = s.exec(select(UserProfile).where(UserProfile.user == user)).first()
                if profile:
                    profile_context = f"""
User Profile:
- Primary Goal: {profile.primary_goal}
- Activity Level: {profile.activity_level}
- Daily Calorie Goal: {profile.daily_calorie_goal}
"""
            except Exception:
                pass
            
            # Get relevant tracking insights from tracking-specific knowledge base
            context_docs = ""
            try:
                from tools.rag import search_tracking
                context_docs = "\n".join(search_tracking("health tracking progress visualization metrics"))
            except Exception:
                context_docs = "No additional context available."
            
            # Generate intelligent summary with insights
            prompt = (
                f"You are a health tracking analyst. Generate insights for this user:\n\n"
                f"{profile_context}\n"
                f"Activity Summary:\n"
                f"- Total meals logged: {total_meals}\n"
                f"- Total workouts logged: {total_workouts}\n"
                f"- Recent meals: {recent_meals}\n"
                f"- Recent workouts: {recent_workouts}\n\n"
                f"Context: {context_docs}\n\n"
                f"Provide a concise progress summary with actionable insights (2-3 sentences). "
                f"Focus on patterns, achievements, and gentle recommendations for improvement."
            )
            
            reply = client.chat.completions.create(
                model=settings.CHAT_MODEL,
                messages=[{"role": "user", "content": prompt}]
            ).choices[0].message.content
            
            return f"📊 *[Progress Tracker]*\n{reply}"
            
        except Exception as e:
            # Database not available
            return f"📊 *[Progress Tracker]*\nDatabase not available. Unable to provide tracking summary at the moment."
