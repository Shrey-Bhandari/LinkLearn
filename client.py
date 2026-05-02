"""Simple client to interact with the content extraction API."""

import requests
import json
import sys
from pathlib import Path


def extract_from_url(url: str, api_url: str = "http://localhost:8000"):
    """Fetch HTML from URL and extract content via API."""
    try:
        # Fetch the webpage
        print(f"Fetching content from {url}...")
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        html_content = response.text
        print(f"HTML fetched: {len(html_content)} characters")
        
        # Send to extraction API
        print("\nSending to extraction API...")
        extract_response = requests.post(
            f"{api_url}/extract",
            json={"html": html_content},
            timeout=10
        )
        extract_response.raise_for_status()
        
        result = extract_response.json()
        return result
    
    except requests.exceptions.ConnectionError:
        print(f"Error: Cannot connect to API at {api_url}")
        print("Make sure the API is running: python main.py")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)


def extract_from_file(file_path: str, api_url: str = "http://localhost:8000"):
    """Read HTML from file and extract content via API."""
    try:
        print(f"Reading HTML from {file_path}...")
        with open(file_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        print(f"HTML read: {len(html_content)} characters")
        
        # Send to extraction API
        print("\nSending to extraction API...")
        response = requests.post(
            f"{api_url}/extract",
            json={"html": html_content},
            timeout=10
        )
        response.raise_for_status()
        
        result = response.json()
        return result
    
    except FileNotFoundError:
        print(f"Error: File not found: {file_path}")
        sys.exit(1)
    except requests.exceptions.ConnectionError:
        print(f"Error: Cannot connect to API at {api_url}")
        print("Make sure the API is running: python main.py")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)


def extract_from_string(html_string: str, api_url: str = "http://localhost:8000"):
    """Extract content from HTML string via API."""
    try:
        response = requests.post(
            f"{api_url}/extract",
            json={"html": html_string},
            timeout=10
        )
        response.raise_for_status()
        result = response.json()
        return result
    
    except requests.exceptions.ConnectionError:
        print(f"Error: Cannot connect to API at {api_url}")
        print("Make sure the API is running: python main.py")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)


def print_result(result: dict):
    """Pretty print extracted content."""
    print("\n" + "="*60)
    print("EXTRACTED CONTENT")
    print("="*60)
    
    if result.get("title"):
        print(f"\nTitle: {result['title']}")
    
    print(f"\nNumber of sections: {len(result.get('sections', []))}")
    
    for i, section in enumerate(result.get('sections', []), 1):
        print(f"\n--- Section {i} ---")
        print(f"Heading: {section['heading']}")
        print(f"Content: {section['content'][:200]}..." if len(section['content']) > 200 
              else f"Content: {section['content']}")


def save_result(result: dict, output_file: str):
    """Save extracted content to JSON file."""
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    print(f"\nResult saved to: {output_file}")


def main():
    """Main client function."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Client for Content Extraction API"
    )
    parser.add_argument(
        "--url",
        help="Extract from web URL"
    )
    parser.add_argument(
        "--file",
        help="Extract from HTML file"
    )
    parser.add_argument(
        "--api",
        default="http://localhost:8000",
        help="API base URL (default: http://localhost:8000)"
    )
    parser.add_argument(
        "--output",
        help="Save result to JSON file"
    )
    
    args = parser.parse_args()
    
    if not args.url and not args.file:
        print("Usage: python client.py [--url URL | --file FILE] [--output OUTPUT] [--api API_URL]")
        print("\nExamples:")
        print("  python client.py --url https://example.com/article")
        print("  python client.py --file example.html --output result.json")
        print("  python client.py --url https://example.com --api http://localhost:8000")
        sys.exit(1)
    
    # Extract content
    if args.url:
        result = extract_from_url(args.url, args.api)
    else:
        result = extract_from_file(args.file, args.api)
    
    # Print result
    print_result(result)
    
    # Save if requested
    if args.output:
        save_result(result, args.output)


if __name__ == "__main__":
    main()
