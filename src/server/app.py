# src/server/app.py
from flask import Flask, render_template, jsonify, request
import pandas as pd
import os

app = Flask(__name__)

# Get the absolute path to the reports directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
REPORTS_DIR = os.path.join(BASE_DIR, 'reports')
DATA_FILE = os.path.join(REPORTS_DIR, 'metal_band_matches.csv')

def _load_bands_dataframe() -> pd.DataFrame:
    """Load and sanitize the report data used by the web app."""
    print(f"Loading data from: {DATA_FILE}")
    if not os.path.exists(DATA_FILE):
        print("Report file not found. The web app will run with an empty dataset.")
        return pd.DataFrame()

    try:
        df = pd.read_csv(DATA_FILE)
    except Exception as e:
        print(f"Failed to read report CSV: {e}")
        return pd.DataFrame()

    if 'Band Name' not in df.columns:
        print("Missing required column 'Band Name'. The web app will run with an empty dataset.")
        return pd.DataFrame()

    filtered = df[df['Band Name'] != 'No match found'].copy()
    print(f"Loaded {len(filtered)} bands")
    return filtered


bands_df = _load_bands_dataframe()

@app.route('/')
def home():
    random_band = None
    if not bands_df.empty:
        random_band = bands_df.sample(n=1).iloc[0]
    total_bands = len(bands_df)
    return render_template('index.html', random_band=random_band, total_bands=total_bands)

@app.route('/search')
def search():
    query = request.args.get('q', '').lower()
    
    if not query:
        return jsonify([])
    if bands_df.empty:
        return jsonify([])
    if 'Search Name' not in bands_df.columns or 'Band Name' not in bands_df.columns:
        return jsonify([])
    
    try:
        results = bands_df[
            (bands_df['Search Name'].astype(str).str.lower().str.contains(query, na=False, regex=False)) |
            (bands_df['Band Name'].astype(str).str.lower().str.contains(query, na=False, regex=False))
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
