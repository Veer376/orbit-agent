"""Defines the Browser Action Executor Agent."""

from google.adk.agents import LlmAgent
from pydantic import BaseModel, Field
from typing import Optional
from .. import GEMINI_MODEL  # Changed import to get from parent package
from ..tools import click_tool, type_tool, scroll_tool, keypress_tool
from ..schema import BrowserActionInput, BrowserActionOutput

# --- Agent Definition --- #

browser_action_executor_agent = LlmAgent(
    name="BrowserActionExecutorAgent",
    description="Analyzes a screenshot and a semantic action description to determine precise parameters (like coordinates) and executes low-level browser actions.",
    model=GEMINI_MODEL, # MUST be a multimodal model capable of vision
    instruction=(
        "You are a browser interaction specialist. You receive a structured action request with a specific action_type "
        "('click', 'type_text', 'scroll', or 'keypress') and a detailed target element description. "
        "You MUST analyze the current screenshot that is automatically passed to you as part of the conversation history. "
        "Using your vision capabilities, carefully locate the target element described in the input. "
        "\n\n"
        "Based on the action_type, perform the following:\n"
        "- For 'click': Find the exact (x,y) coordinates of the target element and call click_element tool.\n"
        "- For 'type_text': Locate the input field and call type_text tool with the provided text_to_type.\n"
        "- For 'scroll': Determine the appropriate direction and amount to scroll, then call scroll_page tool.\n"
        "- For 'keypress': Call press_keys tool with the specified keys_to_press.\n"
        "\n"
        "Be very precise in identifying the correct elements based on the visual information. "
        "Your job is purely execution-focused - you don't need to decide what action to take, just how to perform it accurately."
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
