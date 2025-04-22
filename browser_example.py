"""Example script demonstrating how to use the browser agent."""

import os
import logging
from browser_use_agent.runner import run_browser_agent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Set environment variables if not already set
# os.environ["GOOGLE_API_KEY"] = "your_key_here"  # Uncomment and set your key if needed
# os.environ["GEMINI_MODEL"] = "gemini-1.5-flash"  # Uncomment and set your preferred model

def main():
    """Run an example browser automation task."""
    
    # Define a goal for the browser agent
    user_goal = "Search for 'Python programming tutorials' on Bing and find the first official Python tutorial link"
    
    # The starting URL
    initial_url = "https://www.bing.com/"
    
    print(f"Starting browser agent with goal: {user_goal}")
    print(f"Initial URL: {initial_url}")
    print("=" * 80)
    
    # Run the browser agent
    result = run_browser_agent(
        user_goal=user_goal,
        initial_url=initial_url,
        max_iterations=15  # Allow more iterations for complex tasks
    )
    
    # Print the final result
    print("=" * 80)
    print("FINAL RESULT:")
    print(result)

if __name__ == "__main__":
    main()