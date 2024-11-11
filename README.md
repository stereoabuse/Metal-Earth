# LOTR Band Names 🧙‍♂️ 🎸

Find metal bands named after characters, places, and concepts from Tolkien's works. This project scrapes proper nouns from Tolkien texts and cross-references them with Metal Archives to discover bands inspired by Middle-earth.

## Overview

Tolkien's works have long been an inspiration for metal bands. This tool helps you discover these connections by:
1. Extracting proper nouns from Tolkien's texts
2. Checking each name against the Metal Archives database
3. Generating a CSV of metal bands that share names with Tolkien's world

## Installation

```bash
# Clone the repository
git clone https://github.com/stereoabuse/lotr-band-names.git
cd lotr-band-names

# Install required packages
pip install requests
```

## Usage

The project consists of two main scripts:

### 1. Extract Proper Nouns

```bash
python extract_proper_nouns.py
```

This will:
- Process all chapter files in the *-chapters directories
- Extract capitalized proper nouns
- Filter out common English words
- Save results to `unique_proper_nouns.txt`

### 2. Check Metal Archives

```bash
python metal_archives_checker.py
```

This will:
- Read the proper nouns from `unique_proper_nouns.txt`
- Check each name against Metal Archives
- Save matches to `metal_band_matches.csv`

The output CSV contains:
- Name: The proper noun from Tolkien's work
- URL: Direct link to the band's Metal Archives page
- Total Matches: Number of bands found with this name

## Example Output

```csv
Aragorn,https://www.metal-archives.com/bands/Aragorn/6318,10
Balrog,https://www.metal-archives.com/bands/Balrog/34103,8
Fangorn,https://www.metal-archives.com/bands/Fangorn/82431,4
```

## Data Sources

- Tolkien text data sourced from [jblazzy/LOTR](https://github.com/jblazzy/LOTR)
- Band information from [Metal Archives](https://www.metal-archives.com/)

## Rate Limiting

The script includes a 0.5-second delay between Metal Archives requests to be respectful of their servers. Please do not modify this to make requests more frequent.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. Some areas that could use improvement:

- [ ] Add support for fuzzy matching similar names
- [ ] Add support for words from [Eldamo](https://eldamo.org/index.html)
- [ ] Create visualization of most common Tolkien-inspired band names
- [ ] Add tests for the name extraction process

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Text data from [jblazzy/LOTR](https://github.com/jblazzy/LOTR)
- [Metal Archives](https://www.metal-archives.com/) for their comprehensive database
- All the metal bands keeping the spirit of Middle-earth alive 🤘

## Contact

If you have questions or want to contribute, feel free to:
- Open an issue
- Submit a pull request

---

*One script to find them all, one script to mine them,  
One script to bring them all, and in Python bind them*