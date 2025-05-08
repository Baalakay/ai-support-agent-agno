"""Data models for PDF processing."""
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field

@dataclass
class Specification:
    """Specification model.
    
    Represents a specification with its value, unit, and display format.
    
    Attributes:
        value: The specification value
        unit: Optional unit of measurement
        display_value: Optional formatted display value
    """
    value: str
    unit: Optional[str] = None
    display_value: Optional[str] = None

    def __post_init__(self):
        if self.display_value is None:
            self.display_value = self.value

@dataclass
class Category:
    """Category model.
    
    Represents a category containing specifications.
    
    Attributes:
        name: The category name
        subcategories: Dictionary of specification name to specification
    """
    name: str
    subcategories: Dict[str, Specification] = field(default_factory=dict)

    def add_specification(self, name: str, specification: Specification) -> None:
        """Add a specification to the category."""
        self.subcategories[name] = specification

@dataclass
class Section:
    """Section model.
    
    Represents a section containing categories.
    
    Attributes:
        name: The section name
        categories: Dictionary of category name to category
    """
    name: str
    categories: Dict[str, Category] = field(default_factory=dict)

    def add_category(self, name: str) -> Category:
        """Add a category to the section if it doesn't exist."""
        if name not in self.categories:
            self.categories[name] = Category(name=name)
        return self.categories[name]

@dataclass
class Page:
    """Page model.
    
    Represents a page in the PDF.
    
    Attributes:
        page_number: The page number
        raw_text: The raw text content of the page
    """
    page_number: int
    raw_text: str

@dataclass
class PDFContent:
    """PDF content model.
    
    Represents the content of a PDF document.
    
    Attributes:
        filename: The PDF filename
        model_number: Optional model number extracted from the filename
        raw_text: Raw text content of the PDF
        pages: List of pages in the PDF
        sections: Dictionary of section name to section
    """
    filename: str
    model_number: Optional[str] = None
    raw_text: str = ""
    pages: List[Page] = field(default_factory=list)
    sections: Dict[str, Section] = field(default_factory=dict)

    def add_page(self, page_number: int, raw_text: str) -> Page:
        """Add a page to the PDF content."""
        page = Page(page_number=page_number, raw_text=raw_text)
        self.pages.append(page)
        return page

    def add_section(self, name: str) -> Section:
        """Add a section to the PDF content if it doesn't exist."""
        if name not in self.sections:
            self.sections[name] = Section(name=name)
        return self.sections[name]

    def get_specification(self, section_name: str, category_name: str, specification_name: str) -> Optional[Specification]:
        """Get a specification by section, category, and name.
        
        Args:
            section_name: The section name
            category_name: The category name
            specification_name: The specification name
            
        Returns:
            Optional[Specification]: The specification if found, None otherwise
            
        Raises:
            KeyError: If the section, category, or specification is not found
        """
        if section_name not in self.sections:
            raise KeyError(f"Section '{section_name}' not found")
        
        section = self.sections[section_name]
        if category_name not in section.categories:
            raise KeyError(f"Category '{category_name}' not found in section '{section_name}'")
        
        category = section.categories[category_name]
        if specification_name not in category.subcategories:
            raise KeyError(f"Specification '{specification_name}' not found in category '{category_name}'")
        
        return category.subcategories[specification_name] 