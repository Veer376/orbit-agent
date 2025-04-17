from google.genai import types
import re
import json
import io
from PIL import Image


def extract_json_from_markdown(text):
    # Pattern to match content between triple backticks
    pattern = r'```(?:json)?\n([\s\S]*?)\n```'
    match = re.search(pattern, text)
    
    if match:
        json_content = match.group(1)
        return json.loads(json_content)
    else:
        raise ValueError("Could not extract JSON from the markdown")

def correct_coordinates(x, y):
    
    model_coord_range = 1000.0

    # Calculate the scaling factor for each dimension
    x_scale_factor = 1024 / model_coord_range
    y_scale_factor = 768 / model_coord_range

    # Apply the scaling factors to the raw coordinates from the model
    x_original = x * x_scale_factor
    y_original = y * y_scale_factor

    return x_original, y_original

def screenshot(browser) -> dict:
    #HARDCODED FOR NOW
    width = 1024
    height = 768
    
    image_stream = io.BytesIO(browser.page.screenshot())
    img = Image.open(image_stream)
    img = img.convert('L')
    
    scale_factor = min(640 / width, 640 / height)
    
    new_width = int(width * scale_factor)
    new_height = int(height * scale_factor)
    
    img = img.resize((new_width, new_height))
    
    output_stream = io.BytesIO()
    img.save(output_stream, format="JPEG", quality=85)
    output_bytes = output_stream.getvalue()
    
    part = types.Part(
            inline_data=types.Blob(
                mime_type="image/jpeg",
                data=output_bytes
            )
        )
    
    return part

def handle_action(function_call, page):
    """
    Handle the action based on its type and parameters.
    """
    action = function_call.name
    args = function_call.args
    
    if action == "click":
        x = args.get("points").get("x")
        y = args.get("points").get("y")
        # button = action.get("button", "left")
        x, y = correct_coordinates(x=x, y=y)
        print(f"    BROWSER_AGENT >> clicking at coordinates: 'x={x}', 'y={y}' label: '{args.get('label')}'")
        page.mouse.click(x, y, button="left")
        
    elif action == "type":
        text = args.get("text")
        field = args.get("label")
        # selector = action.get("selector")
        print(f"    BROWSER_AGENT >> typing text: '{text}' at field: '{field}'")
        page.keyboard.type(text)
        
    elif action == "scroll":
        x = args.get("x")
        y = args.get("y")
        x, y = correct_coordinates(x=x, y=y)
        print(f"    BROWSER_AGENT >> scrolling at coordinates: 'x={x}', 'y={y}'")
        page.mouse.move(x, y)
        
    elif action == "keypress":
        keys = args.get("keys")
        for key in keys:
            if key.lower() == "enter":
                print(f"    BROWSER_AGENT >> pressing key: '{key}'")
                page.keyboard.press("Enter")
                # for testing purposes, wait for 1 second after pressing enter
                page.wait_for_timeout(1000)
        
    