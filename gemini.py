from google import genai
from google.genai.types import Tool, GenerateContentConfig, GoogleSearch
from agent import browser_use_loop
from tools import browser_tool


client = genai.Client(api_key="AIzaSyC8yn4F2aKOLpOef0gALTfCTG7afF227mw")

gemini = client.chats.create(
        model="gemini-2.0-flash", 
        config=GenerateContentConfig(
            tools=[browser_tool],
        )
    )

while True: 
    prompt = input("USER >> ")
    if prompt.lower() == "exit":
        print("Exiting...")
        break
    
    response = gemini.send_message(prompt)
    if(response.candidates[0].content.parts[0].function_call):
        function_call = response.candidates[0].content.parts[0].function_call
        print(f"{function_call.name} has been triggered")
        result = browser_use_loop(function_call.args["userquery"])
        
    else: print("GEMINI >> ", response.text)