"""Data models for comparison functionality."""
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field

from .pdf import Specification

@dataclass
class Feature:
    """Feature model.
    
    Represents a feature or advantage with its text and model availability.
    
    Attributes:
        text: Feature/advantage text
        models: Model numbers to presence indicator
    """
    text: str
    models: Dict[str, bool]

@dataclass
class ComparisonSpecification:
    """Comparison specification model.
    
    Represents a specification comparison between models.
    
    Attributes:
        category: Category within section (e.g., 'Voltage')
        specification: Specification name (e.g., 'Switching')
        values: Model numbers to their values
        has_differences: Whether values differ between models
        analysis: Optional analysis data
    """
    category: str
    specification: str
    values: Dict[str, Specification]
    has_differences: bool
    analysis: Optional[Dict[str, Any]] = None

@dataclass
class ComparisonSection:
    """Comparison section model.
    
    Represents a section in the comparison result.
    
    Attributes:
        categories: Specifications or features grouped by category
    """
    categories: Dict[str, List[ComparisonSpecification]] = field(default_factory=dict)

@dataclass
class ComparisonResponse:
    """Comparison response model.
    
    Represents the complete comparison result.
    
    Attributes:
        model_numbers: Models being compared
        sections: All sections including specs, features, and advantages
        differences_count: Number of specifications with differences
    """
    model_numbers: List[str]
    sections: Dict[str, ComparisonSection] = field(default_factory=dict)
    differences_count: int = 0 