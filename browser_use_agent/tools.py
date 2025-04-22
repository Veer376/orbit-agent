from google.adk.tools import FunctionTool
from playwright.sync_api import Page # Import Page for type hinting
from pydantic import BaseModel, Field
from typing import List, Optional
import logging

# Import the core action handler
from .browser import handle_action
from .schema import ClickArgs, TypeArgs, ScrollArgs, KeypressArgs, HumanInteractionInput

# Setup logger
logger = logging.getLogger(__name__)

# --- Tool Functions ---
def click_element(page: Page, args: ClickArgs):
    """Clicks on the page at the specified coordinates."""
    # Construct a mock function_call object for handle_action
    mock_function_call = type('obj', (object,), {
        'name': 'click',
        'args': args.model_dump() # Use Pydantic model
    })()
    handle_action(mock_function_call, page)
    return f"Clicked at ({args.points.x}, {args.points.y})" # Simple confirmation

def type_text(page: Page, args: TypeArgs):
    """Types the specified text into the currently focused element."""
    mock_function_call = type('obj', (object,), {
        'name': 'type',
        'args': args.model_dump()
    })()
    handle_action(mock_function_call, page)
    return f"Typed text: '{args.text}'"

def scroll_page(page: Page, args: ScrollArgs):
    """Scrolls the page up or down."""
    mock_function_call = type('obj', (object,), {
        'name': 'scroll',
        'args': args.model_dump()
    })()
    handle_action(mock_function_call, page)
    return f"Scrolled {args.direction} by {args.amount} pixels"

def press_keys(page: Page, args: KeypressArgs):
    """Presses the specified sequence of keys."""
    mock_function_call = type('obj', (object,), {
        'name': 'keypress',
        'args': args.model_dump()
    })()
    handle_action(mock_function_call, page)
    return f"Pressed keys: {', '.join(args.keys)}"

# --- User Interaction Tool ---
def get_user_input(prompt: str) -> str:
    """
    Prompts the user for input and returns their response.
    
    This tool allows the HumanInteractionAgent to request specific information
    from the user when the browser automation requires human intervention.
    
    Args:
        prompt: The prompt to show to the user, explaining what information is needed.
        
    Returns:
        The user's response as a string.
    """
    logger.info(f"Requesting user input: {prompt}")
    
    # Print a clear separator to make the prompt stand out
    print("\n" + "="*50)
    print("👤 HUMAN INPUT REQUIRED:")
    print(prompt)
    print("="*50)
    
    # Get the user's input
    user_response = input("Your response: ")
    
    logger.info(f"Received user input: {user_response[:20]}{'...' if len(user_response) > 20 else ''}")
    return user_response

# --- ADK Tool Definitions ---
# Wrap the Python functions into ADK FunctionTools

# Note: The standard FunctionTool doesn't automatically handle injecting
# the 'page' object. The ExecutorAgent will need custom logic (e.g., in
# a before_tool_callback or by overriding tool execution) to pass the
# 'page' object from its BrowserController instance to these functions.

click_tool = FunctionTool(func=click_element, name="click_element")
type_tool = FunctionTool(func=type_text, name="type_text")
scroll_tool = FunctionTool(func=scroll_page, name="scroll_page")
keypress_tool = FunctionTool(func=press_keys, name="press_keys")

# Add the user input tool
get_user_input_tool = FunctionTool(
    func=get_user_input,
    name="get_user_input"
)

# Export the tools
__all__ = [
    'click_tool',
    'type_tool',
    'scroll_tool',
    'keypress_tool',
    'get_user_input_tool',
]
