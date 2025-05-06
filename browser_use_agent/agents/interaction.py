"""Defines the Human Interaction Agent."""

from google.adk.agents import LlmAgent
from pydantic import BaseModel, Field
from typing import List, Optional
from .. import GEMINI_MODEL  # Changed import to get from parent package
# Import the user input tool (will be defined later)
from ..tools import get_user_input_tool
from ..schema import HumanInteractionInput

# --- Agent Definition --- #

human_interaction_agent = LlmAgent(
    name="HumanInteractionAgent",
    description="Interacts with the human user to gather necessary information when the browser agent is stuck.",
    model=GEMINI_MODEL, # Can be a simpler model
    instruction=(
        "You are an assistant helping a browser automation agent. The agent needs input from the human user. "
        "You will receive the reason and the specific information required. "
        "Use the 'get_user_input' tool to ask the user for each piece of required information. Construct clear prompts for the user. "
        "Once you have gathered all the required information, your task is complete. The information will be automatically saved to the state for the other agent to use. "
        "If a specific prompt is provided in the input, use that directly with the 'get_user_input' tool."
    ),
    input_schema=HumanInteractionInput,
    tools=[
        get_user_input_tool,
    ],
    # This agent's job is just to get input and finish, update state via tool/callback if needed
    disallow_transfer_to_parent=True,
    disallow_transfer_to_peers=True,
)
