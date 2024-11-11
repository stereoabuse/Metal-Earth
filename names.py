import os
import re
from pathlib import Path
from typing import Set, List, Dict
import urllib.request
from collections import defaultdict

def download_word_list() -> Set[str]:
    """Download a comprehensive English word list."""
    word_set = set()
    
    # List of URLs for different word lists
    urls = [
        'https://raw.githubusercontent.com/dwyl/english-words/master/words.txt',
        'https://raw.githubusercontent.com/first20hours/google-10000-english/master/google-10000-english.txt'
    ]
    
    for url in urls:
        try:
            print(f"Downloading word list from {url}...")
            response = urllib.request.urlopen(url)
            words = response.read().decode('utf-8').splitlines()
            word_set.update(word.strip().lower() for word in words if word.strip())
        except Exception as e:
            print(f"Failed to download from {url}: {str(e)}")
            continue
    
    if not word_set:
        try:
            with open('english_words.txt', 'r', encoding='utf-8') as f:
                word_set = {line.strip().lower() for line in f}
        except FileNotFoundError:
            print("No word list available. Please provide a word list file named 'english_words.txt'")
            return set()
    
    return word_set

def read_chapter_file(file_path: str) -> str:
    """Read content from a single chapter file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()

def get_chapter_folders() -> List[str]:
    """Get all chapter folder paths."""
    return [d for d in os.listdir() if d.endswith('-chapters')]

def combine_chapter_texts(folder: str) -> str:
    """Combine all chapter texts from a single book folder."""
    folder_path = Path(folder)
    combined_text = ""
    
    chapter_files = sorted(
        [f for f in folder_path.glob("*.txt")],
        key=lambda x: int(x.stem) if x.stem.isdigit() else float('inf')
    )
    
    for chapter_file in chapter_files:
        combined_text += read_chapter_file(chapter_file) + "\n"
    
    return combined_text

def analyze_word_usage(text: str) -> Dict[str, Dict]:
    """Analyze how words are used in the text."""
    # Split text into sentences (roughly)
    sentences = re.split('[.!?]+', text)
    
    word_stats = defaultdict(lambda: {'start_count': 0, 'mid_count': 0, 'total_count': 0})
    
    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue
            
        # Split sentence into words
        words = sentence.split()
        if not words:
            continue
            
        # Analyze each word in the sentence
        for i, word in enumerate(words):
            if re.match(r'^[A-Z][a-zA-Z]*$', word):
                word_stats[word]['total_count'] += 1
                if i == 0:
                    word_stats[word]['start_count'] += 1
                else:
                    word_stats[word]['mid_count'] += 1
    
    return word_stats

def is_plural(word: str) -> bool:
    """Check if a word is likely a plural form."""
    return (
        word.endswith('s') and
        not word.endswith('ss') and
        not word.endswith('us') and
        not word.endswith('is') and
        not word.endswith('as') and
        not word.endswith('ess')
    )

def get_singular_form(word: str) -> str:
    """Get the singular form of a word."""
    if is_plural(word):
        return word[:-1]
    return word

def remove_plurals(words: Set[str]) -> Set[str]:
    """Remove plural forms when singular exists."""
    result = set()
    plural_map = {}
    
    for word in words:
        singular = get_singular_form(word)
        if word == singular:
            result.add(word)
        else:
            plural_map[singular] = word
    
    for singular, plural in plural_map.items():
        if singular not in result:
            result.add(plural)
            
    return result

def analyze_proper_nouns() -> Set[str]:
    """Main function to analyze proper nouns in all books."""
    print("Downloading comprehensive word list...")
    common_words = download_word_list()
    print(f"Downloaded {len(common_words)} common words.")
    
    all_text = ""
    print("Reading all texts...")
    for folder in get_chapter_folders():
        print(f"Processing {folder}...")
        all_text += combine_chapter_texts(folder)
    
    print("Analyzing word usage patterns...")
    word_stats = analyze_word_usage(all_text)
    
    print("Identifying proper nouns...")
    proper_nouns = {
        word for word, stats in word_stats.items()
        if (
            # Must appear multiple times
            stats['total_count'] >= 2 and
            # Must appear capitalized in middle of sentence at least once
            stats['mid_count'] >= 1 and
            # Must not be a common word
            word.lower() not in common_words and
            # Must be longer than one character
            len(word) > 1
        )
    }
    
    print("Removing plurals...")
    return remove_plurals(proper_nouns)

def save_results(proper_nouns: Set[str], output_file: str = "unique_proper_nouns.txt"):
    """Save results to a file."""
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("UNIQUE PROPER NOUNS FROM ALL TOLKIEN TEXTS\n")
        f.write("=" * 50 + "\n\n")
        for noun in sorted(proper_nouns):
            f.write(f"{noun}\n")

def main():
    try:
        proper_nouns = analyze_proper_nouns()
        
        # Print summary
        print(f"\nFound {len(proper_nouns)} unique proper nouns across all texts")
        
        # Save results
        save_results(proper_nouns)
        print(f"\nResults have been saved to 'unique_proper_nouns.txt'")
        
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()