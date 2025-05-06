"""Exposes the agents defined in this sub-package."""

# Import from parent package to avoid circular imports
from .. import GEMINI_MODEL

# expose the agents for easy import
__all__ = [
    "browser_coordinator_agent",
    "browser_action_executor_agent",
    "human_interaction_agent",
]

# Note: We're now importing the agents after defining __all__ to prevent circular imports
from .coordinator import browser_coordinator_agent
from .executor import browser_action_executor_agent
from .interaction import human_interaction_agent
