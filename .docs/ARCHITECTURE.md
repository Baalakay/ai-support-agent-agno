# AI Support Agent

An AI-driven customer support system for product information and comparison.

## Overview

This project implements a partially refactored customer support agent for a magnetic sensor manufacturing company. It responds to queries about sensor products by extracting information from relevant PDF manuals. The agent can handle queries about single models or perform comparisons between multiple models. When comparing models, the system extracts differences and provides expert analysis on those differences. It uses a "Workflow: Routing" pattern as defined in https://www.anthropic.com/engineering/building-effective-agents to handle different types of customer queries, and using the customer agent's tools when applicable based on the detected intent (e.g., extract single product model data, extract two models and compare differences in specifications and provide AI recommendations where each excel, pros, cons, etc.,). There will ony be one agent defined (customer_support_agent) to handle the queries and tool invocations.

The application is "partially" refactored in order to implement the AI agents in Agno. The current agents are normal Python onbjects that will need to be replaced with Agno agents. It is critically important to preserve the features/functions of existing agents and tools. but refactored to utilize Agno for the agents. Much of the Python tools, models, and backend API code exists (from the previous implementation) but will likely need to also be refactored some to align with the Agno agents. Some files have been renamed or moved from their previous location so it is important to update all the imports as required. There will also be a front-end component, but that will be another phase, and the current need (Phase 1) is to conplete the backend features. 

## Application Features

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
- **AI Difference Agent**: Analyzes differences using LLM
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

## API Endpoints

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

## Key Refactoring Goals

1. **Simplification**
    - Maintain the same JSON output format

2. **Pattern Implementation**
   - Implement the "Workflow: Routing" pattern
   - Create a customer support agent that routes to appropriate tools
   - Maintain clear separation of concerns

3. **Preservation**
   - Preserve the PDF extraction logic that uses pdfplumber and fitz
   - Important: Do not under any circumstances change the PDF extraction logic unless approval is granted
   - Maintain the comparison functionality
   - Ensure the same output format for API responses

4. **Abstraction**
   - Implement a simple LLM provider abstraction
   - Support OpenAPI gpt 4.0 turbo as the default provider
   - Allow for easy switching between providers


## System Architecture

```mermaid
graph TB
    ClientUI[Client UI] --> Vite
    Vite --> FastAPI[FastAPI Backend]
    FastAPI --> CSA[Customer Support Agent]
    
    subgraph "Processing Layer"
        CSA --> Tool (Choose which tools based on user query: PDF[PDF Processor Tool], COMP[Compare Processor Tool], ARA[AI Recommendation Agent]]
    end
    
    subgraph "LLM Layer"
        CSA --> LLMClient[LLM Client]
        LLMClient --> OpenAPIProvider[OpenAPI Provider]
        LLMClient --> OtherProviders[Other Providers]
    end
```

## Query Processing Workflow

```mermaid
sequenceDiagram
    participant Client
    participant API as FastAPI
    participant CSA as Customer Support Agent
    participant LLM as LLM Client
    participant PDF as PDF Processor Tool
    participant COMP as Compare Processor Tool
    participant ARA as AI Recommendation Agent

    Client->>API: Product Query
    API->>CSA: Process Query
    CSA->>LLM: Determine Intent
    LLM->>Tool: Based on Query Intent
    Tool->>LLM: Tool output
    LLM->>CSA: LLM Response
    CSA->>Client

    alt Single Model Query
        CSA->>LLM
        LLM->>PDF(Tool): Process PDF
        PDF(Tool)->>LLM: Extracted PDF data (JSON)
        LLM->>CSA: Filtered content response to use query
        CSA->>API: JSON Response
    else Comparison Query (when more than one sensor model is requested)
        CSA->>LLM: Compare Models
        LLM->>COMP(Tool): Send model names
        COMP(Tool)->>PDF(Tool): Extract each model's PDF data
        PDF(Tool)->>COMP(Tool): Send extracted PDF output in JSON (per model to compare)
        COMP(Tool)->>COMP(Tool): Extract Differences 
        COMP(Tool)-->>LLM: Comparison Results
        LLM->>AIA: Comparison results
        ARA->>LLM: Generate recommendations/analysis from comparison results
        LLM-->>ARA: AI recommendations/analysis
        ARA-->>CSA: AI recommendations/analysis
        CSA-->>API: JSON Response
    end

    API-->>Client: Update UI
```

## Component Details

1. **Customer Support Agent**
    The Customer Support Agent (CSA) is the central orchestrator that routes queries to appropriate tools based on the query intent. It uses the LLM to determine the intent and then calls the appropriate tools to process the query.

2. **LLM Client**
    The LLM Client provides a simple abstraction for interacting with different LLM providers. It supports OpenAI as the default provider but can be extended to support other providers.

3. **PDF Processor**
    The PDF Processor extracts content from PDF files containing product specifications. 

4. **Compare Processor**
    The Compare Processor compares specifications between multiple products.

5. **AI Recommendation Agent**
    The AI Recommendation Agent uses the LLM to analyze differences between products and acts as a magnetic sensor specialist to provide expert recommendations.

6. **Configuration**
    The configuration maintains shared/global configuration data and variables.

7. **Data Models**


## Project Directory Structure

```
src/
├── ai_support_agent/
│   ├── agents/                             # Agent implementations
│   │   ├── __init__.py
│   │   ├── ai_recommendation_agent.py
│   │   └── customer_support_agent.py
│   ├── api/                                 # API endpoints
│   │   ├── __init__.py
│   │   └── routes.py
│   ├── config/                              # Configuration
│   │   ├── __init__.py
│   │   └── config.py
├── llm/                                     # LLM client and providers
│   ├── llm_client.py
│   ├── gemini_provider.py
│   └── provider_base.py
│   ├── models/                              # Data models
│   │   ├── __init__.py
│   │   ├── agent.py
│   │   ├── comparison.py
│   │   ├── differences.py
│   │   ├── pdf.py
│   │   └── product.py
│   ├── services/                            # Shared services that tools/agents can call
│   ├── tools/                               # Tools that LLM can call
│   │   ├── __init__.py
│   │   ├── compare_processor.py
│   │   ├── pdf_processor.py
│   │   └── transformers.py
│   ├── __init__.py
│   └── main.py                              # Application entry point
├── data/
│   ├── pdfs/                                # PDFs in original form to be extracted from
│   └── diagrams/                            # diagrams extracted from PDFs for displaying in front end 
└── scripts/

frontend/                                    # Frontend implementation root
```


## Implementation Details

1. **Routing Pattern Implementation**

    The Customer Support Agent implements the "Workflow: Routing" pattern by:
    - Determining the intent of a query using the LLM
    - Routing the query to the appropriate tool based on the intent
    - Handling the response from the tool and returning it to the client

2. **LLM Provider Abstraction**
    The LLM Client provides a simple abstraction for interacting with different LLM providers:

3. **PDF Extraction Preservation**
    The PDF Processor preserves the extraction logic from the original implementation:

4. **Error Handling**
    The implementatio includes proper error handling throughout the codebase:

## Critical Implementation Requirements

This implementation follows these cursor rules:
- Python core best practices
- Documentation standards
- Error handling best practices
- Single responsibility principle
