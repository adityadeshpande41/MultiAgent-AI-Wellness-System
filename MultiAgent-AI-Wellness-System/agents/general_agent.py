# General agent for out-of-domain queries
from openai import OpenAI
from app.config import settings

client = OpenAI(api_key=settings.OPENAI_API_KEY)

class GeneralAgent:
    """Handles queries outside fitness, nutrition, and health domains with RAG support."""

    def respond(self, message: str) -> str:
        # First, analyze if this might actually belong to one of our domains
        analysis_prompt = (
            f"Analyze this user message: '{message}'\n\n"
            "Could this message be related to:\n"
            "- FITNESS (workouts, exercise, physical activity, sports, training)\n"
            "- NUTRITION (food, meals, eating, diet, calories, hunger)\n" 
            "- HEALTH (medical concerns, symptoms, mental health, anxiety, stress, sleep)\n\n"
            "If YES, respond with just the domain name (FITNESS, NUTRITION, or HEALTH).\n"
            "If NO, respond with 'OUT_OF_DOMAIN'."
        )
        
        analysis = client.chat.completions.create(
            model=settings.CHAT_MODEL,
            messages=[{"role": "user", "content": analysis_prompt}]
        ).choices[0].message.content.strip()

        if analysis in ["FITNESS", "NUTRITION", "HEALTH"]:
            # Try to provide some relevant information using targeted RAG
            context_docs = ""
            try:
                # Use domain-specific search based on analysis
                if analysis == "FITNESS":
                    from tools.rag import search_fitness
                    context_docs = "\n".join(search_fitness(message))
                elif analysis == "NUTRITION":
                    from tools.rag import search_nutrition
                    context_docs = "\n".join(search_nutrition(message))
                elif analysis == "HEALTH":
                    from tools.rag import search_medical
                    context_docs = "\n".join(search_medical(message))
            except Exception:
                context_docs = "No additional context available."
            
            domain_map = {
                "FITNESS": "🏋️ fitness",
                "NUTRITION": "🍎 nutrition", 
                "HEALTH": "🩺 health"
            }
            
            # Provide helpful information while suggesting the correct domain
            prompt = (
                f"User asked: '{message}' which relates to {analysis.lower()}.\n\n"
                f"Context: {context_docs}\n\n"
                f"Provide a brief helpful response (1-2 sentences) and suggest they ask "
                f"the specialized {analysis.lower()} agent for more detailed help."
            )
            
            reply = client.chat.completions.create(
                model=settings.CHAT_MODEL,
                messages=[{"role": "user", "content": prompt}]
            ).choices[0].message.content
            
            reply += f"\n\nFor more detailed help, try asking the {domain_map[analysis]} specialist!"
        else:
            reply = (
                f"I'm specialized in fitness 🏋️, nutrition 🍎, and health 🩺 topics. "
                f"Your question about '{message}' seems to be outside these areas. "
                f"Could you ask me something related to workouts, meals, or health instead? "
                f"I'd be happy to help with those topics!"
            )
        
        return f"🤖 *[Domain Helper]*\n{reply}"
