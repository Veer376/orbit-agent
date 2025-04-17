from google.genai import types
from tools import click_tool, type_tool, keypress_tool, scroll_tool
from PIL import Image
from utils import screenshot, handle_action
import time
# Here are some rules: 
#                 Text typed in the text field should be ENTERED using keypress.
#                 If the text field is not selected, click on it first.
#                 If the relevant element you are looking for is not visible, try to scroll.
#                 If you are not sure about the next action, ask the user for clarification.

def browser_use_agent(contents, browser_instance, client):
    
    x = 0
    max_iterations = 10 # Safety limit
    iterations = 0
    
    while iterations < max_iterations:
        iterations += 1
        
        browser_agent = client.models.generate_content(
        model="gemini-2.0-flash", 
        config=types.GenerateContentConfig(
            tools=[click_tool, type_tool, keypress_tool, scroll_tool],
            system_instruction = """
                You a browser expert. You deduce the next action based on the user goal and the current state of the browser.
                You can perform action: click, type, keypress, scroll.
                In case of any assistance, you can ask the user for clarification.
                You are not allowed to explain how to perform actions. You should perform actions.
                You execute the action using the function call. 
                and also return the reasoning behind the action in the text part.
                example.
                USER: give me the lastest article from openai.com
                BROWSER_AGENT: going to type the openai website in the search field 
                BROWSER_AGENT: finding subsection of article or click on the website link
                BROWSER_AGENT: clicking on the menu button to find the article section.
                BROWSER_AGENT: scrolling down to find the article section.
                BROWSER_AGENT: clicking on the article section.
                BROWSER_AGENT: clicking on the lastest article link.
                BROSWER_AEGNT: got the text from the lastest article published on the page.
                BROWSER_AEGNT: here is the text from the lastest article published on the page.
                USER: thank you.
                """
            ),
            contents = contents
        )
        
        if not browser_agent.candidates or not browser_agent.candidates[0].content.parts:
             print("   BROWSER_AGENT >> Model returned empty response. Asking user.")
             break # Break to potentially ask user
        
        if browser_agent.candidates[0].content.parts[0].function_call:
            function_call = browser_agent.candidates[0].content.parts[0].function_call
            print(f"    BROWSER_AGENT >> '{function_call.name}' has been triggered")

            contents.append(browser_agent.candidates[0].content)
            
            action_success = False
            error_message = None
            image = None # Initialize image
            
            try:
                # Execute the action
                handle_action(function_call, browser_instance.page)
                action_success = True
                print(f"    BROWSER_AGENT >> Action '{function_call.name}' executed.")

                # Capture state *after* action
                browser_instance.page.screenshot(path=f"screenshot_{x}.png") # Use iteration/unique names
                x+=1
                image = screenshot(browser_instance)

            except Exception as e:
                print(f"    BROWSER_AGENT >> ERROR executing action '{function_call.name}': {e}")
                error_message = str(e)
                # Capture state even after error if possible
                try:
                   image = screenshot(browser_instance)
                except Exception as screenshot_e:
                   print(f"    BROWSER_AGENT >> ERROR taking screenshot after action error: {screenshot_e}")


            function_response_content = {}
            if action_success:
                 function_response_content["message"] = "Executed the Action successfully"
                 if image: function_response_content["current_view_after_execution"] = image
            else:
                 function_response_content["error"] = f"Action failed: {error_message}"
                 if image: function_response_content["current_view_after_error"] = image # Use different key maybe


            contents.append(
                types.Content(
                    role="function",
                    parts=[  # Ensure parts is a list
                        types.Part(
                            function_response=types.FunctionResponse(
                                name=function_call.name,
                                response=function_response_content
                            )
                        )
                    ]
                )
            )
            time.sleep(3)
        else: 
            print(f"    BROWSER_AGENT >> {browser_agent.candidates[0].content.parts[0].text}")
            contents.append(browser_agent.candidates[0].content)
            
            contents.append(
                types.Content(
                    role="user",
                    parts=[
                        types.Part(text=input("    USER >> "))
                    ]
                )
            )
        
        if iterations >= max_iterations:
            print("    BROWSER_AGENT >> Max iterations reached set by the user.")
            return f"Max iterations reached set by the user. History: {contents} Provide the user with the next steps."

        
    final_agent_response = ""
    if browser_agent.candidates and browser_agent.candidates[0].content.parts and hasattr(browser_agent.candidates[0].content.parts[0], 'text'):
         final_agent_response = browser_agent.candidates[0].content.parts[0].text
         
    print(f"    BROWSER_AGENT >> Final response: '{final_agent_response}'")
    return f"Agent loop finished. Final Agent Response: '{final_agent_response}'. Review contents for full history." # Adjusted return

