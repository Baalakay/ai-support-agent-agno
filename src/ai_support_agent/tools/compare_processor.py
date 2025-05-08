"""Service for comparing PDF specifications."""
from typing import Dict, List, Optional, Any, Tuple
import logging

from ..models.pdf import PDFContent, Specification
from ..models.comparison import (
    Feature, ComparisonSpecification, ComparisonSection,
    ComparisonResponse
)
from ..models.differences import Difference
from .pdf_processor import PDFProcessor
from .config import get_config

logger = logging.getLogger(__name__)


class CompareProcessor:
    """Service for comparing PDF specifications.
    
    This component is part of the Processing Layer and is responsible for
    comparing specifications between different PDF documents.
    """
    
    def __init__(self, pdf_processor: Optional[PDFProcessor] = None):
        """Initialize the processor.
        
        Args:
            pdf_processor: Optional PDF processor to use
        """
        self.pdf_processor = pdf_processor or PDFProcessor()
        self.config = get_config()
    
    async def compare_models(
        self,
        model_numbers: List[str]
    ) -> ComparisonResponse:
        """Compare specifications between multiple models.
        
        Args:
            model_numbers: List of model numbers to compare
            
        Returns:
            ComparisonResponse: The comparison results
            
        Raises:
            ValueError: If comparison fails
        """
        try:
            # Collect model data
            models = await self._collect_model_data(model_numbers)
            if not models:
                return ComparisonResponse(model_numbers=model_numbers)
            
            # Process features and advantages
            features = self._process_features(models, model_numbers)
            advantages = self._process_advantages(models, model_numbers)
            
            # Process specifications and differences
            sections, differences = self._process_specifications(models, model_numbers)
            
            # Create response with unified sections structure
            response_sections: Dict[str, ComparisonSection] = {}
            
            # Add Features_And_Advantages section if there are actual features or advantages
            if features or advantages:
                categories: Dict[str, List[Feature]] = {}
                if features:
                    categories["features"] = features
                if advantages:
                    categories["advantages"] = advantages
                if categories:
                    response_sections["Features_And_Advantages"] = ComparisonSection(
                        categories=categories
                    )
            
            # Add specification sections
            response_sections.update(sections)
            
            return ComparisonResponse(
                model_numbers=model_numbers,
                sections=response_sections,
                differences_count=len(differences)
            )
            
        except Exception as e:
            logger.error(f"Failed to compare models: {str(e)}")
            raise ValueError(f"Failed to compare models: {str(e)}")
    
    async def _collect_model_data(
        self,
        model_numbers: List[str]
    ) -> Dict[str, PDFContent]:
        """Collect PDF content for all models.
        
        Args:
            model_numbers: List of model numbers
            
        Returns:
            Dict[str, PDFContent]: Model numbers to their content
        """
        models = {}
        for number in model_numbers:
            try:
                content = await self.pdf_processor.get_content(number)
                models[number] = content
            except Exception as e:
                logger.warning(f"Failed to get content for model {number}: {str(e)}")
        return models
    
    def _process_features(
        self,
        models: Dict[str, PDFContent],
        model_numbers: List[str]
    ) -> List[Feature]:
        """Process features from all models.
        
        Args:
            models: Dictionary of model numbers to their content
            model_numbers: List of model numbers to process
            
        Returns:
            List[Feature]: The processed features
        """
        return self._process_feature_type(models, model_numbers, "features")
    
    def _process_advantages(
        self,
        models: Dict[str, PDFContent],
        model_numbers: List[str]
    ) -> List[Feature]:
        """Process advantages from all models.
        
        Args:
            models: Dictionary of model numbers to their content
            model_numbers: List of model numbers to process
            
        Returns:
            List[Feature]: The processed advantages
        """
        return self._process_feature_type(models, model_numbers, "advantages")
    
    def _process_feature_type(
        self,
        models: Dict[str, PDFContent],
        model_numbers: List[str],
        feature_type: str
    ) -> List[Feature]:
        """Process a specific type of feature from all models.
        
        Args:
            models: Dictionary of model numbers to their content
            model_numbers: List of model numbers to process
            feature_type: Type of feature to process
            
        Returns:
            List[Feature]: The processed features
        """
        all_features = set()
        feature_models: Dict[str, Dict[str, bool]] = {}
        
        for name in model_numbers:
            if name not in models:
                continue
                
            model = models[name]
            if "Features_And_Advantages" not in model.sections:
                continue
                
            section = model.sections["Features_And_Advantages"]
            if feature_type not in section.categories:
                continue
                
            category = section.categories[feature_type]
            if not category.subcategories:
                continue
                
            # Get feature text
            spec = category.subcategories.get("")
            if not spec:
                continue
                
            # Split into individual features
            features = spec.value.split("\n")
            
            # Record each feature
            for feature in features:
                feature = feature.strip()
                if not feature:
                    continue
                    
                all_features.add(feature)
                if feature not in feature_models:
                    feature_models[feature] = {}
                feature_models[feature][name] = True
        
        # Create Feature objects
        return [
            Feature(
                text=feature,
                models={
                    name: feature_models.get(feature, {}).get(name, False)
                    for name in model_numbers
                }
            )
            for feature in sorted(all_features)
        ]
    
    def _process_specifications(
        self,
        models: Dict[str, PDFContent],
        model_numbers: List[str]
    ) -> Tuple[Dict[str, ComparisonSection], List[Difference]]:
        """Process specifications from all models.
        
        Args:
            models: Dictionary of model numbers to their content
            model_numbers: List of model numbers to process
            
        Returns:
            Tuple containing:
            - Dictionary of section name to comparison section
            - List of differences found
        """
        sections: Dict[str, ComparisonSection] = {}
        differences: List[Difference] = []
        
        # First collect all unique section/category combinations
        spec_combinations = []
        seen_combinations = set()
        
        # Process regular sections first
        for name in model_numbers:
            if name not in models:
                continue
                
            model = models[name]
            for section_name, section in model.sections.items():
                if section_name in ["Features_And_Advantages", "Diagram"]:
                    continue
                    
                # Initialize section if not exists
                if section_name not in sections:
                    sections[section_name] = ComparisonSection()
                    
                for category_name, category in section.categories.items():
                    for spec_name in category.subcategories.keys():
                        combination = (section_name, category_name, spec_name)
                        if combination not in seen_combinations:
                            spec_combinations.append(combination)
                            seen_combinations.add(combination)
        
        # Now process each combination
        for section_name, category_name, spec_name in spec_combinations:
            values: Dict[str, Specification] = {}
            has_differences = False
            
            # Collect values from each model
            for name in model_numbers:
                if name not in models:
                    continue
                    
                model = models[name]
                if section_name not in model.sections:
                    continue
                    
                section = model.sections[section_name]
                if category_name not in section.categories:
                    continue
                    
                category = section.categories[category_name]
                if spec_name not in category.subcategories:
                    continue
                    
                spec = category.subcategories[spec_name]
                values[name] = spec
            
            # Skip if no values found
            if not values:
                continue
                
            # Check for differences
            if len(values) > 1:
                value_set = {
                    (spec.value, spec.unit) for spec in values.values()
                }
                has_differences = len(value_set) > 1
            
            # Create comparison specification
            comparison = ComparisonSpecification(
                category=category_name,
                specification=spec_name,
                values=values,
                has_differences=has_differences
            )
            
            # Add to section
            if category_name not in sections[section_name].categories:
                sections[section_name].categories[category_name] = []
            sections[section_name].categories[category_name].append(comparison)
            
            # Record difference if found
            if has_differences:
                # Get the model with the most different value
                all_values = [
                    float(v.value) if v.value.replace('.','',1).isdigit() else v.value
                    for v in values.values()
                ]
                
                if all(isinstance(v, (int, float)) for v in all_values):
                    # For numeric values, find model with most extreme value
                    extreme_model = max(
                        values.items(),
                        key=lambda x: abs(float(x[1].value))
                    )[0]
                    difference_desc = f"Value of {max(all_values)} vs {min(all_values)}"
                else:
                    # For non-numeric values, take first model
                    extreme_model = next(iter(values.keys()))
                    other_values = [
                        v.value for k, v in values.items()
                        if k != extreme_model
                    ]
                    difference_desc = f"Value of {values[extreme_model].value} vs {', '.join(other_values)}"
                
                differences.append(Difference.create(
                    model=extreme_model,
                    category=section_name,
                    subcategory=category_name,
                    specification=spec_name,
                    difference=difference_desc,
                    unit=next(iter(values.values())).unit,
                    values={k: v.value for k, v in values.items()}
                ))
        
        return sections, differences 