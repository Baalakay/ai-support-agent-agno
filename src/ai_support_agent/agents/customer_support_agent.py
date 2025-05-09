"""Customer support agent for handling product queries."""
from typing import Dict, List, Optional, Any
import re
import json
import logging

from ..models.agent import BaseAgent
from ..tools.pdf_processor import PDFProcessor
from ..tools.compare_processor import CompareProcessor
from ..tools.ai_difference_analyzer import AIDifferenceAnalyzer
from ..llm import LLMProvider, get_provider

logger = logging.getLogger(__name__)


class CustomerSupportAgent(BaseAgent[None]):
    """Agent for handling customer support queries.
    
    This agent implements the "Workflow: Routing" pattern to handle different
    types of customer queries, routing them to the appropriate handler based
    on the detected intent.
    """
    
    def __init__(
        self,
        pdf_processor: Optional[PDFProcessor] = None,
        compare_processor: Optional[CompareProcessor] = None,
        difference_analyzer: Optional[AIDifferenceAnalyzer] = None,
        llm_provider: Optional[LLMProvider] = None
    ):
        """Initialize the customer support agent.
        
        Args:
            pdf_processor: Optional PDF processor to use
            compare_processor: Optional compare processor to use
            difference_analyzer: Optional difference analyzer to use
            llm_provider: Optional LLM provider to use
        """
        super().__init__()
        self.llm_provider = llm_provider or get_provider()
        self.pdf_processor = pdf_processor or PDFProcessor()
        self.compare_processor = compare_processor or CompareProcessor()
        self.difference_analyzer = difference_analyzer or AIDifferenceAnalyzer(self.llm_provider)
    
    def get_system_message(self) -> str:
        """Get the system message for the agent."""
        return """You are a helpful customer support agent for a company that manufactures magnetic sensors and relays.
Your task is to analyze customer queries and extract the following information:
1. Query domain (product information, comparison, or features)
2. Topic of interest (specifications, features, advantages, etc.)
3. Model numbers mentioned in the query

Respond with a JSON object containing:
{
  "domain": "product | comparison | features",
  "topic": "specifications | features | advantages | etc.",
  "model_numbers": ["HSR-412R", "HSR-520R", etc.]
}"""
    
    async def analyze_query(self, query: str) -> Dict[str, Any]:
        """Analyze a customer query to detect intent and model numbers.
        
        Args:
            query: The customer query
            
        Returns:
            Dict[str, Any]: The analysis result with domain, topic, and model numbers
        """
        try:
            # Extract model numbers from the query
            model_numbers = self._extract_model_numbers(query)
            
            # If we have an LLM provider, use it to analyze the query
            if self.llm_provider:
                response = await self.llm_provider.generate_text(
                    prompt=self._generate_query_prompt(query)
                )
                
                # Parse the response as JSON
                try:
                    result = json.loads(response.content)
                    result["model_numbers"] = result.get("model_numbers", model_numbers)
                    result["source"] = "llm"
                    return result
                except (json.JSONDecodeError, KeyError) as e:
                    logger.warning(f"Failed to parse LLM response: {str(e)}")
            
            # Rule-based analysis as fallback
            domain = "product"
            topic = "specifications"
            
            # Check for comparison intent
            comparison_keywords = ["compare", "comparison", "versus", "vs", "difference", "differences"]
            if any(keyword in query.lower() for keyword in comparison_keywords) and len(model_numbers) > 1:
                domain = "comparison"
            
            # Check for features intent
            feature_keywords = ["feature", "features", "advantage", "advantages", "benefit", "benefits"]
            if any(keyword in query.lower() for keyword in feature_keywords):
                topic = "features"
            
            return {
                "domain": domain,
                "topic": topic,
                "model_numbers": model_numbers,
                "source": "rule-based"
            }
            
        except Exception as e:
            raise ValueError(f"Failed to analyze query: {str(e)}")
    
    async def handle_query(self, query: str) -> Dict[str, Any]:
        """Handle a customer query.
        
        Args:
            query: The customer query
            
        Returns:
            Dict[str, Any]: The response based on the query intent
        """
        # Analyze the query
        analysis = await self.analyze_query(query)
        
        # Route to the appropriate handler based on intent
        if analysis["domain"] == "product" and analysis["model_numbers"]:
            # Handle single product query
            return await self._handle_product_query(
                analysis["model_numbers"][0],
                analysis["topic"]
            )
        elif analysis["domain"] == "comparison" and len(analysis["model_numbers"]) > 1:
            # Handle comparison query
            comparison = await self.compare_processor.compare_models(analysis["model_numbers"])
            
            # If the topic is features, return the comparison as is
            if analysis["topic"] == "features":
                return comparison.to_dict()
            
            # Otherwise, analyze the differences
            result = await self.difference_analyzer.analyze_differences(
                comparison,
                analysis["topic"]
            )
            return result.to_dict()
        else:
            # Default to handling the first model if available
            if analysis["model_numbers"]:
                return await self._handle_product_query(
                    analysis["model_numbers"][0],
                    analysis["topic"]
                )
            
            # If no model numbers, return an error
            raise ValueError("No model numbers found in query")
    
    async def _handle_product_query(
        self,
        model_number: str,
        topic: str
    ) -> Dict[str, Any]:
        """Handle a query about a single product.
        
        Args:
            model_number: The model number
            topic: The query topic
            
        Returns:
            Dict[str, Any]: The product information
        """
        try:
            # Get product content
            content = self.pdf_processor.get_content(model_number)
            
            # Filter sections based on intent
            sections = {}
            
            if topic == "features":
                if "Features_And_Advantages" in content.sections:
                    sections["Features_And_Advantages"] = content.sections["Features_And_Advantages"].to_dict()
            elif topic == "specifications":
                # Include all sections except Features_And_Advantages
                for section_name, section in content.sections.items():
                    if section_name != "Features_And_Advantages":
                        sections[section_name] = section.to_dict()
            else:
                # Include all sections
                for section_name, section in content.sections.items():
                    sections[section_name] = section.to_dict()
            
            return {
                "model_number": model_number,
                "sections": sections,
                "source": "pdf_processor"
            }
            
        except Exception as e:
            raise ValueError(f"Failed to handle product query: {str(e)}")
    
    def _extract_model_numbers(self, query: str) -> List[str]:
        """Extract model numbers from a query.
        
        Args:
            query: The query to extract from
            
        Returns:
            List[str]: The extracted model numbers
        """
        # Common patterns for model numbers
        patterns = [
            r'([A-Z0-9]+-[A-Z0-9]+)',  # Pattern like HSR-412R
            r'([A-Z]{2,4}[0-9]{3,5}[A-Z]?)',  # Pattern like HSR412R
            r'([A-Z]{2,4}-?[0-9]{3,5}[A-Z]?)'  # Pattern like HSR-412R or HSR412R
        ]
        
        model_numbers = []
        
        for pattern in patterns:
            matches = re.findall(pattern, query)
            model_numbers.extend(matches)
        
        # Remove duplicates while preserving order
        seen = set()
        return [x for x in model_numbers if not (x in seen or seen.add(x))]
    
    def _generate_query_prompt(self, query: str) -> str:
        """Generate a prompt for the query.
        
        Args:
            query: The customer's query
            
        Returns:
            str: Generated prompt
        """
        return f"""Please help answer this customer query:

Query: {query}

Please provide:
1. A clear and helpful response
2. Any relevant information or context
3. Next steps or recommendations if applicable""" 