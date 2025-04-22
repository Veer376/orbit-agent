"""Defines the Browser Coordinator Agent."""

import logging
from google.adk.agents import LlmAgent
from google.adk.tools import AgentTool, FunctionTool
from google.adk.agents.callback_context import CallbackContext
from pydantic import BaseModel, Field

# Import necessary components from the package
from .. import GEMINI_MODEL
from .executor import browser_executor_agent
from .interaction import human_interaction_agent

logger = logging.getLogger(__name__)

# --- Task Management Tools ---

class TaskCompletionArgs(BaseModel):
    reason: str = Field(description="Reason why the task is considered complete")
    result: str = Field(description="Final result or output from the completed task")

class TaskFailureArgs(BaseModel):
    reason: str = Field(description="Reason why the task failed")
    details: str = Field(description="Details about what was attempted and why it failed")

def mark_task_complete(args: TaskCompletionArgs) -> str:
    """
    Marks the current browser task as successfully completed.
    This will exit the loop with a success status.
    """
    logger.info(f"Task marked as complete: {args.reason}")
    # This will be handled by accessing state in the tool context
    return f"Task marked as complete. Reason: {args.reason}"

def mark_task_failed(args: TaskFailureArgs) -> str:
    """
    Marks the current browser task as failed.
    This will exit the loop with a failure status.
    """
    logger.warning(f"Task marked as failed: {args.reason}")
    # This will be handled by accessing state in the tool context
    return f"Task marked as failed. Reason: {args.reason}"

# Callbacks for task management tools
def after_task_complete_callback(
    tool, args, tool_context, tool_response
) -> dict:
    """Updates state after task_complete tool is called"""
    tool_context.state['task_completed'] = True
    tool_context.state['task_result'] = args.result
    tool_context.state['task_completion_reason'] = args.reason
    # Signal to the LoopAgent that it should exit
    tool_context.state['exit_loop'] = True
    return tool_response

def after_task_failed_callback(
    tool, args, tool_context, tool_response
) -> dict:
    """Updates state after task_failed tool is called"""
    tool_context.state['task_failed'] = True
    tool_context.state['task_failure_reason'] = args.reason
    tool_context.state['task_failure_details'] = args.details
    # Signal to the LoopAgent that it should exit
    tool_context.state['exit_loop'] = True
    return tool_response

# Create the tools with their callbacks
task_complete_tool = FunctionTool(
    func=mark_task_complete,
    name="mark_task_complete",
    after_tool_callback=after_task_complete_callback
)

task_failed_tool = FunctionTool(
    func=mark_task_failed,
    name="mark_task_failed",
    after_tool_callback=after_task_failed_callback
)

# --- Agent Definition ---

# Wrap the sub-agents as tools for the coordinator
executor_tool = AgentTool(agent=browser_executor_agent)
interaction_tool = AgentTool(agent=human_interaction_agent)

browser_coordinator_agent = LlmAgent(
    name="BrowserCoordinatorAgent",
    description="Coordinates browser actions to achieve a user goal based on visual context.",
    model=GEMINI_MODEL, # Ensure this model supports multimodal input (image + text)
    instruction=(
        "You are a browser automation coordinator. Your goal is to achieve the user's objective by interacting with a web page. "
        "You will receive the user's overall goal and the current visual state of the browser page as an image in the history. "
        "Analyze the image and the goal to determine the next logical action (e.g., click a button, type in a field, scroll). "
        "\n\n"
        "Use the 'BrowserExecutorAgent' tool to perform the chosen action. Provide the exact tool name (e.g., 'click_element', 'type_text') and necessary arguments based on your analysis of the image. "
        "\n\n"
        "If you are unsure how to proceed, cannot find the necessary element, or require information like login credentials or CAPTCHA input, use the 'HumanInteractionAgent' tool to ask the user for help. Clearly state the reason and what information you need. "
        "\n\n"
        "Review the history to understand previous actions and results. Continue step-by-step until the user's goal is achieved or you determine it cannot be completed."
        "\n\n"
        "When you have successfully completed the user's goal, use the 'mark_task_complete' tool to signal completion with a reason and result summary. "
        "If you determine the task cannot be completed after reasonable effort, use the 'mark_task_failed' tool with an explanation."
        "\n\n"
        "Additional guidelines:"
        "\n- Always confirm that actions had the expected result by analyzing the screenshot"
        "\n- If text needs to be entered, ensure the correct field is focused or click it first"
        "\n- If an element is not visible, try scrolling to reveal it"
        "\n- Keep track of your progress and make sure you're advancing toward the goal"
    ),
    tools=[
        executor_tool,
        interaction_tool,
        task_complete_tool,
        task_failed_tool
    ],
)
