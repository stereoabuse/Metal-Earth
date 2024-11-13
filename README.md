# Metal Earth 🧙‍♂️ 🎸
A *Lord of the Rings* metal band name generator and verifier

Find metal bands named after characters, places, and concepts from Tolkien's works. This project scrapes proper nouns from Tolkien texts and cross-references them with Metal Archives to discover bands inspired by Middle-earth.

## Overview

Tolkien's works have long been an inspiration for metal bands, at least since [Cirith Ungol](https://en.wikipedia.org/wiki/Cirith_Ungol_(band)). This tool helps you discover these connections (and find underused band names) by:
1. Extracting proper nouns from Tolkien's texts
2. Checking each name against the Metal Archives database
3. Generating a CSV of metal bands that share names with Tolkien's legendarium
4. Optionally, checking social media name availability

Skip to the results: [metal_band_matches.csv](metal_band_matches.csv)

## Installation

```bash
# Clone the repository
git clone https://github.com/stereoabuse/lotr-band-names.git
cd lotr-band-names

# Install required packages
pip install -r requirements.txt
```

## Usage

The project consists of two main scripts:

### 1. Extract Proper Nouns

```bash
python src/extract_proper_nouns.py
```

This will:
- Process all chapter files in the *-chapters directories
- Extract capitalized proper nouns
- Filter out common English words
- Save results to `unique_proper_nouns.txt`

### 2. Check Metal Archives

```bash
python src/metal_archives_checker.py
```

This will:
- Read the proper nouns from `unique_proper_nouns.txt`
- Check each name against Metal Archives
- Save matches to `metal_band_matches.csv`
- Take about an hour to run with the default settings (~8000 requests)


## Example Output

```csv
Cirith,Cirith Ungol,https://www.metal-archives.com/bands/Cirith_Ungol/561
Gorgoroth,Gorgoroth,https://www.metal-archives.com/bands/Gorgoroth/770
Isengard,Isengard,https://www.metal-archives.com/bands/Isengard/1027
Lumpkins,No match found,
```

## Data Sources

- Tolkien text data sourced from [jblazzy/LOTR](https://github.com/jblazzy/LOTR)
- Band information from [Metal Archives](https://www.metal-archives.com/)
- Page titles from Tolkien Gateway see  [`data/tolkien_gateway_download_process.md`](data/tolkien_gateway_download_process.md) and [`data/tolkien_gateway_pages.txt`](data/tolkien_gateway_pages.txt)

## Rate Limiting

The script includes a 0.3-second delay between Metal Archives requests to be respectful of their servers. Please do not modify this to make requests more frequent.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. Some areas that could use improvement:

- [ ] Add support for words from Tolkien constructed languages [Eldamo](https://eldamo.org/index.html)
- [ ] Add support for abstracting this to any corpus of text

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Text data from [jblazzy/LOTR](https://github.com/jblazzy/LOTR)
- [Metal Archives](https://www.metal-archives.com/) for their comprehensive database
- Contributors to [Tolkien Gateway](https://tolkiengateway.net/)
- All the metal bands keeping the legend of Middle-earth alive 🤘

---

*One script to find them all, one script to mine them,  
One script to bring them all, and in Python bind them*
