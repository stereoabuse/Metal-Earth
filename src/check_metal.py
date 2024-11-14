import requests
import time
from typing import List, Dict
import csv
import re
import os
import sys

def load_proper_nouns(filename: str = "unique_proper_nouns.txt") -> List[str]:
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


def check_metal_archives(name: str) -> Dict:
    """
    Check if a band exists on Metal Archives.
    Returns only exact matches (case insensitive).
    """
    url = "https://www.metal-archives.com/search/ajax-band-search/"
    
    params = {
        'field': 'name',
        'query': name,
        'sEcho': 1,
        'iDisplayStart': 0,
        'iDisplayLength': 100
    }
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    try:
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        # Filter for exact matches only (case insensitive)
        exact_matches = []
        for band_data in data['aaData']:
            url_match = re.search(r'href="([^"]+)"', band_data[0])
            if url_match:
                band_name = re.sub(r'<[^>]+>', '', band_data[0]).strip()
                if band_name.lower().strip() == name.lower().strip():
                    exact_matches.append({
                        'name': band_name,
                        'url': url_match.group(1)
                    })
        
        return {
            'name': name,
            'exists': bool(exact_matches),
            'total_matches': len(exact_matches),
            'matches': exact_matches
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
    
def save_results(results: List[Dict], filename: str = "metal_band_matches.csv"):
    """Save results to a CSV file."""
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Search Name', 'Band Name', 'URL'])
        
        for result in results:
            if result.get('matches', []):
                # Write each match for names that have matches
                for match in result['matches']:
                    writer.writerow([
                        result['name'],
                        match['name'],
                        match['url']
                    ])
            else:
                # Write a row for names without any matches
                writer.writerow([
                    result['name'],
                    'No match found',
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
        
        time.sleep(0.3)  # Reduced sleep time
        
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
    print("Results have been saved to 'metal_band_matches.csv'")

if __name__ == "__main__":
    main()