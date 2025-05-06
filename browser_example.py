"""Example script demonstrating how to use the browser agent."""

import os
import dotenv
from browser_use_agent.runner import run_browser_agent

# Load environment variables from .env file
dotenv.load_dotenv()

def main():
    """Run an example browser automation task."""
    
    # Define a goal for the browser agent
    user_goal = "Book me a movie ticket - Animal"
    
    # The starting URL
    initial_url = "https://www.bing.com/"
    
    print(f"Starting browser agent with goal: {user_goal}")
    print(f"Initial URL: {initial_url}")
    print("=" * 80)
    
    # Run the browser agent
    result = run_browser_agent(
        user_goal=user_goal,
        initial_url=initial_url,
        max_iterations=5  # Allow more iterations for complex tasks
    )
    
    # Print the final result
    print("=" * 80)
    print("FINAL RESULT:")
    print(result)

if __name__ == "__main__":
    main()