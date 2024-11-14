import requests
import time
from typing import List, Dict
import csv
import re
import os
import sys

def load_proper_nouns(filename: str = "reports/unique_proper_nouns.txt") -> List[str]:
    """Load the proper nouns from the file, skipping header lines."""
    try:
        if not os.path.exists(filename):
            print(f"Error: {filename} not found!")
            print("Please run extract_nouns.py first to generate the list of proper nouns.")
            sys.exit(1)
            
        nouns = []
        with open(filename, 'r', encoding='utf-8') as f:
            for line in f:
                # Skip empty lines and lines starting with =
                if line.strip() and not line.startswith('='):
                    nouns.append(line.strip())
        
        if not nouns:
            print(f"Error: No proper nouns found in {filename}")
            print("Please run extract_nouns.py first to generate proper nouns.")
            sys.exit(1)
            
        return nouns
            
    except Exception as e:
        print(f"Error loading proper nouns from {filename}: {e}")
        sys.exit(1)

def load_gateway_pages(filename: str = "data/external-sources/tolkien_gateway_pages.txt") -> List[str]:
    """Load the Tolkien Gateway pages from the file."""
    try:
        if not os.path.exists(filename):
            print(f"Warning: {filename} not found!")
            return []
            
        pages = []
        with open(filename, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    pages.append(line.strip())
        return pages
            
    except Exception as e:
        print(f"Error loading gateway pages from {filename}: {e}")
        return []

def combine_search_terms(verbose: bool = True) -> List[str]:
    """Combine proper nouns and Gateway pages into a single deduplicated list."""
    proper_nouns = load_proper_nouns()
    gateway_pages = load_gateway_pages()
    
    if verbose:
        print(f"Loaded {len(proper_nouns)} proper nouns")
        print(f"Loaded {len(gateway_pages)} gateway pages")
    
    # Combine and deduplicate
    combined_terms = list(set(proper_nouns + gateway_pages))
    
    # Sort alphabetically
    combined_terms.sort()
    
    if verbose:
        print(f"Final combined list contains {len(combined_terms)} terms")
    
    return combined_terms


def get_band_details(url: str, headers: dict) -> dict:
    """Get detailed information about a band from their Metal Archives page."""
    try:
        time.sleep(.1)  # Respect rate limiting
        
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        html = response.text
        
        details = {}
        
        # Patterns that match Metal Archives' HTML structure
        patterns = {
            'genre': r'<dt>Genre:</dt>\s*<dd>(.*?)</dd>',
            'themes': r'<dt>Themes:</dt>\s*<dd>(.*?)</dd>',
            'country': r'<dt>Country of origin:</dt>\s*<dd>.*?>(.*?)</a>',
            'location': r'<dt>Location:</dt>\s*<dd>(.*?)</dd>',
            'status': r'<dt>Status:</dt>\s*<dd>(.*?)</dd>',
            'formed': r'<dt>Formed in:</dt>\s*<dd>(.*?)</dd>'
        }
        
        for key, pattern in patterns.items():
            match = re.search(pattern, html, re.DOTALL | re.IGNORECASE)
            if match:
                value = match.group(1)
                value = re.sub(r'<[^>]+>', '', value)  # Remove any nested HTML
                value = re.sub(r'\s+', ' ', value)     # Normalize whitespace
                value = value.strip()
                details[key] = value if value else 'N/A'
            else:
                details[key] = 'N/A'
                
        return details
        
    except requests.exceptions.RequestException as e:
        print(f"Network error getting band details from {url}: {str(e)}")
        return {k: 'Error' for k in ['genre', 'themes', 'country', 'location', 'status', 'formed']}
    except Exception as e:
        print(f"Error parsing band details from {url}: {str(e)}")
        return {k: 'Error' for k in ['genre', 'themes', 'country', 'location', 'status', 'formed']}

def check_metal_archives(name: str) -> Dict:
    """Check if a band exists on Metal Archives."""
    base_url = "https://www.metal-archives.com/search/ajax-band-search/"
    
    params = {
        'field': 'name',
        'query': name,
        'sEcho': 1,
        'iDisplayStart': 0,
        'iDisplayLength': 100
    }
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'X-Requested-With': 'XMLHttpRequest'
    }
    
    try:
        time.sleep(.1)  # Respect rate limiting
        
        response = requests.get(base_url, params=params, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        exact_matches = []
        for band_data in data['aaData']:
            url_match = re.search(r'href="([^"]+)"', band_data[0])
            if url_match:
                band_name = re.sub(r'<[^>]+>', '', band_data[0]).strip()
                if band_name.lower().strip() == name.lower().strip():
                    band_url = url_match.group(1)
                    print(f"Getting details for {band_name} from {band_url}")
                    details = get_band_details(band_url, headers)
                    exact_matches.append({
                        'name': band_name,
                        'url': band_url,
                        **details
                    })
        
        return {
            'name': name,
            'exists': bool(exact_matches),
            'total_matches': len(exact_matches),
            'matches': exact_matches
        }
    
    except requests.exceptions.RequestException as e:
        print(f"Network error checking {name}: {str(e)}")
        return {
            'name': name,
            'exists': False,
            'total_matches': 0,
            'matches': [],
            'error': f"Network error: {str(e)}"
        }
    except Exception as e:
        print(f"Error checking {name}: {str(e)}")
        return {
            'name': name,
            'exists': False,
            'total_matches': 0,
            'matches': [],
            'error': str(e)
        }

def save_results(results: List[Dict], filename: str = "reports/metal_band_matches.csv"):
    """Save results to a CSV file."""
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([
            'Search Name',
            'Band Name',
            'URL',
            'Genre',
            'Themes',
            'Country',
            'Location',
            'Status',
            'Formed'
        ])
        
        for result in results:
            if result.get('matches', []):
                for match in result['matches']:
                    writer.writerow([
                        result['name'],
                        match['name'],
                        match['url'],
                        match.get('genre', 'N/A'),
                        match.get('themes', 'N/A'),
                        match.get('country', 'N/A'),
                        match.get('location', 'N/A'),
                        match.get('status', 'N/A'),
                        match.get('formed', 'N/A')
                    ])
            else:
                writer.writerow([
                    result['name'],
                    'No match found',
                    '',
                    '',
                    '',
                    '',
                    '',
                    '',
                    ''
                ])
def main():
    print("Loading and combining search terms...")
    search_terms = combine_search_terms()
    print(f"Loaded {len(search_terms)} names to check")
    
    results = []
    total = len(search_terms)
    
    print("\nChecking names against Metal Archives...")
    # This will take a while
    for i, name in enumerate(search_terms, 1):
        print(f"Checking {name} ({i}/{total})...")
        
        result = check_metal_archives(name)
        results.append(result)
        
        if result['exists']:
            print(f"Found {result['total_matches']} matching bands:")
            for match in result['matches']:
                print(f"  - {match['name']}")  # Removed match_type reference
        
        time.sleep(0.1)  # Reduced sleep time
        
        # Save progress every 10 names
        if i % 10 == 0:
            print(f"\nSaving progress... ({i}/{total} names processed)")
            save_results(results)
    
    print("\nSaving final results...")
    save_results(results)
    
    # Count matches
    exact_matches = sum(1 for r in results for m in r.get('matches', []))
    
    print(f"\nFinished checking {total} names")
    print(f"Found {exact_matches} exact matches")
    print("Results have been saved to 'reports/metal_band_matches.csv'")

if __name__ == "__main__":
    main()