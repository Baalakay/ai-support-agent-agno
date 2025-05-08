"""Service for processing PDF documents."""

import re
import os
import fitz  # PyMuPDF
import pdfplumber
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple

from .config import get_config
from ..transformers import format_display_value, standardize_unit
from ..models.pdf import (
    PDFContent, Specification, Category, Section, Page
)

logger = logging.getLogger(__name__)


class PDFProcessorError(Exception):
    """Base error for PDF processing operations."""
    pass


class PDFProcessor:
    """Service for processing PDF documents.
    
    This component is part of the Processing Layer and is responsible for
    extracting and processing content from PDF documents.
    """
    
    def __init__(self, data_dir: Optional[Path] = None):
        """Initialize the processor.
        
        Args:
            data_dir: Optional directory containing PDF files
        """
        self.config = get_config()
        self.data_dir = data_dir or Path(self.config.get("pdf_dir", "data/pdfs"))
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Configure section patterns
        self.section_patterns = {
            'electrical': 'electrical specifications',
            'magnetic': 'magnetic specifications',
            'physical': 'physical/operational specifications'
        }
        self.section_order = ["electrical", "magnetic", "physical"]
    
    async def get_content(self, model_number: str) -> PDFContent:
        """Get content for a specific model number.
        
        Args:
            model_number: The model number to get content for
            
        Returns:
            PDFContent: The processed PDF content
            
        Raises:
            FileNotFoundError: If no PDF found for model number
            PDFProcessorError: If PDF processing fails
        """
        try:
            # Find PDF file
            pdf_path = self._find_pdf_file(model_number)
            if not pdf_path:
                raise FileNotFoundError(f"No PDF found for model {model_number}")
            
            # Extract content
            content = self._extract_content(pdf_path)
            
            # Extract and save diagram if configured
            self._extract_diagram(content)
            
            return content
            
        except FileNotFoundError:
            raise
        except Exception as e:
            logger.error(f"Failed to process PDF for model {model_number}: {str(e)}")
            raise PDFProcessorError(f"Failed to process PDF: {str(e)}")
    
    def _find_pdf_file(self, model_number: str) -> Optional[Path]:
        """Find a PDF file for the given model number.
        
        Args:
            model_number: The model number to find
            
        Returns:
            Optional[Path]: The PDF file path if found
        """
        # Check if the directory exists
        if not self.data_dir.exists():
            return None
        
        # Look for exact match first
        for pdf_file in self.data_dir.glob("*.pdf"):
            if model_number.lower() in pdf_file.stem.lower():
                return pdf_file
        
        # If no exact match, try to find a file with a similar name
        for pdf_file in self.data_dir.glob("*.pdf"):
            # Extract model number from filename
            extracted = self._extract_model_name(pdf_file.stem)
            if extracted and extracted.lower() == model_number.lower():
                return pdf_file
        
        return None
    
    def _extract_model_name(self, filename: str) -> Optional[str]:
        """Extract model number from filename.
        
        Args:
            filename: The filename to extract from
            
        Returns:
            Optional[str]: The extracted model number
        """
        # Remove extension and split on underscores/spaces
        base_name = Path(filename).stem
        
        # First try to find HSR-\d+ pattern
        hsr_match = re.search(r'HSR-?(\d+[RFW]?)', base_name, re.IGNORECASE)
        if hsr_match:
            return hsr_match.group(1).upper()
        
        # Then try just the number with optional suffix
        parts = re.split(r'[_\s]', base_name)
        for part in parts:
            # Basic pattern: digits followed by optional R/F/W
            if re.match(r'^\d+[RFW]?$', part, re.IGNORECASE):
                return part.upper()
        
        # If no match found and input is just digits, use that
        if base_name.isdigit():
            return base_name
        
        return None
    
    def _extract_content(self, pdf_path: Path) -> PDFContent:
        """Extract content from a PDF file.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            PDFContent: The extracted content
            
        Raises:
            PDFProcessorError: If content extraction fails
        """
        try:
            # Extract model number from filename
            model_name = self._extract_model_name(pdf_path.stem)
            
            # Create initial content
            content = PDFContent(
                filename=pdf_path.name,
                model_number=model_name
            )
            
            # Extract text and tables
            with pdfplumber.open(pdf_path) as pdf:
                for i, page in enumerate(pdf.pages):
                    # Extract text
                    text = page.extract_text() or ""
                    content.add_page(i + 1, text)
                    
                    # Extract tables
                    tables = [
                        [[str(cell) if cell else '' for cell in row] for row in table]
                        for table in page.extract_tables()
                    ]
                    
                    # Process features and advantages
                    if i == 0:  # Only process first page
                        features_advantages = self._extract_features_advantages(page)
                        if features_advantages:
                            content.sections.update(features_advantages)
                    
                    # Process specification tables
                    specs = self._process_tables(tables)
                    if specs:
                        for section_name, section_data in specs.items():
                            if section_name not in content.sections:
                                content.sections[section_name] = Section(name=section_name)
                            section = content.sections[section_name]
                            
                            for category_name, category_data in section_data.items():
                                category = section.add_category(category_name)
                                
                                for subcategory_name, subcategory_data in category_data.items():
                                    subcategory = Category(name=subcategory_name)
                                    category.subcategories[subcategory_name] = subcategory
                                    
                                    for spec_name, spec_data in subcategory_data.items():
                                        value = format_display_value(spec_data["value"])
                                        unit = standardize_unit(spec_data.get("unit"))
                                        spec = Specification(name=spec_name, value=value, unit=unit)
                                        subcategory.add_specification(spec_name, spec)
            
            return content
            
        except Exception as e:
            logger.error(f"Failed to extract content from {pdf_path}: {str(e)}")
            raise PDFProcessorError(f"Failed to extract content: {str(e)}")
    
    def _extract_features_advantages(
        self,
        page: Any
    ) -> Optional[Dict[str, Section]]:
        """Extract features and advantages from a page.
        
        Args:
            page: The PDF page to extract from
            
        Returns:
            Optional[Dict[str, Section]]: The extracted features and advantages
        """
        try:
            features: List[str] = []
            advantages: List[str] = []
            
            # Extract features from left box
            feat_box = (0, 130, 295, 210)
            feat_area = page.within_bbox(feat_box)
            feat_text = feat_area.extract_text()
            if feat_text:
                for line in feat_text.split('\n'):
                    line = line.strip()
                    if line and line.lower() != 'features':
                        features.append(line)
            
            # Extract advantages from right box
            adv_box = (300, 130, 610, 210)
            adv_area = page.within_bbox(adv_box)
            adv_text = adv_area.extract_text()
            if adv_text:
                for line in adv_text.split('\n'):
                    line = line.strip()
                    if line and line.lower() != 'advantages':
                        advantages.append(line)
            
            if not features and not advantages:
                return None
            
            # Create section structure
            section = Section(name="Features_And_Advantages")
            
            if features:
                category = Category(name="features")
                spec = Specification(value='\n'.join(features))
                category.add_specification("", spec)
                section.add_category("features")
                section.categories["features"] = category
            
            if advantages:
                category = Category(name="advantages")
                spec = Specification(value='\n'.join(advantages))
                category.add_specification("", spec)
                section.add_category("advantages")
                section.categories["advantages"] = category
            
            return {"Features_And_Advantages": section}
            
        except Exception as e:
            logger.warning(f"Failed to extract features/advantages: {str(e)}")
            return None
    
    def _process_tables(
        self,
        tables: List[List[List[str]]]
    ) -> Dict[str, Dict[str, Dict[str, Dict[str, Dict[str, Any]]]]]:
        """Process specification tables.
        
        Args:
            tables: List of tables to process
            
        Returns:
            Dict: The processed specifications
        """
        sections: Dict[str, Dict[str, Dict[str, Dict[str, Dict[str, Any]]]]] = {}
        
        for table in tables:
            if not table:  # Skip empty tables
                continue
            
            # Clean first row
            first_row = [str(col).strip() if col else "" for col in table[0]]
            
            # Skip features/advantages table
            if (len(first_row) == 2 and
                    "Features" in first_row[0] and
                    "Advantages" in first_row[1]):
                continue
            
            # Process table into specifications
            specs = self._parse_table(table)
            if specs:
                for section_name, section_data in specs.items():
                    if section_name not in sections:
                        sections[section_name] = {}
                    sections[section_name].update(section_data)
        
        return sections
    
    def _parse_table(
        self,
        table: List[List[str]]
    ) -> Dict[str, Dict[str, Dict[str, Dict[str, Dict[str, Any]]]]]:
        """Parse a table into specifications.
        
        Args:
            table: The table to parse
            
        Returns:
            Dict: The parsed specifications
        """
        if not table:  # Empty table
            return {}
        
        specs: Dict[str, Dict[str, Dict[str, Dict[str, Dict[str, Any]]]]] = {}
        current_category: Optional[str] = None
        current_section: Optional[str] = None
        
        # Process rows
        for row in table[1:]:  # Skip header row
            try:
                # Clean row data
                row_data = [str(cell).strip() if cell else "" for cell in row]
                
                if not any(row_data):  # Skip empty rows
                    continue
                
                # Get category and subcategory
                category = row_data[0] if row_data[0] else current_category
                subcategory = row_data[1] if len(row_data) > 1 and row_data[1] else ""
                
                if category and isinstance(category, str):
                    current_category = category
                    # Determine section
                    section_name = self._get_section_for_category(category, current_section)
                    current_section = section_name
                    
                    # Initialize section structure
                    if section_name not in specs:
                        specs[section_name] = {
                            "categories": {}
                        }
                    if category not in specs[section_name]["categories"]:
                        specs[section_name]["categories"][category] = {
                            "subcategories": {}
                        }
                
                # Get unit and value
                if len(row_data) > 3 and current_section and current_category:
                    raw_unit = row_data[2].strip() if row_data[2] else None
                    value = row_data[3].strip()
                    
                    # Create specification
                    unit = standardize_unit(raw_unit)
                    spec = {
                        "value": value,
                        "unit": unit,
                        "display_value": format_display_value(value, unit)
                    }
                    
                    # Add to structure
                    specs[current_section]["categories"][current_category]["subcategories"][subcategory] = spec
                    
            except (ValueError, IndexError) as e:
                logger.warning(f"Failed to parse table row: {str(e)}")
                continue
        
        return specs
    
    def _get_section_for_category(
        self,
        category: str,
        current_section: Optional[str] = None
    ) -> str:
        """Determine the section for a category.
        
        Args:
            category: The category to classify
            current_section: Optional current section
            
        Returns:
            str: The determined section name
        """
        category_lower = category.lower()
        
        # Electrical section categories
        if any(term in category_lower for term in [
            'power', 'voltage', 'current', 'resistance', 'capacitance',
            'temperature', 'electrical'
        ]):
            return self.section_patterns['electrical']
        
        # Magnetic section categories
        elif any(term in category_lower for term in [
            'pull - in', 'test coil', 'magnetic'
        ]):
            return self.section_patterns['magnetic']
        
        # Physical section categories
        elif any(term in category_lower for term in [
            'capsule', 'contact material', 'operate time', 'release time',
            'physical', 'operational'
        ]):
            return self.section_patterns['physical']
        
        # If no match found, use current section or first section as default
        return current_section or self.section_patterns[self.section_order[0]]
    
    def _extract_diagram(self, content: PDFContent) -> None:
        """Extract and save diagram from PDF content.
        
        Args:
            content: The PDF content to extract from
        """
        try:
            if not content.model_number:
                return
            
            # Get diagram directory from config
            diagram_dir = self.config.get(
                "diagram_dir",
                os.path.join(os.path.dirname(str(self.data_dir)), "diagrams")
            )
            
            # Ensure diagram directory exists
            os.makedirs(diagram_dir, exist_ok=True)
            
            # Extract diagram using PyMuPDF
            diagram_path = Path(diagram_dir) / f"{content.model_number}.png"
            if not diagram_path.exists():
                try:
                    doc = fitz.open(str(self.data_dir / content.filename))
                    page = doc[0]  # First page
                    
                    # Get the diagram area (top-right corner)
                    rect = fitz.Rect(300, 0, 600, 120)
                    
                    # Extract image
                    pix = page.get_pixmap(clip=rect)
                    pix.save(str(diagram_path))
                    doc.close()
                except Exception as e:
                    logger.warning(f"Failed to extract diagram: {str(e)}")
                    return
            
            # Add diagram section if image exists
            if diagram_path.exists():
                if "Diagram" not in content.sections:
                    section = Section(name="Diagram")
                    content.sections["Diagram"] = section
                    
                    category = Category(name="")
                    section.add_category("")
                    section.categories[""] = category
                    
                    spec = Specification(value=str(diagram_path))
                    category.add_specification("", spec)
                    
        except Exception as e:
            logger.warning(f"Failed to handle diagram: {str(e)}") 