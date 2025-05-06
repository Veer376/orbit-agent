from google.adk.tools import FunctionTool
from playwright.sync_api import Page # Import Page for type hinting
from pydantic import BaseModel, Field
from typing import List, Optional

# Import the core action handler
from .browser import handle_action
from .schema import ClickArgs, TypeArgs, ScrollArgs, KeypressArgs, HumanInteractionInput
# Access to the global browser controller
from .globals import BROWSER_CONTROLLER

# --- Tool Functions ---
def click_element_wrapper(args: ClickArgs, tool_context=None):
    """Tool for clicking elements on the webpage."""
    from .globals import get_browser_controller, check_browser_controller
    
    # Diagnostic check
    print("[CLICK_TOOL] Checking BROWSER_CONTROLLER in click_element_wrapper:")
    has_controller = check_browser_controller()
    
    # Get the browser controller using the getter function
    browser_controller = get_browser_controller()
    
    if not browser_controller:
        print("[ERROR] Browser controller not available for click operation")
        return "Error: Browser controller is not available."
    
    try:
        print(f"[CLICK_TOOL] Using browser controller: {browser_controller}")
        success = browser_controller.click(
            x=args.points.x, 
            y=args.points.y,
            label=args.label
        )
        
        return f"{'Clicked' if success else 'Failed to click'} at ({args.points.x}, {args.points.y})"
    except Exception as e:
        print(f"[ERROR] Click error: {e}")
        return f"Error when clicking: {str(e)}"

def type_text_wrapper(args: TypeArgs, tool_context=None):
    """Tool for typing text into input fields on the webpage."""
    from .globals import get_browser_controller
    
    # Get the browser controller using the getter function
    browser_controller = get_browser_controller()
    
    if not browser_controller:
        print("[ERROR] Browser controller not available for type operation")
        return "Error: Browser controller is not available."
    
    try:
        success = browser_controller.type_text(
            text=args.text,
            label=args.label
        )
        
        return f"{'Typed' if success else 'Failed to type'} text: '{args.text}'"
    except Exception as e:
        print(f"[ERROR] Type text error: {e}")
        return f"Error when typing text: {str(e)}"

def scroll_page_wrapper(args: ScrollArgs, tool_context=None):
    """Tool for scrolling the webpage."""
    from .globals import get_browser_controller
    
    # Get the browser controller using the getter function
    browser_controller = get_browser_controller()
    
    if not browser_controller:
        print("[ERROR] Browser controller not available for scroll operation")
        return "Error: Browser controller is not available."
    
    # Extract coordinates if provided
    x = None
    y = None
    if args.points:
        x = args.points.x
        y = args.points.y
        
    try:
        success = browser_controller.scroll(
            direction=args.direction,
            amount=args.amount,
            x=x,
            y=y
        )
        
        return f"{'Scrolled' if success else 'Failed to scroll'} {args.direction} by {args.amount} pixels"
    except Exception as e:
        print(f"[ERROR] Scroll error: {e}")
        return f"Error when scrolling: {str(e)}"

def press_keys_wrapper(args: KeypressArgs, tool_context=None):
    """Tool for pressing keyboard keys."""
    from .globals import get_browser_controller
    
    # Get the browser controller using the getter function
    browser_controller = get_browser_controller()
    
    if not browser_controller:
        print("[ERROR] Browser controller not available for key press operation")
        return "Error: Browser controller is not available."
    
    try:
        success = browser_controller.press_keys(
            keys=args.keys
        )
        
        return f"{'Pressed' if success else 'Failed to press'} keys: {', '.join(args.keys)}"
    except Exception as e:
        print(f"[ERROR] Key press error: {e}")
        return f"Error when pressing keys: {str(e)}"

def get_user_input_wrapper(prompt: str, tool_context=None) -> str:
    """Tool for getting input from the human user."""
    print(f"[INFO] Requesting user input: {prompt}")
    
    # Print a clear separator to make the prompt stand out
    print("\n" + "="*50)
    print("👤 HUMAN INPUT REQUIRED:")
    print(prompt)
    print("="*50)
    
    # Get the user's input
    user_response = input("Your response: ")
    
    print(f"[INFO] Received user input: {user_response[:20]}{'...' if len(user_response) > 20 else ''}")
    return user_response

# Create the FunctionTool instances with the proper wrapper functions
click_tool = FunctionTool(click_element_wrapper)
type_tool = FunctionTool(type_text_wrapper)
scroll_tool = FunctionTool(scroll_page_wrapper)
keypress_tool = FunctionTool(press_keys_wrapper)
get_user_input_tool = FunctionTool(get_user_input_wrapper)

# Export the tools
__all__ = [
    'click_tool',
    'type_tool',
    'scroll_tool',
    'keypress_tool',
    'get_user_input_tool',
]
