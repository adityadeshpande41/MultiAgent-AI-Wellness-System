# DEPRECATED: Replaced by orchestrator.py
# This file is no longer used after removing LangGraph dependency
# See orchestrator.py for the new implementation

from agents.orchestrator import run_agent

# Maintain backward compatibility
workflow = None  # No longer needed

def run_agent_deprecated(user: str, msg: str) -> str:
    """
    DEPRECATED: Use orchestrator.run_agent instead
    Maintained for backward compatibility
    """
    return run_agent(user, msg)
