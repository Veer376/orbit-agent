from google.genai import types
import re
import json

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

