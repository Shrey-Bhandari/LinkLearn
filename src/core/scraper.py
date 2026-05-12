import re
from typing import List
from urllib.parse import urlparse
from pydantic import BaseModel
import httpx
from .extractor import ContentExtractor


class ScraperError(Exception):
    pass


class SectionData(BaseModel):
    heading: str
    content: str
    level: int | None = None


class PageContent(BaseModel):
    url: str
    title: str | None = None
    sections: List[SectionData] = []


class URLScraper:
    """Fetch and clean educational content from a URL."""

    DEFAULT_HEADERS = {
        "User-Agent": "Link2Learn/1.0 (+https://github.com/LinkLearn)"
    }

    def __init__(self, timeout: int = 30, max_html_size: int = 10 * 1024 * 1024):
        self.timeout = timeout
        self.max_html_size = max_html_size

    def fetch_html(self, url: str) -> str:
        """Fetch HTML content from a URL with basic error handling."""
        try:
            with httpx.Client(timeout=self.timeout, follow_redirects=True) as client:
                response = client.get(url, headers=self.DEFAULT_HEADERS)
        except httpx.RequestError as exc:
            raise ScraperError(f"Failed to fetch URL {url}: {exc}") from exc

        if response.status_code != 200:
            raise ScraperError(
                f"Unexpected status code {response.status_code} for URL {url}"
            )

        if len(response.text) > self.max_html_size:
            raise ScraperError(
                f"Page size exceeds limit ({len(response.text)} bytes) for {url}"
            )

        return response.text

    def scrape_url(self, url: str) -> PageContent:
        """Scrape the URL and return cleaned, structured page content."""
        html = self.fetch_html(url)
        content = self.extract_content(html)
        if not content.title and not content.sections:
            raise ScraperError(f"No educational content found at {url}")

        content.url = url
        return content

    def extract_content(self, html: str) -> PageContent:
        """Extract the title and sections from HTML content."""
        extractor = ContentExtractor(html)
        extracted = extractor.extract()

        sections = [
            SectionData(
                heading=section.heading,
                content=self._normalize_text(section.content),
                level=section.level,
            )
            for section in extracted.sections
            if section.heading and section.content
        ]

        sections = self._dedupe_sections(sections)
        return PageContent(
            url="",
            title=self._normalize_text(extracted.title) if extracted.title else None,
            sections=sections,
        )

    def _normalize_text(self, text: str) -> str:
        """Normalize whitespace and remove redundant line breaks."""
        if not text:
            return ""
        normalized = re.sub(r"\s+", " ", text).strip()
        return normalized

    def _dedupe_sections(self, sections: List[SectionData]) -> List[SectionData]:
        """Remove duplicate headings or duplicate content blocks."""
        seen = set()
        unique_sections: List[SectionData] = []

        for section in sections:
            fingerprint = f"{section.heading.lower()}|{section.content.lower()}"
            if fingerprint in seen:
                continue
            seen.add(fingerprint)
            unique_sections.append(section)

        return unique_sections
