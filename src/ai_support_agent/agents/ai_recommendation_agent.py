"""Service for analyzing differences between models using AI."""
from typing import Dict, List, Optional, Any
from pathlib import Path
import logging

from ..models.differences import Difference, Analysis
from ..models.product import QueryIntent
from ..llm.provider import LLMProvider
from ..llm.factory import LLMProviderFactory
from ..config import get_llm_config

logger = logging.getLogger(__name__)

class AIAIRecommendationAgent:
    """Service for analyzing differences between models using AI.
    
    This component is part of the Processing Layer and is called by the
    Customer Support Agent after receiving comparison results from the
    Compare Processor.
    """
    
    def __init__(self, llm_provider: Optional[LLMProvider] = None):
        """Initialize the analyzer.
        
        Args:
            llm_provider: Optional LLM provider to use
        """
        self.llm_provider = llm_provider or LLMProviderFactory.create_provider()
        self.config = get_llm_config()
        # Load system prompt from config or use default
        self.system_prompt = """You are an expert technical analyst specializing in magnetic sensors and relays.
            Your task is to analyze differences between product models and provide insights that would be valuable for customers.
            
            For each difference, consider:
            1. Technical significance
            2. Practical implications
            3. Use case impacts
            4. Customer recommendations
            
            Focus on providing actionable insights that help customers make informed decisions.
            Your analysis should be thorough yet accessible, suitable for both technical and non-technical audiences."""
    
    def _create_analysis_prompt(self, differences: List[Difference], intent: QueryIntent) -> str:
        """Create a prompt for the AI to analyze differences.
        
        Args:
            differences: List of differences to analyze
            intent: Query intent to focus the analysis
            
        Returns:
            str: The formatted prompt
        """
        prompt = f"Please analyze the following differences between models, focusing on {intent.topic}"
        if intent.sub_topic:
            prompt += f" specifically regarding {intent.sub_topic}"
        prompt += ":\n\n"
        
        for diff in differences:
            prompt += f"- {diff.category} > {diff.subcategory} > {diff.specification}:\n"
            prompt += f"  {diff.difference}"
            if diff.unit:
                prompt += f" ({diff.unit})"
            prompt += "\n"
            
            # Add detailed values
            prompt += "  Values by model:\n"
            for model, value in diff.values.items():
                prompt += f"    - {model}: {value}"
                if diff.unit:
                    prompt += f" {diff.unit}"
                prompt += "\n"
            prompt += "\n"
        
        prompt += """Please provide:
1. A brief summary of the key differences
2. The most important differences to consider
3. Recommendations based on these differences
4. Any relevant technical details

Format your response as JSON with the following structure:
{
    "summary": "Brief overview of differences",
    "key_differences": ["Important difference 1", "Important difference 2", ...],
    "recommendations": ["Recommendation 1", "Recommendation 2", ...],
    "technical_details": {
        "detail1": "value1",
        ...
    }
}"""
        
        return prompt
    
    async def analyze_differences(
        self,
        differences: List[Difference],
        intent: QueryIntent
    ) -> Analysis:
        """Analyze differences between models using AI.
        
        This method is called by the Customer Support Agent after receiving
        comparison results from the Compare Processor.
        
        Args:
            differences: List of differences to analyze
            intent: Query intent to focus the analysis
            
        Returns:
            Analysis: The analysis results
            
        Raises:
            ValueError: If analysis fails or response format is invalid
        """
        try:
            # Create and send prompt with system prompt
            prompt = self._create_analysis_prompt(differences, intent)
            
            # Get temperature from config
            temperature = self.config.get("temperature", 0.7)
            
            logger.debug(f"Sending analysis prompt with intent: {intent}")
            response = await self.llm_provider.generate_json(
                prompt=prompt,
                system_prompt=self.system_prompt,
                temperature=temperature
            )
            
            # Parse response into Analysis object
            data = response.content
            return Analysis(
                summary=data["summary"],
                key_differences=data["key_differences"],
                recommendations=data["recommendations"],
                technical_details=data.get("technical_details")
            )
            
        except (KeyError, TypeError) as e:
            logger.error(f"Failed to parse AI response: {str(e)}")
            # Return error analysis that frontend can handle
            return Analysis(
                summary="Error analyzing differences",
                key_differences=["Failed to parse AI response"],
                recommendations=["Please try again or contact support"],
                technical_details={
                    "error": str(e),
                    "raw_response": response.content if 'response' in locals() else None
                }
            )
            
        except Exception as e:
            logger.error(f"Unexpected error in analyze_differences: {str(e)}")
            raise ValueError(f"Failed to analyze differences: {str(e)}") 