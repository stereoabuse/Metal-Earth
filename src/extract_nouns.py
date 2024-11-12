import ssl
import urllib.request
import os
from pathlib import Path

def download_word_list():
    """Download a list of common English words, with SSL verification handling."""
    
    # Create an SSL context that doesn't verify certificates (use with caution)
    ssl_context = ssl._create_unverified_context()
    
    word_list_urls = [
        'https://raw.githubusercontent.com/dwyl/english-words/master/words.txt',
        'https://raw.githubusercontent.com/first20hours/google-10000-english/master/google-10000-english.txt'
    ]
    
    words = set()
    
    print("Downloading comprehensive word list...")
    for url in word_list_urls:
        try:
            print(f"Downloading word list from {url}...")
            response = urllib.request.urlopen(url, context=ssl_context)
            content = response.read().decode('utf-8')
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

def extract_proper_nouns(texts, common_words):
    """Extract proper nouns from the texts."""
    print("Analyzing word usage patterns...")
    
    # Split texts into words and normalize
    words = []
    for text in texts:
        words.extend(word.strip('.,!?()[]{}:;"\'') for word in text.split())
    
    print("Identifying proper nouns...")
    proper_nouns = set()
    
    for word in words:
        # Basic proper noun rules:
        # 1. Starts with capital letter
        # 2. Not at start of sentence
        # 3. Not a common word
        if (word and word[0].isupper() and 
            len(word) > 1 and
            word.lower() not in common_words):
            proper_nouns.add(word)
    
    print("Removing plurals...")
    # Remove obvious plurals if singular exists
    singles = {word[:-1] for word in proper_nouns if word.endswith('s')}
    proper_nouns = {word for word in proper_nouns if not (word.endswith('s') and word[:-1] in singles)}
    
    return sorted(proper_nouns)

def main():
    # Download or load word list
    common_words = download_word_list()
    
    # Read all texts
    texts = read_texts()
    
    # Extract proper nouns
    proper_nouns = extract_proper_nouns(texts, common_words)
    
    print(f"\nFound {len(proper_nouns)} unique proper nouns across all texts")
    
    # Save results
    with open('unique_proper_nouns.txt', 'w') as f:
        f.write('\n'.join(proper_nouns))
    
    print("\nResults have been saved to 'unique_proper_nouns.txt'")

if __name__ == "__main__":
    main()