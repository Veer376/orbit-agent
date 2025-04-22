"""Defines the Browser Action Executor Agent."""

from google.adk.agents import LlmAgent
from pydantic import BaseModel, Field
from typing import Optional
from . import GEMINI_MODEL
from ..tools import click_tool, type_tool, scroll_tool, keypress_tool
from ..schema import BrowserActionInput, BrowserActionOutput

# --- Agent Definition --- #

browser_action_executor_agent = LlmAgent(
    name="BrowserActionExecutorAgent",
    description="Analyzes a screenshot and a semantic action description to determine precise parameters (like coordinates) and executes low-level browser actions.",
    model=GEMINI_MODEL, # MUST be a multimodal model capable of vision
    instruction=(
        "You are a browser interaction specialist. You receive a semantic action (like 'click', 'type', 'scroll'), a description of the target element, and potentially text to type. "
        "You MUST analyze the provided screenshot (path in state) using your vision capabilities to locate the target element described. "
        "Based on the visual location, determine the exact parameters needed for the low-level browser tool (e.g., x, y coordinates for 'click_at', text for 'type_text'). "
        "Call the appropriate low-level tool (`click_at`, `type_text`, `scroll_page`) with the precise parameters you determined. "
        "Be accurate in identifying the element based on the description and screenshot."
    ),
    input_schema=BrowserActionInput, # Define how the Coordinator calls this agent
    tools=[
        click_tool,
        type_tool,
        scroll_tool,
        keypress_tool,
        # Add other browser action tools here as needed
    ],
    
    # This agent should only execute the requested action, so disable transfers
    disallow_transfer_to_parent=True,
    disallow_transfer_to_peers=True,
)
