import requests
import json
import time
from typing import List, Dict
import csv
import re
import os
import sys
from fuzzy_search import are_similar

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
def check_metal_archives(name: str) -> Dict:
    """
    Check if a band exists on Metal Archives, including fuzzy matches.
    Returns a dictionary with search results and status.
    """
    # First try exact match
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
        # Get exact matches
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()
        data = response.json()
        exact_matches = data['aaData']
        
        # Try fuzzy search for similar names
        fuzzy_matches = []
        if data['iTotalRecords'] < 100:  # Only do fuzzy search if we don't have too many exact matches
            # Get a broader search to check for similar names
            fuzzy_params = params.copy()
            # Remove any special characters and try partial match
            fuzzy_params['query'] = re.sub(r'[^a-zA-Z]', '', name)
            fuzzy_response = requests.get(url, params=fuzzy_params, headers=headers)
            fuzzy_data = fuzzy_response.json()
            
            # Check each result for similarity
            for band_data in fuzzy_data['aaData']:
                band_name = re.sub(r'<[^>]+>', '', band_data[0])  # Remove HTML tags
                if band_data not in exact_matches and are_similar(name, band_name):
                    fuzzy_matches.append(band_data)
        
        # Extract URLs and combine results
        all_matches = []
        for band_data in (exact_matches + fuzzy_matches):
            url_match = re.search(r'href="([^"]+)"', band_data[0])
            if url_match:
                band_name = re.sub(r'<[^>]+>', '', band_data[0])
                all_matches.append({
                    'name': band_name,
                    'url': url_match.group(1),
                    'match_type': 'exact' if band_data in exact_matches else 'similar'
                })
        
        return {
            'name': name,
            'exists': bool(all_matches),
            'total_matches': len(all_matches),
            'matches': all_matches
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
        writer.writerow(['Search Name', 'Band Name', 'URL', 'Match Type'])
        
        for result in results:
            for match in result.get('matches', []):
                writer.writerow([
                    result['name'],
                    match['name'],
                    match['url'],
                    match['match_type']
                ])

def main():
    print("Loading proper nouns...")
    nouns = load_proper_nouns()
    print(f"Loaded {len(nouns)} names to check")
    
    results = []
    total = len(nouns)
    
    print("\nChecking names against Metal Archives...")
    for i, name in enumerate(nouns, 1):
        print(f"Checking {name} ({i}/{total})...")
        
        result = check_metal_archives(name)
        results.append(result)
        
        if result['exists']:
            print(f"Found {result['total_matches']} matching bands:")
            for match in result['matches']:
                print(f"  - {match['name']} ({match['match_type']} match)")
        
        time.sleep(0.5)  # Reduced sleep time
        
        # Save progress every 20 names
        if i % 20 == 0:
            print(f"\nSaving progress... ({i}/{total} names processed)")
            save_results(results)
    
    print("\nSaving final results...")
    save_results(results)
    
    # Count exact and similar matches
    exact_matches = sum(1 for r in results for m in r.get('matches', []) if m['match_type'] == 'exact')
    similar_matches = sum(1 for r in results for m in r.get('matches', []) if m['match_type'] == 'similar')
    
    print(f"\nFinished checking {total} names")
    print(f"Found {exact_matches} exact matches and {similar_matches} similar matches")
    print("Results have been saved to 'metal_band_matches.csv'")

if __name__ == "__main__":
    main()