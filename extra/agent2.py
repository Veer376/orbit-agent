from google.genai import types
from tools import click_tool, type_tool
from PIL import Image

def browser_use_agent(content, browser_instance, client):
    
    browser_agent = client.chats.create(
        model="gemini-2.0-flash", 
        config=types.GenerateContentConfig(
            tools=[click_tool, type_tool],
            system_instruction = """
                You are a browser automation agent. Your goal is to complete tasks using web interfaces.
                ALWAYS use the provided functions rather than explaining how to perform actions.
                When analyzing a page, first identify relevant elements, then call the appropriate function. """
            ),
    )
    browser_agent_response = browser_agent.send_message(content)
    
    while browser_agent_response.candidates[0].content.parts[0].function_call:
        function_call = browser_agent_response.candidates[0].content.parts[0].function_call
        print(f"    BROWSER_USE_AGENT >> '{function_call.name}' has been triggered")
                
        print("Action to be performed")
        image = types.Part(
            inline_data=types.Blob(
                mime_type="image/png",
                data=browser_instance.page.screenshot()
            )
        )
        function_response_part = types.Part(
            function_response=types.FunctionResponse(
                name=function_call.name,
                response={
                    "execution_status": "success",
                    "message": "action_result_message",
                    "current_view": image  # Optional, or regenerate fresh screenshot
                }   
            )
        )
        browser_agent_response = browser_agent.send_message([function_response_part])
    
    print('Done.')
    