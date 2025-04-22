# Orbit Agent

Orbit Agent is a browser automation framework that combines the power of Gemini AI models with browser automation capabilities.

## Overview

This project enables automated web browsing through AI-driven agents, allowing for:

- Task completion via browser automation
- Visual interaction with web elements
- AI decision-making based on screen context

## Key Components

- **Gemini Integration**: Uses Google's Gemini models for content generation and decision-making
- **Browser Automation**: Playwright-based controller for web navigation and interaction
- **Computer Vision**: OpenCV utilities for visualizing interaction points
- **Action Tools**: Structured tools for clicking, typing, scrolling, and keyboard input

## How it Works

1. The main Gemini agent receives user instructions
2. Upon activation, a specialized browser agent is deployed
3. The browser agent:
   - Interprets the current screen
   - Decides on appropriate actions (clicking, typing, scrolling)
   - Executes actions via the browser controller
   - Takes screenshots to observe results
   - Continues until task completion or user intervention

## Use Cases

- Web testing automation
- Form filling and data entry
- Web scraping and information gathering
- Task automation for repetitive web-based workflows

## Agent Architecture

This diagram outlines the multi-agent architecture used for browser automation:

```bash
MasterAgent (Handles simple queries, dispatches complex tasks like web browsing)
 │
 └─> Calls -> LoopAgent (Manages the overall browser task cycle)
               │
               └─> BrowserCoordinatorAgent with Planner()
                     │
                     ├─ Has -> HumanInteractionAgent
                     │           │
                     │           └─ Has -> _
                     │
                     ├─ Has -> BrowserActionExecutorAgent
                     │           │
                     │           ├─ Has -> click_at()
                     │           ├─ Has -> type_text()
                     │           └─ Has Tool -> scroll_page()
                     │                                          
                     └─> Has -> ReflectionAgent
```

**Flow Summary:**

1.  The `MasterAgent` delegates browser tasks to the `LoopAgent`.
2.  The `LoopAgent` iterates, running the `SequentialAgent` in each cycle.
3.  The `SequentialAgent` executes the `BrowserCoordinatorAgent`.
4.  The `BrowserCoordinatorAgent` analyzes the browser state (screenshot).
    *   If it needs user input (like login credentials), it calls the `HumanInteractionAgent` tool.
    *   Otherwise, it determines the next browser action (e.g., "click button") and calls the `BrowserActionExecutorAgent` tool.
5.  The `BrowserActionExecutorAgent` uses vision to find the target element on the screenshot and calls the appropriate low-level browser function tool (`click_at`, `type_text`, etc.).
6.  The loop repeats, capturing a new state (screenshot) and continuing the process.

## Requirements

- Python 3
- Playwright
- Google Gemini API access
- PIL (Pillow)
- OpenCV (for visualization)