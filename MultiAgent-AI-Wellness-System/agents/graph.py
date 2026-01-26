# DEPRECATED: This file has been replaced by orchestrator.py
# LangGraph dependency has been removed from the system
# All functionality is now handled by the custom orchestrator

# For backward compatibility, redirect to orchestrator
from agents.orchestrator import WellnessOrchestrator, run_agent

# Legacy class for any remaining imports
class GraphState:
    """DEPRECATED: Legacy class for backward compatibility"""
    def __init__(self):
        self.user = ""
        self.messages = []

# Legacy function for any remaining imports  
def build_graph():
    """DEPRECATED: Returns None as LangGraph is no longer used"""
    return None
