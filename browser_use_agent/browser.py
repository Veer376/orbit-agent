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


def screenshot(browser_controller: BrowserController) -> types.Part: # Changed input type hint
    #HARDCODED FOR NOW - Consider getting from browser_controller.page.viewport_size
    width = 1024
    height = 768

    image_stream = io.BytesIO(browser_controller.page.screenshot()) # Use browser_controller
    img = Image.open(image_stream)
    # img = img.convert('L') # Keep color for better model interpretation? Test this.

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
                mime_type="image/png", # Changed mime_type
                data=output_bytes
            )
        )

    return part

def handle_action(function_call, page: Page): # page type hint added
    """
    Handle the action based on its type and parameters.
    """
    action = function_call.name
    args = function_call.args

    print(f"    ACTION_HANDLER >> Handling action: {action} with args: {args}") # Added general log

    if action == "click":
        x = args.get("points", {}).get("x")
        y = args.get("points", {}).get("y")
        label = args.get('label', '[no label provided]') # Default label
        if x is None or y is None:
             print(f"    ACTION_HANDLER >> ERROR: Missing coordinates for click action.")
             # Optionally raise an error or return a failure status
             return

        # button = action.get("button", "left") # Assuming left click is default
        x_orig, y_orig = correct_coordinates(x=x, y=y)
        print(f"    ACTION_HANDLER >> Clicking at model coords ({x},{y}), page coords ({x_orig:.1f},{y_orig:.1f}), label: '{label}'")
        try:
            page.mouse.click(x_orig, y_orig, button="left", timeout=5000) # Add timeout
            page.wait_for_timeout(500) # Small delay after click
        except Exception as e:
            print(f"    ACTION_HANDLER >> ERROR clicking: {e}")
            # Optionally raise or return failure

    elif action == "type":
        text = args.get("text")
        field_label = args.get("label", "[no label provided]") # Default label
        if text is None:
             print(f"    ACTION_HANDLER >> ERROR: Missing text for type action.")
             # Optionally raise an error or return a failure status
             return
        # selector = action.get("selector") # Consider if selector is needed
        print(f"    ACTION_HANDLER >> Typing text: '{text}' (intended field: '{field_label}')")
        try:
            page.keyboard.type(text, delay=50, timeout=10000) # Add delay and timeout
            page.wait_for_timeout(200) # Small delay after typing
        except Exception as e:
            print(f"    ACTION_HANDLER >> ERROR typing: {e}")
            # Optionally raise or return failure

    elif action == "scroll":
        # Scrolling often doesn't need precise coords, direction/amount is better
        # Keeping coords for now based on original code
        x = args.get("x")
        y = args.get("y")
        direction = args.get("direction", "down") # Add directionality
        amount = args.get("amount", 500) # Add scroll amount

        if x is not None and y is not None:
            x_orig, y_orig = correct_coordinates(x=x, y=y)
            print(f"    ACTION_HANDLER >> Moving mouse to scroll target: ({x_orig:.1f},{y_orig:.1f})")
            page.mouse.move(x_orig, y_orig)
            # Add actual scroll after moving mouse?
            print(f"    ACTION_HANDLER >> Scrolling {direction} by approx {amount} pixels")
            scroll_delta_y = amount if direction == "down" else -amount
            page.mouse.wheel(0, scroll_delta_y)

        else:
             # Default scroll if no coords
             print(f"    ACTION_HANDLER >> Scrolling {direction} by approx {amount} pixels")
             scroll_delta_y = amount if direction == "down" else -amount
             page.mouse.wheel(0, scroll_delta_y)

        page.wait_for_timeout(500) # Delay after scroll

    elif action == "keypress":
        keys = args.get("keys")
        if not keys:
             print(f"    ACTION_HANDLER >> ERROR: Missing keys for keypress action.")
             # Optionally raise an error or return a failure status
             return

        # Ensure keys is a list
        if not isinstance(keys, list):
            keys = [keys]

        for key in keys:
            # Map common names to Playwright keys if needed
            pw_key = key
            if key.lower() == "enter":
                pw_key = "Enter"
            # Add other mappings like "tab", "esc", etc. if needed

            print(f"    ACTION_HANDLER >> Pressing key: '{pw_key}'")
            try:
                page.keyboard.press(pw_key, timeout=5000) # Add timeout
                # Add delay based on key? e.g., longer after Enter
                if pw_key == "Enter":
                    page.wait_for_timeout(1500) # Longer wait after Enter
                else:
                    page.wait_for_timeout(200)
            except Exception as e:
                 print(f"    ACTION_HANDLER >> ERROR pressing key '{pw_key}': {e}")
                 # Optionally raise or return failure
    else:
        print(f"    ACTION_HANDLER >> WARNING: Unknown action type '{action}'")
        # Optionally raise an error for unknown actions
