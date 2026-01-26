# Custom orchestrator with confidence-based routing and clarifying questions
from typing import Dict, Any, List, Optional
import streamlit as st

from agents.router import RouterAgent
from agents.fitness_coach import FitnessCoachAgent
from agents.nutrition_specialist import NutritionAgent
from agents.doctor_avatar import DoctorAgent
from agents.tracking_viz import TrackingAgent
from agents.general_agent import GeneralAgent
from agents.api_tool_agent import APIToolAgent
from agents.clarification_agent import clarification_agent


class WellnessOrchestrator:
    """
    Custom orchestrator with confidence-based routing and intelligent clarification.
    Coordinates multiple wellness agents with smart conversation flow.
    """
    
    def __init__(self):
        # Initialize all agents
        self.router = RouterAgent()
        self.fitness = FitnessCoachAgent()
        self.nutrition = NutritionAgent()
        self.doctor = DoctorAgent()
        self.tracking = TrackingAgent()
        self.general = GeneralAgent()
        self.api_tool = APIToolAgent()
        
        # Agent mapping
        self.agents = {
            "fitness": self.fitness,
            "nutrition": self.nutrition,
            "health": self.doctor,
            "tracking": self.tracking,
            "misc": self.general
        }
    
    def process_message(self, user: str, message: str) -> str:
        """
        Main entry point for processing user messages.
        Handles confidence-based routing with intelligent clarification.
        """
        # Check if this is a response to a pending clarification
        if clarification_agent.is_clarification_response(user, message):
            return self._handle_clarification_response(user, message)
        
        # Route the message with confidence scoring
        intent, confidence, scores, clarifying_question = self.router.route_with_confidence(message)
        
        # Handle low confidence with clarifying questions or redirection
        if clarifying_question:
            if intent == "misc":
                # Unrelated query - return redirection message directly
                return clarifying_question
            else:
                # Wellness query - store pending clarification
                clarification_agent.store_pending_clarification(user, message, scores)
                return self._format_clarification_response(clarifying_question, scores)
        
        # Handle high confidence workflows
        return self._execute_agent_workflow(user, message, intent)
    
    def _handle_clarification_response(self, user: str, message: str) -> str:
        """Handle user's response to a clarification question."""
        pending = clarification_agent.get_pending_clarification(user)
        if not pending:
            return self.process_message(user, message)
        
        original_message = pending["original_message"]
        previous_scores = pending["scores"]
        
        # Try to detect intent from the clarification response
        detected_intent = clarification_agent.detect_clarification_intent(message, previous_scores)
        
        if detected_intent:
            clarification_agent.clear_pending_clarification(user)
            return self._execute_agent_workflow(user, original_message, detected_intent)
        else:
            # Still unclear, try one more time
            follow_up = clarification_agent.generate_follow_up_question(message, previous_scores)
            return f"""🤔 *[Still Need Clarification]*

{follow_up}

*Or you can try rephrasing your original question: "{original_message}"*"""
    
    def _format_clarification_response(self, clarifying_question: str, scores: Dict[str, float]) -> str:
        """Format a clarification response with confidence scores."""
        # Format the confidence scores for display
        score_display = []
        sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        for category, score in sorted_scores[:3]:  # Show top 3
            if score > 0.1:  # Only show meaningful scores
                emoji = {"fitness": "🏋️", "nutrition": "🍎", "health": "🩺", "misc": "🤖"}
                score_display.append(f"{emoji.get(category, '•')} {category.title()}: {score:.1%}")
        
        response = f"""🤔 *[Clarification Needed]*

{clarifying_question}

*My confidence scores:*
{chr(10).join(score_display)}

Please clarify so I can help you better!"""
        
        return response
    
    def _execute_agent_workflow(self, user: str, message: str, intent: str) -> str:
        """Execute the appropriate agent workflow based on intent."""
        if intent == "nutrition":
            return self._handle_nutrition_workflow(user, message)
        elif intent == "tracking":
            return self._handle_tracking_workflow(user, message)
        else:
            return self._handle_simple_workflow(user, message, intent)
    
    def _handle_nutrition_workflow(self, user: str, message: str) -> str:
        """Handle nutrition workflow with potential API lookup."""
        # Check if this needs food database lookup
        if self.api_tool.needs_food_lookup(message):
            food_items = self.api_tool.extract_food_items(message)
            food_data = self.api_tool.lookup_food(food_items)
            response = self.nutrition.respond_with_api_data(user, message, food_data)
        else:
            response = self.nutrition.respond(user, message)
        
        return response
    
    def _handle_tracking_workflow(self, user: str, message: str) -> str:
        """Handle tracking/analytics workflow."""
        return self.tracking.summarize(user)
    
    def _handle_simple_workflow(self, user: str, message: str, intent: str) -> str:
        """Handle simple single-agent workflows."""
        if intent in self.agents:
            agent = self.agents[intent]
            
            # Handle different agent interfaces
            if intent == "fitness":
                response = agent.respond(user, message)
            elif intent == "health":
                response = agent.respond(message, user)
            elif intent == "misc":
                response = agent.respond(message)
            else:
                response = agent.respond(user, message)
        else:
            # Fallback to general agent
            response = self.general.respond(message)
        
        return response


# Global orchestrator instance
orchestrator = WellnessOrchestrator()


def run_agent(user: str, msg: str) -> str:
    """
    Main function that replaces the LangGraph workflow.
    Now with confidence-based routing and clarifying questions.
    """
    return orchestrator.process_message(user, msg)