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

## Requirements

- Python 3
- Playwright
- Google Gemini API access
- PIL (Pillow)
- OpenCV (for visualization)