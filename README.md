# AI Support Agent

An AI-driven customer support system for product information and comparison.

## Overview

This project implements a customer support agent that can extract information from customer's sensor product PDFs, compare products, and analyze differences between them. It uses a "Workflow: Routing" pattern as defined in https://www.anthropic.com/engineering/building-effective-agents to handle different types of customer queries, and using the customer agent's tools when applicable based on the detected intent. There will ony be one agent defined (customer_support_agent) to handle the queries and tool invocations.

## Features

- Extract structured content from PDF files
- Compare specifications between products
- Analyze differences using LLM
- Provide product information
- Handle natural language queries

## Architecture

The system is built with a clean, modular architecture:

- **Customer Support Agent**: Main entry point that routes queries based on intent
- **PDF Processor**: Tool to extract content from PDF files
- **Compare Processor**: Tool to compare specifications between products
- **AI Difference Analyzer**: Analyzes differences using LLM
- **LLM Client**: Abstraction for tools to interact with different LLM providers

## Technology to use
- **Backend Code**: Python
- **Agentic Framework**: Agno
- **Python Linter/Formatter**: ruff
- **FrontEnd Code**: React, Typescript, Tailwind CSS, ShadUI
- **Python Package Management**: uv
- **Python Build Backend**: hatchling
- **Other Python libraries**: use 'uv pip list' 

## Forbidden Python Package Install or Usage
- pip

## Installation

1. Clone the repository
2. Create a virtual environment: `python -m venv venv`
3. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - Unix/MacOS: `source venv/bin/activate`
4. Install dependencies: `pip install -r requirements.txt`
5. Create a `.env` file with your configuration (see `.env.example`)

## Usage

### Running the API

```bash
cd src
python -m ai_support_agent.main
```

The API will be available at http://localhost:8000

### API Endpoints

- `POST /api/query`: Handle a customer query
- `GET /api/models`: List available product sensor models
- `GET /api/model/{model_number}`: Get information about a specific product sensor model
- `POST /api/compare`: Compare multiple models
- `POST /api/analyze`: Analyze differences between models

## Example Queries

- "What are the specifications of HSR-412R?"
- "Compare HSR-412R and HSR-520R"
- "What are the differences between HSR-412R and HSR-520R?"
- "What are the features of HSR-412R?"

## Project Structure

```
src/
├── ai_support_agent/
│   ├── agents/
│   │   ├── __init__.py
│   │   └── customer_support_agent.py
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes.py
│   ├── config/
│   │   ├── __init__.py
│   │   └── config.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── agent.py
│   │   ├── comparison.py
│   │   ├── differences.py
│   │   ├── pdf.py
│   │   └── product.py
│   ├── services/ # Services that tools can call
│   ├── tools/ # Tools that LLM can call
│   │   ├── __init__.py
│   │   ├── ai_difference_analyzer.py
│   │   ├── compare_processor.py
│   │   ├── pdf_processor.py
│   │   └── transformers.py
│   ├── __init__.py
│   └── main.py
├── data/
│   ├── pdfs/ # PDFs in original form to be extracted from
│   └── diagrams/ # diagrams extracted from PDFs for displaying in front end 
└── scripts/
```

## License

MIT 