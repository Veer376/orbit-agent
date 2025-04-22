"""Defines the main LoopAgent for the browser interaction capability."""

import logging
from google.adk.agents import LoopAgent
from google.adk.agents.callback_context import CallbackContext

# Import the coordinator agent
from .agents.coordinator import browser_coordinator_agent

logger = logging.getLogger(__name__)

def before_loop_iteration(callback_context: CallbackContext):
    """Callback executed before each loop iteration to track state."""
    # Get current iteration count or default to 0
    iteration_count = callback_context.state.get('iteration_count', 0)
    max_iterations = callback_context.state.get('max_iterations', 10)
    
    # Log the current iteration status
    logger.info(f"Starting loop iteration {iteration_count + 1}/{max_iterations}")
    
    # Increment the iteration count for the next iteration
    callback_context.state['iteration_count'] = iteration_count + 1
    
    # Optionally check if we should exit early (e.g., goal achieved or error condition)
    if callback_context.state.get('task_completed', False):
        logger.info("Task marked as completed. Exiting loop.")
        callback_context.state['exit_loop'] = True
    
    if callback_context.state.get('task_failed', False):
        logger.warning("Task marked as failed. Exiting loop.")
        callback_context.state['exit_loop'] = True
    
    # Check if we've hit the maximum iterations
    if iteration_count >= max_iterations:
        logger.warning(f"Reached maximum iterations ({max_iterations}). Exiting loop.")
        callback_context.state['exit_loop'] = True
        callback_context.state['max_iterations_reached'] = True

# Define the LoopAgent that orchestrates the browser task.
browser_loop_agent = LoopAgent(
    name="BrowserTaskLoop",
    description="Manages the iterative process of browser interaction by coordinating actions based on screen state.",
    sub_agents=[browser_coordinator_agent],
    max_iterations=10,  # Default limit - can be overridden by state['max_iterations']
    before_agent_callback=before_loop_iteration, 
    # exit_condition is handled by setting state['exit_loop'] in the callback
)

# Expose the loop agent as the main entry point for this capability
agent = browser_loop_agent
