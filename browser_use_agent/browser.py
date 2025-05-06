from playwright.sync_api import sync_playwright, Page, Browser, Playwright
from google.genai import types
import io
from PIL import Image
import time # Added for handle_action

# Assuming correct_coordinates remains in the global utils
from .utils import correct_coordinates

class BrowserController:
    def __init__(self, viewport_width=1024, viewport_height=768):
        try:
            self.viewport_width = viewport_width
            self.viewport_height = viewport_height
            self.playwright: Playwright = sync_playwright().start()
            self.browser: Browser = self.playwright.chromium.launch(
                headless=False, # Keep False for debugging, True for headless
                chromium_sandbox=True,
                env={},
                args=["--disable-extensions", "--disable-file-system"]
            )
            self.page: Page = self.browser.new_page()
            self.page.set_viewport_size({"width": viewport_width, "height": viewport_height})
            print("    BROWSER_CONTROLLER >> Browser initialized.") # Updated print prefix

        except Exception as e:
            print(f"    BROWSER_CONTROLLER >> Error during browser initialization: {e}") # Updated print prefix
            # Attempt cleanup if partial initialization occurred
            if hasattr(self, 'browser') and self.browser:
                self.browser.close()
            if hasattr(self, 'playwright') and self.playwright:
                self.playwright.stop()
            raise # Re-raise the exception

    def navigate(self, url: str):
        try:
            self.page.goto(url, wait_until='load', timeout=60000) # Wait for load, reasonable timeout
            print("    BROWSER_CONTROLLER >> Navigation successful.") # Updated print prefix
        except Exception as e:
            print(f"    BROWSER_CONTROLLER >> Error navigating to {url}: {e}") # Updated print prefix
            # Decide how to handle navigation errors (e.g., raise, return status)

    def close(self):
        print("    BROWSER_CONTROLLER >> Closing browser controller...") # Updated print prefix
        try:
            if hasattr(self, 'browser') and self.browser:
                self.browser.close()
                print("    BROWSER_CONTROLLER >> Browser closed.") # Updated print prefix
            if hasattr(self, 'playwright') and self.playwright:
                self.playwright.stop()
                print("    BROWSER_CONTROLLER >> Playwright stopped.") # Updated print prefix
        except Exception as e:
            print(f"    BROWSER_CONTROLLER >> Error during closing: {e}") # Updated print prefix

    def screenshot(self) -> types.Part:
        """
        Take a screenshot of the current browser page and return it as a Part object
        compatible with Google's Gemini model.
        
        Returns:
            types.Part: A Part object containing the screenshot as inline data.
        """
        print("    BROWSER_CONTROLLER >> Taking screenshot.")
        
        try:
            # Use the actual viewport dimensions from the class
            width = self.viewport_width
            height = self.viewport_height
            
            image_stream = io.BytesIO(self.page.screenshot())
            img = Image.open(image_stream)
            # img = img.convert('L') # Keep color for better model interpretation
            
            # Optional resizing (consider if needed for performance vs. model accuracy)
            # scale_factor = min(640 / width, 640 / height)
            # new_width = int(width * scale_factor)
            # new_height = int(height * scale_factor)
            # img = img.resize((new_width, new_height))
            
            output_stream = io.BytesIO()
            # Use PNG for lossless quality, JPEG if size is critical
            img.save(output_stream, format="PNG")
            output_bytes = output_stream.getvalue()
            
            part = types.Part(
                inline_data=types.Blob(
                    mime_type="image/png",
                    data=output_bytes
                )
            )
            
            print("    BROWSER_CONTROLLER >> Screenshot captured successfully.")
            return part
            
        except Exception as e:
            print(f"    BROWSER_CONTROLLER >> Error taking screenshot: {e}")
            raise

    def click(self, x: float, y: float, label: str = None, button: str = "left", timeout: int = 5000, delay_after: int = 500):
        """
        Click at the specified coordinates.
        
        Args:
            x: X-coordinate in model scale (0-1000)
            y: Y-coordinate in model scale (0-1000)
            label: Optional label for logging/debugging
            button: Mouse button to click ("left", "middle", "right")
            timeout: Timeout for the click operation in ms
            delay_after: Time to wait after click in ms
            
        Returns:
            bool: True if successful, False otherwise
        """
        label = label or '[no label provided]'
        print(f"    BROWSER_CONTROLLER >> Clicking at model coords ({x},{y}), label: '{label}'")
        
        try:
            # Convert from model coordinates (0-1000 scale) to actual page coordinates
            x_orig, y_orig = correct_coordinates(x=x, y=y)
            print(f"BROWSER_CONTROLLER >> Converted to page coords ({x_orig:.1f},{y_orig:.1f})")
            
            # Execute the click
            self.page.mouse.click(x_orig, y_orig, button=button, timeout=timeout)
            self.page.wait_for_timeout(delay_after)
            return True
        except Exception as e:
            print(f"    BROWSER_CONTROLLER >> ERROR clicking: {e}")
            return False
    
    def scroll(self, direction: str = "down", amount: int = 500, x: float = None, y: float = None, delay_after: int = 500):
        """
        Scroll the page in the specified direction.
        
        Args:
            direction: Direction to scroll ("up" or "down")
            amount: Amount to scroll in pixels
            x: Optional X-coordinate to position mouse before scrolling (model scale 0-1000)
            y: Optional Y-coordinate to position mouse before scrolling (model scale 0-1000)
            delay_after: Time to wait after scroll in ms
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Position mouse if coordinates provided
            if x is not None and y is not None:
                x_orig, y_orig = correct_coordinates(x=x, y=y)
                print(f"    BROWSER_CONTROLLER >> Moving mouse to scroll target: ({x_orig:.1f},{y_orig:.1f})")
                self.page.mouse.move(x_orig, y_orig)
            
            # Calculate scroll delta based on direction
            scroll_delta_y = amount if direction == "down" else -amount
            print(f"    BROWSER_CONTROLLER >> Scrolling {direction} by approx {amount} pixels")
            
            # Execute scroll
            self.page.mouse.wheel(0, scroll_delta_y)
            self.page.wait_for_timeout(delay_after)
            return True
        except Exception as e:
            print(f"    BROWSER_CONTROLLER >> ERROR scrolling: {e}")
            return False

    def type_text(self, text: str, label: str = None, delay: int = 50, timeout: int = 10000, delay_after: int = 200):
        """
        Type the specified text.
        
        Args:
            text: The text to type
            label: Optional label for logging/debugging
            delay: Delay between keystrokes in ms
            timeout: Timeout for the typing operation in ms
            delay_after: Time to wait after typing in ms
            
        Returns:
            bool: True if successful, False otherwise
        """
        label = label or '[no field label provided]'
        print(f"    BROWSER_CONTROLLER >> Typing text: '{text}' (intended field: '{label}')")
        
        try:
            self.page.keyboard.type(text, delay=delay, timeout=timeout)
            self.page.wait_for_timeout(delay_after)
            return True
        except Exception as e:
            print(f"    BROWSER_CONTROLLER >> ERROR typing: {e}")
            return False
            
    def press_keys(self, keys, delay_after: int = 200):
        """
        Press keyboard keys.
        
        Args:
            keys: Single key or list of keys to press
            delay_after: Time to wait after key press in ms
            
        Returns:
            bool: True if successful, False otherwise
        """
        # Ensure keys is a list
        if not isinstance(keys, list):
            keys = [keys]
            
        try:
            for key in keys:
                # Map common names to Playwright keys if needed
                pw_key = key
                if key.lower() == "enter":
                    pw_key = "Enter"
                elif key.lower() == "tab":
                    pw_key = "Tab"
                elif key.lower() == "escape" or key.lower() == "esc":
                    pw_key = "Escape"
                
                print(f"    BROWSER_CONTROLLER >> Pressing key: '{pw_key}'")
                self.page.keyboard.press(pw_key, timeout=5000)
                
                # Add delay based on key? e.g., longer after Enter
                if pw_key == "Enter":
                    self.page.wait_for_timeout(1500)
                else:
                    self.page.wait_for_timeout(delay_after)
            return True
        except Exception as e:
            print(f"    BROWSER_CONTROLLER >> ERROR pressing keys: {e}")
            return False

# Keep the standalone function for backward compatibility but make it use the class method
def screenshot(browser_controller: BrowserController) -> types.Part:
    """
    Legacy function that calls the BrowserController's screenshot method.
    Kept for backward compatibility.
    
    Args:
        browser_controller: The BrowserController instance
        
    Returns:
        types.Part: A Part object containing the screenshot as inline data.
    """
    return browser_controller.screenshot()

def handle_action(function_call, browser_controller: BrowserController):
    """
    Handle the action based on its type and parameters, using the BrowserController methods.
    
    Args:
        function_call: The function call object with name and args
        browser_controller: The BrowserController instance
        
    Returns:
        bool: True if the action was successful, False otherwise
    """
    action = function_call.name
    args = function_call.args

    print(f"    ACTION_HANDLER >> Handling action: {action} with args: {args}")

    if action == "click":
        x = args.get("points", {}).get("x")
        y = args.get("points", {}).get("y")
        label = args.get('label')
        
        if x is None or y is None:
             print(f"    ACTION_HANDLER >> ERROR: Missing coordinates for click action.")
             return False
        
        # Use the BrowserController click method
        return browser_controller.click(x, y, label)
        
    elif action == "type":
        text = args.get("text")
        field_label = args.get("label")
        
        if text is None:
             print(f"    ACTION_HANDLER >> ERROR: Missing text for type action.")
             return False
        
        # Use the BrowserController type_text method
        return browser_controller.type_text(text, field_label)
        
    elif action == "scroll":
        x = args.get("points", {}).get("x") if args.get("points") else None
        y = args.get("points", {}).get("y") if args.get("points") else None
        direction = args.get("direction", "down")
        amount = args.get("amount", 500)
        
        # Use the BrowserController scroll method
        return browser_controller.scroll(direction, amount, x, y)
        
    elif action == "keypress":
        keys = args.get("keys")
        
        if not keys:
             print(f"    ACTION_HANDLER >> ERROR: Missing keys for keypress action.")
             return False
        
        # Use the BrowserController press_keys method
        return browser_controller.press_keys(keys)
        
    else:
        print(f"    ACTION_HANDLER >> WARNING: Unknown action type '{action}'")
        return False
