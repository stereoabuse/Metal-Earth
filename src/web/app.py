# src/web/app.py
from flask import Flask, render_template, jsonify, request
import pandas as pd
import random
import os

app = Flask(__name__)

# Get the absolute path to the reports directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
REPORTS_DIR = os.path.join(BASE_DIR, 'reports')
DATA_FILE = os.path.join(REPORTS_DIR, 'metal_band_matches.csv')

# Load the data once when starting the server
print(f"Loading data from: {DATA_FILE}")
df = pd.read_csv(DATA_FILE)
bands_df = df[df['Band Name'] != 'No match found'].copy()
print(f"Loaded {len(bands_df)} bands")

@app.route('/')
def home():
    random_band = bands_df.sample(n=1).iloc[0]
    total_bands = len(bands_df)
    return render_template('index.html', random_band=random_band, total_bands=total_bands)

@app.route('/search')
def search():
    query = request.args.get('q', '').lower()
    
    if not query:
        return jsonify([])
    
    try:
        results = bands_df[
            (bands_df['Search Name'].astype(str).str.lower().str.contains(query, na=False)) |
            (bands_df['Band Name'].astype(str).str.lower().str.contains(query, na=False))
        ].to_dict('records')
        
        clean_results = []
        for result in results[:10]:
            clean_result = {}
            for key, value in result.items():
                if pd.isna(value):
                    clean_result[key] = None
                else:
                    clean_result[key] = str(value)
            clean_results.append(clean_result)
        
        return jsonify(clean_results)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def run_server(host='0.0.0.0', port=5000, debug=False):
    app.run(host=host, port=port, debug=debug)

if __name__ == '__main__':
    run_server(debug=True)