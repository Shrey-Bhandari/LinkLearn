"""Content extraction engine for educational webpages."""

from typing import Optional
from bs4 import BeautifulSoup, Tag
from pydantic import BaseModel


class Section(BaseModel):
    """Represents a section with heading and content."""
    heading: str
    content: str
    level: Optional[int] = None


class ExtractedContent(BaseModel):
    """Represents extracted educational content."""
    title: Optional[str] = None
    sections: list[Section] = []


class ContentExtractor:
    """Extract meaningful educational content from HTML."""
    
    # Tags to completely remove from the document
    REMOVAL_TAGS = {
        'nav', 'footer', 'script', 'style', 'noscript', 
        'meta', 'link', 'header', 'aside',
        'iframe', 'form', 'button'
    }
    
    # Common ad/banner class/id patterns
    AD_PATTERNS = {
        'ad', 'advertisement', 'banner', 'sponsor', 'promo',
        'popup', 'modal', 'sidebar', 'widget', 'social'
    }
    
    # Heading tags we care about
    HEADING_TAGS = {'h1', 'h2', 'h3'}
    
    def __init__(self, html: str):
        """Initialize extractor with HTML content."""
        self.soup = BeautifulSoup(html, 'html.parser')
        self._remove_unwanted_elements()
    
    def _remove_unwanted_elements(self) -> None:
        """Remove navigation, ads, scripts, and other non-educational content."""
        # Remove by tag
        for tag_name in self.REMOVAL_TAGS:
            for tag in self.soup.find_all(tag_name):
                tag.decompose()
        
        # Remove common ad/banner patterns by class and id
        for element in self.soup.find_all(class_=True):
            if self._is_ad_element(element.get('class', [])):
                element.decompose()
        
        for element in self.soup.find_all(id=True):
            if self._is_ad_element([element.get('id', '')]):
                element.decompose()
    
    def _is_ad_element(self, classes_or_ids: list) -> bool:
        """Check if element matches ad patterns."""
        combined = ' '.join(str(c).lower() for c in classes_or_ids)
        return any(pattern in combined for pattern in self.AD_PATTERNS)
    
    def _extract_text(self, element: Tag) -> str:
        """Extract and clean text from element."""
        text = element.get_text(separator=' ', strip=True)
        # Clean up multiple spaces
        text = ' '.join(text.split())
        return text
    
    def extract(self) -> ExtractedContent:
        """Extract educational content and return structured data."""
        result = ExtractedContent()
        
        # Extract title
        title_tag = self.soup.find('title')
        if title_tag:
            result.title = self._extract_text(title_tag)
        else:
            # Fallback to h1
            h1 = self.soup.find('h1')
            if h1:
                result.title = self._extract_text(h1)
        
        # Extract sections with headings and content
        current_heading = None
        current_content = []
        
        for element in self.soup.find_all(['h1', 'h2', 'h3', 'p']):
            if element.name in self.HEADING_TAGS:
                # Save previous section if exists
                if current_heading and current_content:
                    content_text = ' '.join(current_content).strip()
                    if content_text:
                        result.sections.append(
                            Section(
                                heading=current_heading,
                                content=content_text,
                                level=current_level
                            )
                        )
                
                # Start new section
                current_heading = self._extract_text(element)
                current_level = int(element.name[1])
                current_content = []
            
            elif element.name == 'p' and current_heading:
                # Add paragraph to current section
                para_text = self._extract_text(element)
                if para_text:
                    current_content.append(para_text)
        
        # Don't forget the last section
        if current_heading and current_content:
            content_text = ' '.join(current_content).strip()
            if content_text:
                result.sections.append(
                    Section(heading=current_heading, content=content_text)
                )
        
        return result
