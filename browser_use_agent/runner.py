"""Initializes and runs the Browser Loop Agent with proper state management."""

import os
import traceback
from typing import List, Optional, Dict, Any
from google.genai import types
from google.adk.runners import Runner
from google.adk.sessions.in_memory_session_service import InMemorySessionService
from google.adk.events.event import Event

# Import our agents and browser controller
from .agent import browser_loop_agent
from .browser import BrowserController
# Import the global browser controller reference
from .globals import BROWSER_CONTROLLER
from .globals import check_browser_controller

def run_browser_agent(
    user_goal: str,
    initial_url: str,
    api_key: Optional[str] = None,
    max_iterations: int = 10,
    additional_state: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Initializes and runs the browser agent with state management.
    
    Args:
        user_goal: The user's intended goal for browser automation
        initial_url: The starting URL to navigate to
        api_key: Google API key (optional, ADK will use environment variable by default)
        max_iterations: Maximum iteration limit for the loop agent
        additional_state: Any additional state values to initialize the session with
        
    Returns:
        Dict containing final_result (str), success (bool), and events (list)
    """
    global BROWSER_CONTROLLER
    
    # Initialize browser
    browser_controller = None
    result = {
        "success": False,
        "final_result": "",
        "events": [],
        "error": None
    }
    
    try:
        # Initialize browser
        print("[INFO] Initializing browser controller")
        browser_controller = BrowserController()
        BROWSER_CONTROLLER = browser_controller  # Store in global variable for tools to access
        
        # Call our diagnostic function to check BROWSER_CONTROLLER status in runner.py
        print("[RUNNER] Checking BROWSER_CONTROLLER after initialization:")
        check_browser_controller()
        
        if BROWSER_CONTROLLER: print("[INFO] Browser controller initialized successfully")
        else: print("[ERROR] Browser controller initialization failed")
        
        # Navigate to initial URL
        print(f"[INFO] Navigating to initial URL: {initial_url}")
        browser_controller.navigate(initial_url)
        
        # Take initial screenshot - now using the method directly from browser_controller
        initial_screenshot_part = browser_controller.screenshot()
        print("[INFO] Captured initial screenshot")
        
        # Prepare initial state - DON'T store browser_controller directly
        initial_state = {
            "has_browser_instance": True,
            "user_goal": user_goal,
            "iteration_count": 0,
            "max_iterations": max_iterations,
            "task_completed": False,
            "task_failed": False,
            "exit_loop": False,
            "current_screenshot": initial_screenshot_part.inline_data
        }
        
        # Add any additional state provided
        if additional_state:
            initial_state.update(additional_state)
        
        # Set up ADK runner and session
        session_service = InMemorySessionService()
        session = session_service.create_session(
            app_name="BrowserAutomationAgent",
            user_id="user",
            state=initial_state
        )
        
        # Create initial message with user goal and screenshot
        initial_message = types.Content(
            role='user',
            parts=[
                types.Part(text=f"Goal: {user_goal}\n\nI am showing you a screenshot of the current web page. Please analyze this screenshot carefully to understand the page layout and available interactive elements before taking any action."),
                initial_screenshot_part  # Use the Part object directly
            ]
        )
        
        # Create runner
        runner = Runner(
            app_name="BrowserAutomationAgent", 
            agent=browser_loop_agent,
            session_service=session_service
        )
        
        # Collect all response events
        response_events = []
        try:
            for event in runner.run(
                user_id=session.user_id,
                session_id=session.id,
                new_message=initial_message,
            ):
                # print("EVENT : ", event)
                response_events.append(event)
                
                if event.content and event.content.parts:
                    for part in event.content.parts:
                            print(f"[EVENT][{event.author}]: \n       [PART]: {part.text}\n")
            
            # Retrieve final session state
            final_session = session_service.get_session(
                app_name="BrowserAutomationAgent",
                user_id="user",
                session_id=session.id
            )
            final_state = final_session.state
            
            task_completed = final_state.get('task_completed', False)
            task_failed = final_state.get('task_failed', False)
            max_iterations_reached = final_state.get('max_iterations_reached', False)
            
            result["success"] = task_completed and not task_failed
            
            final_result = "Browser automation completed.\n\n"
            
            if task_completed:
                final_result += "✅ Task successfully completed.\n\n"
                final_result += f"Result: {final_state.get('task_result', 'No detailed result provided.')}\n"
                final_result += f"Reason: {final_state.get('task_completion_reason', 'No reason provided.')}\n\n"
            elif task_failed:
                final_result += "❌ Task failed to complete.\n\n"
                final_result += f"Reason: {final_state.get('task_failure_reason', 'No reason provided.')}\n"
                final_result += f"Details: {final_state.get('task_failure_details', 'No details provided.')}\n\n"
            elif max_iterations_reached:
                final_result += "⚠️ Maximum iterations reached without completion.\n\n"
            
            result["final_result"] = final_result
            result["events"] = response_events
            
        except Exception as runner_ex:
            print(f"[ERROR] Error during agent execution: {runner_ex}")
            print(f"[ERROR] {traceback.format_exc()}")
            result["error"] = f"Agent execution error: {str(runner_ex)}"
            result["final_result"] = f"Browser automation failed with error: {str(runner_ex)}"
        
        return result
    
    except Exception as e:
        print(f"[ERROR] Error initializing browser or setup: {e}")
        print(f"[ERROR] {traceback.format_exc()}")
        result["error"] = f"Setup error: {str(e)}"
        result["final_result"] = f"Browser automation failed during setup: {str(e)}"
        return result
        
    finally:
        if browser_controller is not None:
            try:
                browser_controller.close()
                print("[INFO] Browser controller closed")
            except Exception as close_ex:
                print(f"[ERROR] Error closing browser: {close_ex}")
        BROWSER_CONTROLLER = None