"""Data models for differences and analysis."""
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field


class DifferenceError(Exception):
    """Base error for difference-related operations."""
    pass


class ValidationError(DifferenceError):
    """Error raised when difference validation fails."""
    pass


@dataclass
class Difference:
    """Model representing a difference between specifications.
    
    Attributes:
        model: The model number with the most different value
        category: The category of the specification (e.g., 'Technical')
        subcategory: The subcategory (e.g., 'Voltage')
        specification: The specific attribute being compared
        difference: Description of the difference
        unit: Optional unit of measurement
        values: Dictionary mapping model numbers to their values
    """
    model: str
    category: str
    subcategory: str
    specification: str
    difference: str
    unit: Optional[str] = None
    values: Dict[str, str] = field(default_factory=dict)
    
    def __post_init__(self):
        """Validate the difference after initialization."""
        if not self.model:
            raise ValidationError("Model number is required")
        if not self.category:
            raise ValidationError("Category is required")
        if not self.specification:
            raise ValidationError("Specification is required")
        if not self.difference:
            raise ValidationError("Difference description is required")
        if not self.values:
            raise ValidationError("Values dictionary is required")
            
    @classmethod
    def create(
        cls,
        model: str,
        category: str,
        specification: str,
        difference: str,
        values: Dict[str, str],
        subcategory: Optional[str] = None,
        unit: Optional[str] = None
    ) -> 'Difference':
        """Create a new Difference instance with validation.
        
        Args:
            model: Model number that has the difference
            category: Category the difference occurs in
            specification: Specific value that differs
            difference: How it differs from other models
            values: Raw values for comparison
            subcategory: Optional subcategory if applicable
            unit: Optional unit of measurement if applicable
            
        Returns:
            Difference: The validated difference instance
            
        Raises:
            ValidationError: If validation fails
        """
        return cls(
            model=model,
            category=category,
            subcategory=subcategory or "",
            specification=specification,
            difference=difference,
            unit=unit,
            values=values
        )


@dataclass
class Analysis:
    """Model representing an analysis of differences.
    
    Attributes:
        summary: Brief summary of the differences
        key_differences: List of most important differences
        recommendations: List of recommendations based on differences
        technical_details: Optional technical details about differences
    """
    summary: str
    key_differences: List[str]
    recommendations: List[str]
    technical_details: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        """Validate the analysis after initialization."""
        if not self.summary:
            raise ValidationError("Summary is required")
        if not self.key_differences:
            raise ValidationError("Key differences list is required")
        if not self.recommendations:
            raise ValidationError("Recommendations list is required")
            
    @classmethod
    def create(
        cls,
        summary: str,
        key_differences: List[str],
        recommendations: List[str],
        technical_details: Optional[Dict[str, Any]] = None
    ) -> 'Analysis':
        """Create a new Analysis instance with validation.
        
        Args:
            summary: Brief summary of the differences
            key_differences: List of most important differences
            recommendations: List of recommendations
            technical_details: Optional technical details
            
        Returns:
            Analysis: The validated analysis instance
            
        Raises:
            ValidationError: If validation fails
        """
        return cls(
            summary=summary,
            key_differences=key_differences,
            recommendations=recommendations,
            technical_details=technical_details
        )
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert the analysis to a dictionary.
        
        Returns:
            Dict[str, Any]: The dictionary representation
        """
        return {
            "summary": self.summary,
            "key_differences": self.key_differences,
            "recommendations": self.recommendations,
            "technical_details": self.technical_details
        } 