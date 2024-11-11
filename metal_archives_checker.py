import requests
import json
import time
from typing import List, Dict
import csv
import re

def load_proper_nouns(filename: str = "unique_proper_nouns.txt") -> List[str]:
    """Load the proper nouns from the file, skipping header lines."""
    nouns = []
    with open(filename, 'r', encoding='utf-8') as f:
        # Skip header lines
        for line in f:
            if line.startswith('='):
                break
        # Read actual nouns
        for line in f:
            noun = line.strip()
            if noun:  # Skip empty lines
                nouns.append(noun)
    return nouns

def extract_url_from_html(html_string: str) -> str:
    """Extract the URL from an HTML anchor tag."""
    match = re.search(r'href="([^"]+)"', html_string)
    return match.group(1) if match else ''

def check_metal_archives(name: str) -> Dict:
    """
    Check if a band exists on Metal Archives.
    Returns a dictionary with search results and status.
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
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        # Extract URLs from the HTML in the response
        bands_with_urls = []
        if data['aaData']:
            for band_data in data['aaData']:
                url = extract_url_from_html(band_data[0])
                bands_with_urls.append(url)
        
        return {
            'name': name,
            'exists': data['iTotalRecords'] > 0,
            'total_matches': data['iTotalRecords'],
            'urls': bands_with_urls
        }
    
    except Exception as e:
        print(f"Error checking {name}: {str(e)}")
        return {
            'name': name,
            'exists': False,
            'total_matches': 0,
            'urls': [],
            'error': str(e)
        }

def save_results(results: List[Dict], filename: str = "metal_band_matches.csv"):
    """Save results to a CSV file."""
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Name', 'URL', 'Total Matches'])
        
        for result in results:
            # Write a row for each URL found
            if result['urls']:
                for url in result['urls']:
                    writer.writerow([
                        result['name'],
                        url,
                        result['total_matches']
                    ])
            else:
                # Write a single row with empty URL for names with no matches
                writer.writerow([
                    result['name'],
                    '',
                    result['total_matches']
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
            print(f"Found {result['total_matches']} matching bands")
        
        # Reduced sleep time
        time.sleep(0.5)
        
        # Save progress every 20 names
        if i % 20 == 0:
            print(f"\nSaving progress... ({i}/{total} names processed)")
            save_results(results)
    
    print("\nSaving final results...")
    save_results(results)
    
    matches = sum(1 for r in results if r['exists'])
    print(f"\nFinished checking {total} names")
    print(f"Found {matches} names that match existing metal bands")
    print("Results have been saved to 'metal_band_matches.csv'")

if __name__ == "__main__":
    main()