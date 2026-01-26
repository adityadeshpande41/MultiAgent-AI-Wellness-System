# Agent router with improved LLM-based confidence scoring
from typing import Dict, Tuple, Optional, Literal
import json
import re

class RouterAgent:
    """Classifies user input using LLM with confidence scoring - handles both wellness and non-wellness queries properly."""
    
    def __init__(self):
        self.confidence_threshold = 0.6  # Lower threshold - only ask clarification for very unclear queries
        self.categories = {
            "fitness": "Exercise, workouts, physical activity, sports, training, gym, running, strength, cardio, muscle building",
            "nutrition": "Food, meals, eating, diet, calories, hunger, snacks, cooking, meal planning, supplements, nutritional information", 
            "health": "Medical concerns, symptoms, pain, illness, mental health, anxiety, stress, sleep issues, headaches, body aches",
            "misc": "Everything else not related to fitness, nutrition, or health - general questions, weather, time, etc."
        }

    def route_with_confidence(self, text: str) -> Tuple[str, float, Dict[str, float], Optional[str]]:
        """Route with LLM-based confidence scoring and optional clarifying question."""
        import streamlit as st
        st.write(f"🔍 ROUTER: Analyzing '{text}' with LLM confidence scoring")
        
        # Try LLM scoring first
        try:
            category, confidence, scores = self._llm_classify_with_confidence(text)
            st.write(f"🤖 ROUTER: LLM classification successful")
        except Exception as e:
            st.write(f"❌ ROUTER: LLM classification failed: {e}")
            st.write("🔄 ROUTER: Falling back to keyword-based scoring")
            category, confidence, scores = self._keyword_classify_with_confidence(text)
        
        st.write(f"📊 ROUTER: Final scores: {scores}")
        st.write(f"🎯 ROUTER: Top category: {category} (confidence: {confidence:.2f})")
        
        # Only ask for clarification if:
        # 1. It's a wellness-related query (not misc)
        # 2. AND confidence is low
        # 3. AND it's genuinely ambiguous between wellness categories
        clarifying_question = None
        
        if category != "misc" and confidence < self.confidence_threshold:
            # Check if it's genuinely ambiguous between wellness categories
            wellness_scores = {k: v for k, v in scores.items() if k != "misc"}
            if len([v for v in wellness_scores.values() if v > 0.2]) >= 2:
                st.write(f"❓ ROUTER: Low confidence ({confidence:.2f}) and ambiguous between wellness categories")
                clarifying_question = self._generate_clarifying_question(text, scores)
            else:
                st.write(f"✅ ROUTER: Low confidence but not ambiguous - routing to {category}")
        
        return category, confidence, scores, clarifying_question

    def _llm_classify_with_confidence(self, text: str) -> Tuple[str, float, Dict[str, float]]:
        """Use LLM to classify with confidence scores."""
        from openai import OpenAI
        from app.config import settings
        import streamlit as st
        
        client = OpenAI(api_key=settings.OPENAI_API_KEY)
        
        # Improved prompt that better handles non-wellness queries
        classification_prompt = f"""
Analyze this user message and provide confidence scores for each category.

User message: "{text}"

Categories:
- FITNESS: {self.categories['fitness']}
- NUTRITION: {self.categories['nutrition']}
- HEALTH: {self.categories['health']}
- MISC: {self.categories['misc']}

Instructions:
1. If the message is clearly NOT about wellness (fitness/nutrition/health), give MISC a high score (0.8-1.0)
2. If it's clearly about one wellness category, give that category a high score (0.8-1.0)
3. If it's ambiguous between wellness categories, distribute scores more evenly (0.3-0.6 each)
4. Be confident for clear cases - don't be overly cautious
5. Ensure all scores sum to approximately 1.0

Examples:
- "what is color of sky" → misc: 1.0, others: 0.0
- "what time is it" → misc: 1.0, others: 0.0  
- "how many calories in pizza" → nutrition: 0.9, others: low
- "I feel bad" → health: 0.8, others: low
- "I want to lose weight" → nutrition: 0.4, fitness: 0.4, health: 0.1, misc: 0.1 (ambiguous)
- "help me" → misc: 0.4, others: 0.2 each (genuinely unclear)

Respond with ONLY a JSON object:
{{
    "fitness": 0.0,
    "nutrition": 0.0,
    "health": 0.0,
    "misc": 0.0
}}
"""
        
        st.write("🤖 ROUTER: Requesting LLM confidence scores...")
        response = client.chat.completions.create(
            model=settings.CHAT_MODEL,
            messages=[{"role": "user", "content": classification_prompt}],
            temperature=0.1  # Low temperature for consistent scoring
        )
        
        response_text = response.choices[0].message.content.strip()
        st.write(f"📊 ROUTER: LLM response: {response_text}")
        
        # Extract and parse JSON
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if not json_match:
            raise ValueError("No JSON found in LLM response")
        
        scores = json.loads(json_match.group())
        
        # Validate scores
        if not all(isinstance(v, (int, float)) for v in scores.values()):
            raise ValueError("Invalid score types in LLM response")
        
        if not all(0 <= v <= 1 for v in scores.values()):
            raise ValueError("Scores must be between 0 and 1")
        
        # Normalize scores to sum to 1.0
        total = sum(scores.values())
        if total > 0:
            scores = {k: v/total for k, v in scores.items()}
        else:
            raise ValueError("All scores are zero")
        
        # Find top category and confidence
        top_category = max(scores.keys(), key=lambda k: scores[k])
        confidence = scores[top_category]
        
        return top_category, confidence, scores

    def _keyword_classify_with_confidence(self, text: str) -> Tuple[str, float, Dict[str, float]]:
        """Fallback keyword-based classification with confidence scoring."""
        import streamlit as st
        st.write("🔤 ROUTER: Using keyword-based fallback scoring")
        
        text_lower = text.lower()
        scores = {"fitness": 0.0, "nutrition": 0.0, "health": 0.0, "misc": 0.0}
        
        # Enhanced keyword sets
        keyword_sets = {
            "fitness": {
                "high": ["workout", "exercise", "gym", "fitness", "training", "muscle", "strength", "cardio", "sport", "run", "running", "working out"],
                "medium": ["physical", "active", "lift", "lifting", "movement", "stronger", "performance"],
                "low": ["move", "activity"]
            },
            "nutrition": {
                "high": ["food", "eat", "meal", "diet", "nutrition", "calories", "calorie", "hungry", "breakfast", "lunch", "dinner", "snack", "pizza", "cheese", "bread", "chicken", "beef", "vegetable", "fruit", "apple", "egg", "eggs", "how many calories", "calorie count", "nutritional value", "protein", "carbs", "fat"],
                "medium": ["cooking", "recipe", "weight", "lose weight", "slice", "serving", "healthy", "unhealthy"],
                "low": ["taste", "flavor"]
            },
            "health": {
                "high": ["headache", "headaches", "pain", "hurt", "sick", "illness", "doctor", "medical", "anxiety", "stress", "depression", "symptom", "symptoms", "feel bad", "feeling bad"],
                "medium": ["feeling", "ache", "sore", "mental", "mood", "health", "tired", "fatigue"],
                "low": ["bad", "uncomfortable", "weird"]
            }
        }
        
        # Non-wellness indicators (should route to misc)
        non_wellness_keywords = ["time", "weather", "color", "sky", "what is", "when is", "where is", "who is", "how old", "temperature", "date", "day", "year", "month"]
        
        # Check for non-wellness keywords first
        for keyword in non_wellness_keywords:
            if keyword in text_lower:
                scores["misc"] = 0.9
                break
        
        # If not clearly non-wellness, check wellness categories
        if scores["misc"] < 0.5:
            for category, keywords in keyword_sets.items():
                category_score = 0.0
                
                # Check for keyword matches with different confidence levels
                for keyword in keywords["high"]:
                    if keyword in text_lower:
                        category_score = max(category_score, 0.85)
                
                for keyword in keywords["medium"]:
                    if keyword in text_lower:
                        category_score = max(category_score, 0.65)
                
                for keyword in keywords["low"]:
                    if keyword in text_lower:
                        category_score = max(category_score, 0.4)
                
                scores[category] = category_score
        
        # If no category scored, default to misc with moderate confidence
        if max(scores.values()) == 0:
            scores["misc"] = 0.6
        
        # Normalize scores
        total = sum(scores.values())
        if total > 0:
            scores = {k: v/total for k, v in scores.items()}
        
        # Find top category
        top_category = max(scores.keys(), key=lambda k: scores[k])
        confidence = scores[top_category]
        
        return top_category, confidence, scores

    def _generate_clarifying_question(self, text: str, scores: Dict[str, float]) -> str:
        """Generate an intelligent clarifying question using LLM."""
        from openai import OpenAI
        from app.config import settings
        import streamlit as st
        
        try:
            client = OpenAI(api_key=settings.OPENAI_API_KEY)
            
            # Get top wellness categories for clarification (exclude misc)
            wellness_scores = {k: v for k, v in scores.items() if k != "misc" and v > 0.1}
            sorted_scores = sorted(wellness_scores.items(), key=lambda x: x[1], reverse=True)
            top_categories = [cat for cat, score in sorted_scores[:2]]
            
            if len(top_categories) < 2:
                # Not genuinely ambiguous, don't ask clarification
                return None
            
            clarification_prompt = f"""
The user said: "{text}"

This seems to be about wellness but I'm not sure if it's more about {top_categories[0]} or {top_categories[1]}.

Generate a friendly, specific clarifying question that:
1. Acknowledges their wellness goal
2. Offers 2-3 specific examples for each of the top categories
3. Is conversational and helpful
4. Is 1-2 sentences maximum

Example format: "I want to help you with [topic] - are you looking for [specific examples for category 1] or [specific examples for category 2]?"

Be specific with examples rather than just category names.
"""
            
            response = client.chat.completions.create(
                model=settings.CHAT_MODEL,
                messages=[{"role": "user", "content": clarification_prompt}],
                temperature=0.3
            )
            
            question = response.choices[0].message.content.strip()
            st.write(f"❓ ROUTER: Generated LLM clarifying question")
            return question
            
        except Exception as e:
            st.write(f"❌ ROUTER: Failed to generate LLM clarifying question: {e}")
            # Fallback clarifying question
            wellness_categories = [k for k, v in scores.items() if k != "misc" and v > 0.1]
            if len(wellness_categories) >= 2:
                return f"I want to help with your wellness goal - are you asking about {wellness_categories[0]} or {wellness_categories[1]}?"
            return None

    def classify(self, text: str) -> Literal["fitness", "nutrition", "health", "misc"]:
        """Backward compatibility method."""
        category, _, _, _ = self.route_with_confidence(text)
        return category

    def route(self, text: str):
        return self.classify(text)
