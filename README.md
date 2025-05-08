# AI Support Agent

An AI-driven customer support system for product information and comparison.

## Overview

This project implements a customer support agent that can extract information from PDF product manuals, compare products, and analyze differences between them. It uses a "Workflow: Routing" pattern to handle different types of customer queries, routing them to the appropriate handler based on the detected intent.

## Features

- Extract structured content from PDF files
- Compare specifications between products
- Analyze differences using LLM
- Provide product information
- Handle natural language queries

## Architecture

The system is built with a clean, modular architecture:

- **Customer Support Agent**: Main entry point that routes queries based on intent
- **PDF Processor**: Extracts content from PDF files
- **Compare Processor**: Compares specifications between products
- **AI Difference Analyzer**: Analyzes differences using LLM
- **LLM Client**: Abstraction for interacting with LLM providers

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
- `GET /api/models`: List available models
- `GET /api/model/{model_number}`: Get information about a specific model
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
│   ├── services/
│   │   ├── __init__.py
│   │   └── llm_client.py
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── ai_difference_analyzer.py
│   │   ├── compare_processor.py
│   │   ├── pdf_processor.py
│   │   └── transformers.py
│   ├── __init__.py
│   └── main.py
├── data/
│   ├── pdfs/
│   ├── diagrams/
│   └── processed/
└── static/
```

## License

MIT 