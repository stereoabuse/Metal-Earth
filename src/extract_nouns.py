import requests
from pathlib import Path

def download_word_list():
    """Download a list of common English words, with SSL verification handling."""
    word_list_urls = [
        'https://raw.githubusercontent.com/dwyl/english-words/master/words.txt',
        'https://raw.githubusercontent.com/first20hours/google-10000-english/master/google-10000-english.txt'
    ]
    
    words = set()
    
    print("Downloading comprehensive word list...")
    for url in word_list_urls:
        try:
            print(f"Downloading word list from {url}...")
            response = requests.get(url, verify=False)  # verify=False is equivalent to the previous SSL context
            response.raise_for_status()  # Raise an exception for bad status codes
            content = response.text
            words.update(word.strip().lower() for word in content.split())
            print(f"Successfully downloaded words from {url}")
            break  # Exit loop if successful
        except Exception as e:
            print(f"Failed to download from {url}: {e}")
            continue
    
    # If no words were downloaded, try to use local file
    if not words:
        local_file = Path('english_words.txt')
        if local_file.exists():
            print("Using local word list file...")
            with open(local_file, 'r') as f:
                words.update(word.strip().lower() for word in f)
        else:
            print("No word list available. Please provide a word list file named 'english_words.txt'")
    
    print(f"Downloaded {len(words)} common words.")
    return words

def read_texts():
    """Read all text files from the data directories."""
    texts = []
    data_dir = Path('data')
    
    # Find all chapter directories
    chapter_dirs = [d for d in data_dir.iterdir() if d.is_dir() and d.name.endswith('-chapters')]
    
    print("Reading all texts...")
    for dir_path in chapter_dirs:
        for file_path in dir_path.glob('*.txt'):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    texts.append(f.read())
            except Exception as e:
                print(f"Error reading {file_path}: {e}")
    
    return texts


def extract_proper_nouns(texts: list[str], common_words: set) -> set:
    """Extract proper nouns from texts that aren't in common word list."""
    words = set()
    
    # First pass: collect all words
    for text in texts:
        for word in text.split():
            # Skip if word is too short
            if len(word) < 2:
                continue
                
            # Check if first character is uppercase
            if not word[0].isupper():
                continue
            
            # Handle possessive 's before other punctuation
            if "'s" in word.lower():
                word = word.split("'")[0]
            
            # Remove remaining punctuation, keeping original case
            clean_word = ''.join(c for c in word if c.isalpha())
            
            # Skip if empty after cleaning
            if not clean_word:
                continue
                
            # Skip if it's a common word (lowercase comparison)
            if clean_word.lower() in common_words:
                continue
            
            # Standardize to Title Case
            clean_word = clean_word.title()
            words.add(clean_word)
    
    # Second pass: remove plurals if singular exists
    filtered_words = set()
    for word in words:
        # If word ends in 's' and its singular form exists in our set,
        # skip it. Otherwise, add it to our filtered set.
        if word.endswith('s'):
            singular = word[:-1]
            if singular in words:
                continue
        filtered_words.add(word)
    
    return filtered_words
def main():
    # Download or load word list
    common_words = download_word_list()
    
    # Read all texts
    texts = read_texts()
    
    # Extract proper nouns
    proper_nouns = extract_proper_nouns(texts, common_words)
    
    print(f"\nFound {len(proper_nouns)} unique proper nouns across all texts")
    
    # Sort the proper nouns alphabetically
    sorted_nouns = sorted(proper_nouns)
    
    # Save results
    with open('reports/unique_proper_nouns.txt', 'w') as f:
        f.write('\n'.join(sorted_nouns))
    
    print("\nResults have been saved to 'reports/unique_proper_nouns.txt'")
if __name__ == "__main__":
    main()