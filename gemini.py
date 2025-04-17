from google import genai
from google.genai import types
from google.genai.types import Tool, GenerateContentConfig
from agents import browser_use_agent
from tools import browser_tool
from browser import BrowserController
from PIL import Image
from typing import Union
from utils import screenshot

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
        
        # only function call
        print(f"GEMINI >> Activating the BROWSER_AGENT")
        browser_instance = BrowserController()
        url = "https://www.bing.com/"
        print(f"    BROWSER_AGENT >> Nativating to URL '{url}")
        browser_instance.navigate(url)
        
        contents = []
        contents = [types.Part(text = prompt), screenshot(browser_instance)]
        
        result = browser_use_agent(contents, browser_instance, client)
        
        print(f"GEMINI (BROSWER_AGENT) >> ", gemini.send_message(result).candidates[0].content.parts[0].text)
        browser_instance.close()
        
    else: print("GEMINI >> ", response.text)