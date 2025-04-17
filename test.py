
from google.genai import types
from google import genai
import PIL
from utils import extract_json_from_markdown, correct_coordinates

client = genai.Client(api_key="AIzaSyC8yn4F2aKOLpOef0gALTfCTG7afF227mw")

image = PIL.Image.open("screenshot_6.png")
browser_agent = client.models.generate_content(
        model="gemini-2.0-flash", 
        config=types.GenerateContentConfig(
            # tools=[click_tool, type_tool],
            system_instruction = """
                Return the coordinates of the point in the json format: points: {x: 0, y: 0} 
                """
            ),
        contents = ["click the bookmyshow website", image]
    )

data = browser_agent.candidates[0].content.parts[0].text
json = extract_json_from_markdown(data)

print(json)
x, y = correct_coordinates(json["point"]["x"], json["point"]["y"])
print(f"X: {x}, Y: {y}")
