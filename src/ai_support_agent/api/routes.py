"""API routes for the customer support agent."""
from typing import Dict, List, Optional, Any
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from ..agents.customer_support_agent import CustomerSupportAgent
from ..models.product import QueryIntent
from ..models.comparison import ComparisonResponse
from ..models.differences import Analysis


# Create FastAPI router
router = APIRouter(prefix="/api", tags=["Customer Support"])


# Error handling
class ErrorResponse(BaseModel):
    """Error response model."""
    detail: str = Field(..., description="Error message")
    error_type: str = Field(..., description="Type of error")


# Request and response models
class QueryRequest(BaseModel):
    """Request model for query endpoint."""
    query: str = Field(..., description="User query to process")


class QueryResponse(BaseModel):
    """Response model for query endpoint."""
    result: Dict[str, Any] = Field(..., description="Query result")


class ModelListResponse(BaseModel):
    """Response model for model listing."""
    models: List[str] = Field(..., description="List of available model numbers")


class ModelInfoResponse(BaseModel):
    """Response model for model information."""
    specifications: Dict[str, Any] = Field(..., description="Model specifications")
    features: Optional[List[str]] = Field(None, description="Model features")
    advantages: Optional[List[str]] = Field(None, description="Model advantages")


class CompareRequest(BaseModel):
    """Request model for model comparison."""
    model_numbers: List[str] = Field(..., min_items=2, description="List of model numbers to compare")


class AnalyzeRequest(BaseModel):
    """Request model for difference analysis."""
    model_numbers: List[str] = Field(..., min_items=2, description="List of model numbers to analyze")
    topic: str = Field("specifications", description="Topic to focus on")
    sub_topic: Optional[str] = Field(None, description="Optional sub-topic to focus on")


# Error handling
def handle_customer_support_error(e: Exception) -> HTTPException:
    """Handle customer support errors.
    
    Args:
        e: The exception to handle
        
    Returns:
        HTTPException: The HTTP exception to raise
    """
    if isinstance(e, FileNotFoundError):
        return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
            headers={"error_type": "not_found"}
        )
    elif isinstance(e, ValueError):
        return HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
            headers={"error_type": "validation_error"}
        )
    else:
        return HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
            headers={"error_type": "internal_error"}
        )


# Dependency to get the customer support agent
def get_customer_support_agent() -> CustomerSupportAgent:
    """Get the customer support agent.
    
    Returns:
        CustomerSupportAgent: The customer support agent
    """
    return CustomerSupportAgent()


@router.post(
    "/query",
    response_model=QueryResponse,
    responses={
        400: {"model": ErrorResponse},
        500: {"model": ErrorResponse}
    }
)
async def handle_query(
    request: QueryRequest,
    agent: CustomerSupportAgent = Depends(get_customer_support_agent)
) -> QueryResponse:
    """Handle a customer query.
    
    Args:
        request: The query request
        agent: The customer support agent
        
    Returns:
        QueryResponse: The query response
        
    Raises:
        HTTPException: If query handling fails
    """
    try:
        # Handle the query
        result = await agent.handle_query(request.query)
        
        # Convert result to dictionary if needed
        if hasattr(result, 'to_dict'):
            result_dict = result.to_dict()
        else:
            result_dict = result
        
        return QueryResponse(result=result_dict)
    except Exception as e:
        raise handle_customer_support_error(e)


@router.get(
    "/models",
    response_model=ModelListResponse,
    responses={500: {"model": ErrorResponse}}
)
async def list_models(
    agent: CustomerSupportAgent = Depends(get_customer_support_agent)
) -> ModelListResponse:
    """List available models.
    
    Args:
        agent: The customer support agent
        
    Returns:
        ModelListResponse: List of available model numbers
        
    Raises:
        HTTPException: If the model listing fails
    """
    try:
        # Get list of PDF files in the PDF directory
        pdf_dir = agent.pdf_processor.data_dir
        
        # Extract model numbers from filenames
        model_numbers = []
        for file in pdf_dir.glob("*.pdf"):
            model_number = agent.pdf_processor._extract_model_name(file.stem)
            if model_number:
                model_numbers.append(model_number)
        
        return ModelListResponse(models=sorted(model_numbers))
    except Exception as e:
        raise handle_customer_support_error(e)


@router.get(
    "/model/{model_number}",
    response_model=ModelInfoResponse,
    responses={
        404: {"model": ErrorResponse},
        500: {"model": ErrorResponse}
    }
)
async def get_model_info(
    model_number: str,
    agent: CustomerSupportAgent = Depends(get_customer_support_agent)
) -> ModelInfoResponse:
    """Get information about a specific model.
    
    Args:
        model_number: The model number
        agent: The customer support agent
        
    Returns:
        ModelInfoResponse: Model information
        
    Raises:
        HTTPException: If the model information retrieval fails
    """
    try:
        # Create a product query intent
        intent = QueryIntent(
            domain="product",
            topic="specifications"
        )
        
        # Handle the product query
        result = await agent._handle_product_query(model_number, intent)
        
        # Convert to response model
        response_dict = result.to_dict()
        return ModelInfoResponse(
            specifications=response_dict.get("specifications", {}),
            features=response_dict.get("features", []),
            advantages=response_dict.get("advantages", [])
        )
    except Exception as e:
        raise handle_customer_support_error(e)


@router.post(
    "/compare",
    response_model=ComparisonResponse,
    responses={
        400: {"model": ErrorResponse},
        500: {"model": ErrorResponse}
    }
)
async def compare_models(
    request: CompareRequest,
    agent: CustomerSupportAgent = Depends(get_customer_support_agent)
) -> ComparisonResponse:
    """Compare multiple models.
    
    Args:
        request: The comparison request
        agent: The customer support agent
        
    Returns:
        ComparisonResponse: Comparison result
        
    Raises:
        HTTPException: If the comparison fails
    """
    try:
        # Compare the models
        result = await agent.compare_processor.compare_models(request.model_numbers)
        
        return result
    except Exception as e:
        raise handle_customer_support_error(e)


@router.post(
    "/analyze",
    response_model=Analysis,
    responses={
        400: {"model": ErrorResponse},
        500: {"model": ErrorResponse}
    }
)
async def analyze_differences(
    request: AnalyzeRequest,
    agent: CustomerSupportAgent = Depends(get_customer_support_agent)
) -> Analysis:
    """Analyze differences between models.
    
    Args:
        request: The analysis request
        agent: The customer support agent
        
    Returns:
        Analysis: Analysis result
        
    Raises:
        HTTPException: If the analysis fails
    """
    try:
        # Create a comparison query intent
        intent = QueryIntent(
            domain="comparison",
            topic=request.topic,
            sub_topic=request.sub_topic
        )
        
        # Compare the models
        comparison = await agent.compare_processor.compare_models(request.model_numbers)
        
        # Analyze the differences
        result = await agent.difference_analyzer.analyze_differences(
            comparison,
            intent
        )
        
        return result
    except Exception as e:
        raise handle_customer_support_error(e) 