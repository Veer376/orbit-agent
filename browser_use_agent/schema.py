from pydantic import BaseModel, Field, Optional, List

class Point(BaseModel):
    x: float = Field(description="X-coordinate (0-1000 scale)")
    y: float = Field(description="Y-coordinate (0-1000 scale)")

class ClickArgs(BaseModel):
    label: Optional[str] = Field(None, description="Label of the element to click (for context)")
    points: Point = Field(description="Coordinates to click")

class TypeArgs(BaseModel):
    text: str = Field(description="Text to type")
    label: Optional[str] = Field(None, description="Label of the field being typed into (for context)")

class ScrollArgs(BaseModel):
    direction: Optional[str] = Field("down", description="Direction to scroll ('up' or 'down')")
    amount: Optional[int] = Field(500, description="Approximate amount to scroll in pixels")
    # Optional coordinates if scrolling needs to target a specific area first
    points: Optional[Point] = Field(None, description="Optional coordinates to move mouse to before scrolling")

class KeypressArgs(BaseModel):
    keys: List[str] = Field(description="List of keys to press (e.g., ['Enter'], ['Control', 'a'])")

class HumanInteractionInput(BaseModel):
    """Input schema for the HumanInteractionAgent."""
    reason: str = Field(description="The reason why human input is required (e.g., 'Login required', 'Ambiguous choice').")
    required_info: List[str] = Field(default_factory=list, description="List of specific information needed (e.g., ['username', 'password'], ['captcha_text']).")
    prompt_override: Optional[str] = Field(None, description="Optional specific prompt to show the user directly.")

# --- Input Schema --- #

class BrowserActionInput(BaseModel):
    """Input schema for the BrowserActionExecutorAgent."""
    action: str = Field(description="The type of action to perform (e.g., 'click', 'type', 'scroll').")
    target_description: Optional[str] = Field(None, description="A detailed visual description of the target element on the screenshot.")
    text_to_type: Optional[str] = Field(None, description="The text to type (only used for 'type' action).")
    scroll_direction: Optional[str] = Field(None, description="Direction to scroll ('up', 'down', 'left', 'right').")
    scroll_amount: Optional[int] = Field(None, description="Amount to scroll (e.g., pixels, percentage - depends on tool implementation). Optional.")
