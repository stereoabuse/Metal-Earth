import os
import re
import time
import requests
from datetime import datetime
from typing import Dict, List

class HTMLRenderer:
    """Class to generate HTML snippets for the report."""

    @staticmethod
    def generate_ma_html(ma_data: Dict) -> str:
        if not ma_data['matches']:
            return "<p>No existing bands found on Metal Archives.</p>"

        html = f"<p>Found {ma_data['total_matches']} existing band(s):</p>"
        for match in ma_data['matches']:
            html += f"""
            <div class="metal-archives">
                <strong>{match['name']}</strong><br>
                Genre: {match['genre']}<br>
                <a href="{match['url']}" target="_blank" style="color: #ff6b6b;">View on Metal Archives</a>
            </div>
            """
        return html

    @staticmethod
    def generate_social_html(social: Dict[str, bool]) -> str:
        return ''.join([
            f'<li><strong>{platform}:</strong> <span class="{"available" if available else "taken"}">'
            f'{"Available" if available else "Taken"}</span></li>'
            for platform, available in social.items()
        ])

    @staticmethod
    def generate_variations_html(variations: List[str]) -> str:
        return ''.join([f'<span class="variation">{v}</span>' for v in variations])

    @staticmethod
    def generate_recs_html(recs: List[str]) -> str:
        if not recs:
            return "<p>No specific recommendations.</p>"
        return ''.join([f'<li>{rec}</li>' for rec in recs])

class BandNameAnalyzer:
    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    SOCIAL_MEDIA_PLATFORMS = {
        'bandcamp': 'https://{handle}.bandcamp.com',
        'instagram': 'https://www.instagram.com/{handle}/',
        'twitter': 'https://twitter.com/{handle}',
        'facebook': 'https://facebook.com/{handle}'
    }

    def check_metal_archives(self, name: str) -> Dict:
        """Check if the band exists on Metal Archives."""
        url = "https://www.metal-archives.com/search/ajax-band-search/"
        params = {
            'field': 'name',
            'query': name,
            'sEcho': 1,
            'iDisplayStart': 0,
            'iDisplayLength': 100
        }
        try:
            response = requests.get(url, params=params, headers=self.HEADERS)
            response.raise_for_status()
            data = response.json()
            matches = self._parse_ma_results(data['aaData'])
            return {
                'exists': bool(matches),
                'total_matches': len(matches),
                'matches': matches
            }
        except Exception as e:
            print(f"Error checking Metal Archives: {str(e)}")
            return {'exists': False, 'total_matches': 0, 'matches': []}

    def _parse_ma_results(self, aaData: List) -> List[Dict]:
        """Parse the results from Metal Archives."""
        matches = []
        for band_data in aaData:
            url_match = re.search(r'href="([^"]+)"', band_data[0])
            name_match = re.sub(r'<[^>]+>', '', band_data[0])
            genre = band_data[1] if len(band_data) > 1 else 'Unknown'
            if url_match:
                matches.append({
                    'name': name_match,
                    'url': url_match.group(1),
                    'genre': genre
                })
        return matches

    def check_social_media(self, name: str) -> Dict[str, bool]:
        """Check social media availability."""
        handle = re.sub(r'[^a-zA-Z0-9]', '', name.lower())
        results = {}
        for platform, url_template in self.SOCIAL_MEDIA_PLATFORMS.items():
            url = url_template.format(handle=handle)
            try:
                response = requests.get(url, headers=self.HEADERS)
                results[platform] = response.status_code != 200
                time.sleep(0.5)  # Be nice to the servers
            except Exception:
                results[platform] = True  # Assume available if error
        return results

    def generate_variations(self, name: str) -> List[str]:
        """Generate metal-style variations of the name."""
        variations = set()
        variations.add(name)

        metal_chars = {
            'a': 'æ', 'o': 'ø', 'u': 'ü',
            'A': 'Æ', 'O': 'Ø', 'U': 'Ü'
        }

        for char, replacement in metal_chars.items():
            if char in name:
                metal_name = name.replace(char, replacement)
                variations.add(metal_name)

        # Add common prefixes/suffixes
        variations.update({f"The {name}", name.replace(' ', ''), name.replace(' ', '_')})

        return sorted(variations)

    def _calculate_viability_score(self, ma_data: Dict, social: Dict[str, bool]) -> int:
        """Calculate a viability score from 0-100."""
        score = 100
        score -= ma_data['total_matches'] * 20
        score -= sum(not available for available in social.values()) * 10
        return max(0, min(100, score))

    def _generate_recommendations(self, name: str, ma_data: Dict, social: Dict[str, bool]) -> List[str]:
        """Generate recommendations based on analysis."""
        recs = []
        if ma_data['total_matches'] > 0:
            recs.append(f"Warning: Found {ma_data['total_matches']} existing band(s) with this name")
        taken_platforms = [p for p, available in social.items() if not available]
        if taken_platforms:
            recs.append(f"Social media handles already taken on: {', '.join(taken_platforms)}")
        if len(name) > 20:
            recs.append("Consider a shorter name for better social media usage")
        return recs

    def analyze_name(self, name: str) -> Dict:
        """Perform comprehensive name analysis."""
        ma_data = self.check_metal_archives(name)
        social = self.check_social_media(name)
        variations = self.generate_variations(name)
        score = self._calculate_viability_score(ma_data, social)
        recommendations = self._generate_recommendations(name, ma_data, social)
        return {
            'name': name,
            'metal_archives': ma_data,
            'social_media': social,
            'variations': variations,
            'viability_score': score,
            'recommendations': recommendations
        }

def generate_html_report(analysis: Dict, output_dir: str = "reports") -> str:
    """Generate HTML report from analysis."""
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"band_name_report_{timestamp}.html"
    filepath = os.path.join(output_dir, filename)
    html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <!-- HTML content unchanged -->
    </head>
    <body>
        <div class="container">
            <h1>Band Name Analysis: {analysis['name']}</h1>
            <div class="section">
                <div class="score" style="color: {'#4CAF50' if analysis['viability_score'] >= 70 else '#f44336'}">
                    {analysis['viability_score']}/100
                </div>
            </div>
            <div class="section">
                <h2>Metal Archives Results</h2>
                {HTMLRenderer.generate_ma_html(analysis['metal_archives'])}
            </div>
            <div class="section">
                <h2>Social Media Availability</h2>
                <ul>
                    {HTMLRenderer.generate_social_html(analysis['social_media'])}
                </ul>
            </div>
            <div class="section">
                <h2>Name Variations</h2>
                {HTMLRenderer.generate_variations_html(analysis['variations'])}
            </div>
            <div class="section">
                <h2>Recommendations</h2>
                <ul>
                    {HTMLRenderer.generate_recs_html(analysis['recommendations'])}
                </ul>
            </div>
            <footer style="text-align: center; margin-top: 20px; color: #888;">
                Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            </footer>
        </div>
    </body>
    </html>
    """
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(html)
    return filepath

def analyze_from_file(filename: str = "unique_proper_nouns.txt"):
    """Analyze all names from the proper nouns file."""
    analyzer = BandNameAnalyzer()
    os.makedirs("reports", exist_ok=True)
    print("Loading names from file...")
    with open(filename, 'r', encoding='utf-8') as f:
        # Skip header lines
        for line in f:
            if line.startswith('='):
                break
        names = [line.strip() for line in f if line.strip()]
    print(f"Found {len(names)} names to analyze")
    for i, name in enumerate(names, 1):
        print(f"\nAnalyzing name {i}/{len(names)}: {name}")
        analysis = analyzer.analyze_name(name)
        report_path = generate_html_report(analysis)
        print(f"Report generated: {report_path}")
        time.sleep(1)  # Be nice to the servers

def analyze_single_name(name: str):
    """Analyze a single band name."""
    analyzer = BandNameAnalyzer()
    analysis = analyzer.analyze_name(name)
    report_path = generate_html_report(analysis)
    print(f"\nReport generated: {report_path}")

def main():
    print("LOTR Band Name Analyzer")
    print("=" * 50)
    print("\n1. Analyze a single name")
    print("2. Analyze all names from file")
    choice = input("\nEnter your choice (1 or 2): ")
    if choice == "1":
        name = input("Enter band name to analyze: ")
        analyze_single_name(name)
    elif choice == "2":
        analyze_from_file()
    else:
        print("Invalid choice!")

if __name__ == "__main__":
    main()
