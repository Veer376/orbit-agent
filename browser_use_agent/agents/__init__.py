"""Exposes the agents defined in this sub-package."""

from .coordinator import browser_coordinator_agent
from .executor import browser_action_executor_agent
from .interaction import human_interaction_agent

# expose the agents for easy import
__all__ = [
    "browser_coordinator_agent",
    "browser_action_executor_agent",
    "human_interaction_agent",
]

import os

GEMINI_MODEL = os.getenv("GEMINI_MODEL")
if GEMINI_MODEL is None:
    # You might want to default to a specific model instead of raising an error,
    # depending on your application's needs.
    # For example:
    # GEMINI_MODEL = "gemini-1.5-flash-latest"
    # print("Warning: GEMINI_MODEL environment variable not set, defaulting to gemini-1.5-flash-latest")
    raise ValueError("GEMINI_MODEL environment variable must be set.")
