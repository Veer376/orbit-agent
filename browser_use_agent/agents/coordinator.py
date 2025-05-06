"""Defines the Browser Coordinator Agent."""

from google.adk.agents import LlmAgent
from google.adk.tools.agent_tool import AgentTool  # Changed import to use specific module
from google.adk.tools import FunctionTool
from google.adk.agents.callback_context import CallbackContext
from pydantic import BaseModel, Field

# Import necessary components from the package
from .. import GEMINI_MODEL
from .executor import browser_action_executor_agent
from .interaction import human_interaction_agent
from ..schema import TaskCompletionArgs, TaskFailureArgs

# --- Task Management Tools ---


def mark_task_complete(args: TaskCompletionArgs, tool_context=None) -> str:
    """
    Marks the current browser task as successfully completed.
    This will exit the loop with a success status.
    """
    print(f"[SUCCESS] Task marked as complete: {args.reason}")
    # This will be handled by accessing state in the tool context
    if tool_context:
        tool_context.state['task_completed'] = True
        tool_context.state['task_result'] = args.result
        tool_context.state['task_completion_reason'] = args.reason
        # Signal to the LoopAgent that it should exit
        tool_context.state['exit_loop'] = True
    return f"Task marked as complete. Reason: {args.reason}"


def mark_task_failed(args: TaskFailureArgs, tool_context=None) -> str:
    """
    Marks the current browser task as failed.
    This will exit the loop with a failure status.
    
    Args:
        args: A TaskFailureArgs object with reason and details
        tool_context: The context for this tool execution
    """
    try:
        # Try to access args as a TaskFailureArgs object
        reason = args.get("reason", "Unknown reason")
        details = args.get("details", "No details provided")
    except (AttributeError, TypeError):
        # Handle dictionary formats
        if isinstance(args, dict):
            if 'args' in args and isinstance(args['args'], dict):
                # Nested args structure that sometimes comes from the LLM
                inner_args = args['args']
                reason = inner_args.get('reason', 'Unknown reason')
                details = inner_args.get('details', 'No details provided')
            else:
                # Direct dictionary
                reason = args.get('reason', 'Unknown reason')
                details = args.get('details', 'No details provided')
        else:
            # Fallback
            reason = "Unknown failure reason"
            details = "No details available"
    
    print(f"[FAILURE] Task marked as failed: {reason}")
    print(f"[DETAILS] {details}")
    
    # This will be handled by accessing state in the tool context
    if tool_context:
        tool_context.state['task_failed'] = True
        tool_context.state['task_failure_reason'] = reason
        tool_context.state['task_failure_details'] = details
        # Signal to the LoopAgent that it should exit
        tool_context.state['exit_loop'] = True
    
    return f"Task marked as failed. Reason: {reason}"


# Create the tools with their callbacks (modified to work with ADK's FunctionTool implementation)
task_complete_tool = FunctionTool(mark_task_complete)
task_failed_tool = FunctionTool(mark_task_failed)

# --- Agent Definition ---

# Wrap the sub-agents as tools for the coordinator
executor_tool = AgentTool(agent=browser_action_executor_agent)
interaction_tool = AgentTool(agent=human_interaction_agent)

browser_coordinator_agent = LlmAgent(
    name="BrowserCoordinatorAgent",
    description="Coordinates browser actions to achieve a user goal based on visual context.",
    model=GEMINI_MODEL, # Ensure this model supports multimodal input (image + text)
    instruction=(
        "You are a browser automation coordinator. Your goal is to achieve the user's objective by interacting with a web page. "
        "You will receive the user's overall goal and the current visual state of the browser page as an image in the history. "
        "\n\n"
        "FIRST STEP: Always begin by carefully analyzing the initial screenshot to understand the current page state. "
        "Identify key elements visible in the screenshot such as buttons, input fields, menu items, and page content. "
        "This analysis is crucial for planning your approach to meet the user's goal."
        "\n\n"
        "Analyze the image and the goal to determine the next logical action. Think about what a human would do next, such as:"
        "\n- \"I need to click on the search bar\""
        "\n- \"I should type 'movie tickets' in this field\""
        "\n- \"I need to scroll down to see more options\""
        "\n- \"I should press Enter to submit the form\""
        "\n\n"
        "Focus on explaining your reasoning about WHAT needs to be done next rather than specifying technical implementation details. "
        "Based on your reasoning, the system will determine how to execute the action."
        "\n\n"
        "For each action, you need to provide:"
        "\n- For clicking: A clear description of what element you want to click"
        "\n- For typing: What text you want to enter and which field it should go into"
        "\n- For scrolling: Which direction to scroll and why"
        "\n- For key presses: Which keys need to be pressed (like Enter)"
        "\n\n"
        "If you are unsure how to proceed, cannot find the necessary element, or require information like login credentials or CAPTCHA input, use the 'HumanInteractionAgent' tool to ask the user for help. When using this tool, you MUST ALWAYS include BOTH:"
        "\n- 'reason': A clear explanation of why you need human assistance"
        "\n- 'required_info': A list of the specific information you need from the user"
        "\n\nFor example: { 'reason': 'Need movie ticketing website URL', 'required_info': ['URL of a movie ticketing website'] }"
        "\n\n"
        "Review the history to understand previous actions and results. Continue step-by-step until the user's goal is achieved or you determine it cannot be completed."
        "\n\n"
        "When you have successfully completed the user's goal, mark the task as complete with a reason and result summary. "
        "If you determine the task cannot be completed after reasonable effort, mark the task as failed with an explanation."
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
