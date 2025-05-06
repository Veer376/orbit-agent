from typing import Optional, List, Literal
from pydantic import BaseModel, Field

class Point(BaseModel):
    x: float = Field(description="X-coordinate (0-1000 scale)")
    y: float = Field(description="Y-coordinate (0-1000 scale)")

class ClickArgs(BaseModel):
    label: Optional[str] = Field(description="Label of the element to click (for context)")
    points: Point = Field(description="Coordinates to click")

class TypeArgs(BaseModel):
    text: str = Field(description="Text to type")
    label: Optional[str] = Field(description="Label of the field being typed into (for context)")

class ScrollArgs(BaseModel):
    direction: Optional[str] = Field(description="Direction to scroll ('up' or 'down')")
    amount: Optional[int] = Field(description="Approximate amount to scroll in pixels")
    # Optional coordinates if scrolling needs to target a specific area first
    points: Optional[Point] = Field(description="Optional coordinates to move mouse to before scrolling")

class KeypressArgs(BaseModel):
    keys: List[str] = Field(description="List of keys to press (e.g., ['Enter'], ['Control', 'a'])")

class HumanInteractionInput(BaseModel):
    """Input schema for the HumanInteractionAgent."""
    reason: str = Field(description="The reason why human input is required (e.g., 'Login required', 'Ambiguous choice').")
    required_info: List[str] = Field(description="List of specific information needed (e.g., ['username', 'password'], ['captcha_text']).")
    prompt_override: Optional[str] = Field(description="Optional specific prompt to show the user directly.")

# --- Input Schema --- #

class BrowserActionInput(BaseModel):
    action : str = Field(description= " The type of action to perform (e.g., 'click', 'type_text', 'scroll', 'keypress').")
    action_description: str = Field(description="A description of the action to be performed. eg. type the text - 'animal movie ticket', click on the search bar, etc.")

# --- Output Schema --- #

class BrowserActionOutput(BaseModel):
    """Output schema for the BrowserActionExecutorAgent."""
    action_performed: str = Field(description="The type of action that was performed.")
    success: bool = Field(description="Whether the action was executed successfully.")
    details: str = Field(description="Additional details about the executed action.")

class TaskCompletionArgs(BaseModel):
    reason: str = Field(description="Reason why the task is considered complete")
    result: str = Field(description="Final result or output from the completed task")

class TaskFailureArgs(BaseModel):
    reason: str = Field(description="Reason why the task failed")
    details: str = Field(description="Details about what was attempted and why it failed")
