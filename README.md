# Company Research Assistant - AI Agent

An intelligent conversational AI agent that researches companies and generates comprehensive account plans using Gemini AI, Wikipedia, and web scraping.

## Features

-  Multi-source company research (Wikipedia, web scraping)
-  Automated account plan generation
-  Natural conversational interface
-  Section-by-section plan updates
-  Real-time research progress updates
-  Handles multiple user personas (confused, efficient, chatty, edge cases)

## Architecture

### Components

1. **Agent** (`agent.py`) - Core conversational AI using Gemini
2. **Tools** (`tools.py`) - Research tools (Wikipedia API, ScrapingDog)
3. **Account Plan** (`account_plan.py`) - Plan structure and management
4. **Main** (`main.py`) - CLI interface

### Design Decisions

- **Gemini Pro**: Chosen for natural language understanding, intent detection, and content generation
- **Multi-source Research**: Wikipedia for reliable public data, ScrapingDog for live website content
- **Modular Architecture**: Separation of concerns for maintainability
- **Conversational State**: Maintains context across conversation
- **Transparency**: Agent provides real-time updates during research

## Setup

### Prerequisites

- Python 3.8+
- Gemini API key
- ScrapingDog API key




