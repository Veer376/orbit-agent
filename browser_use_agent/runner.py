"""Initializes and runs the Browser Loop Agent with proper state management."""

import logging
import os
import traceback
from typing import List, Optional, Dict, Any
from google.genai import types
from google.adk.runners import Runner
from google.adk.sessions.in_memory_session_service import InMemorySessionService
from google.adk.events.event import Event

# Import our agents and browser controller
from .agent import browser_loop_agent
from .browser import BrowserController, screenshot

logger = logging.getLogger(__name__)

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
        api_key: Google API key (optional, defaults to environment variable)
        max_iterations: Maximum iteration limit for the loop agent
        additional_state: Any additional state values to initialize the session with
        
    Returns:
        Dict containing final_result (str), success (bool), and events (list)
    """
    # Set API key from parameter or environment
    if api_key:
        os.environ["GOOGLE_API_KEY"] = api_key

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
        logger.info("Initializing browser controller")
        browser_controller = BrowserController()
        
        # Navigate to initial URL
        logger.info(f"Navigating to initial URL: {initial_url}")
        browser_controller.navigate(initial_url)
        
        # Take initial screenshot
        initial_screenshot = screenshot(browser_controller)
        logger.info("Captured initial screenshot")
        
        # Prepare initial state
        initial_state = {
            # Store browser_controller in state for tools to access
            "browser_instance": browser_controller,
            # Store goal in state for agents to reference
            "user_goal": user_goal,
            # Track iterations for safety
            "iteration_count": 0,
            "max_iterations": max_iterations,
            # Initialize flags
            "task_completed": False,
            "task_failed": False,
            "exit_loop": False,
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
        
        # Create runner
        runner = Runner(
            app_name="BrowserAutomationAgent", 
            agent=browser_loop_agent,
            session_service=session_service
        )
        
        # Create initial contents with user goal and screenshot
        initial_content = types.Content(
            role="user",
            parts=[
                types.Part(text=f"Goal: {user_goal}"),
                initial_screenshot
            ]
        )
        
        # Collect all response events
        response_events = []
        try:
            for event in runner.run(
                user_id=session.user_id,
                session_id=session.id,
                new_message=initial_content
            ):
                # Store event for final result compilation
                response_events.append(event)
                
                # Log progress
                if event.content and event.content.parts:
                    for part in event.content.parts:
                        if hasattr(part, 'text') and part.text:
                            logger.info(f"[{event.author}]: {part.text[:100]}...")
            
            # Retrieve final session state
            final_session = session_service.get_session(
                app_name="BrowserAutomationAgent",
                user_id="user",
                session_id=session.id
            )
            final_state = final_session.state
            
            # Check for success or failure indicators
            task_completed = final_state.get('task_completed', False)
            task_failed = final_state.get('task_failed', False)
            max_iterations_reached = final_state.get('max_iterations_reached', False)
            
            # Set success flag
            result["success"] = task_completed and not task_failed
            
            # Compile final result message based on outcome
            final_result = "Browser automation completed.\n\n"
            
            if task_completed:
                final_result += "✅ Task successfully completed.\n\n"
            elif task_failed:
                final_result += "❌ Task failed to complete.\n\n"
            elif max_iterations_reached:
                final_result += "⚠️ Maximum iterations reached without completion.\n\n"
            
            # Add details from final events
            final_result += "Results:\n"
            for event in response_events:
                if event.is_final_response() and event.content and event.content.parts:
                    for part in event.content.parts:
                        if hasattr(part, 'text') and part.text:
                            final_result += part.text + "\n"
            
            result["final_result"] = final_result
            result["events"] = response_events
            
        except Exception as runner_ex:
            logger.error(f"Error during agent execution: {runner_ex}")
            logger.error(traceback.format_exc())
            result["error"] = f"Agent execution error: {str(runner_ex)}"
            result["final_result"] = f"Browser automation failed with error: {str(runner_ex)}"
        
        return result
    
    except Exception as e:
        logger.error(f"Error initializing browser or setup: {e}")
        logger.error(traceback.format_exc())
        result["error"] = f"Setup error: {str(e)}"
        result["final_result"] = f"Browser automation failed during setup: {str(e)}"
        return result
        
    finally:
        # Ensure browser is closed
        if browser_controller is not None:
            try:
                browser_controller.close()
                logger.info("Browser controller closed")
            except Exception as close_ex:
                logger.error(f"Error closing browser: {close_ex}")