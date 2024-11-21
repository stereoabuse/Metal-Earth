# Metal Earth 🧙‍♂️ 🎸
A *Lord of the Rings* metal band name generator and verifier

Find metal bands named after characters, places, and concepts from Tolkien's works. This project scrapes proper nouns from Tolkien texts and cross-references them with Metal Archives to discover bands inspired by Middle-earth.

## Overview

Tolkien's works have long been an inspiration for metal bands, at least since [Cirith Ungol](https://en.wikipedia.org/wiki/Cirith_Ungol_(band)). This tool helps you discover these connections (and find underused band names) by:
1. Extracting proper nouns from Tolkien's texts
2. Finding the Tolkien Gateway page for each name as potential search terms
3. Manually curating a list of search terms
4. Checking each term against the Metal Archives database
5. Generating a CSV of metal bands that share names with Tolkien's legendarium
6. Optionally, checking social media name availability

Skip to the results: [reports/metal_band_matches.csv](reports/metal_band_matches.csv)

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
- Save results to `reports/unique_proper_nouns.txt`

### 2. Check Metal Archives

```bash
python src/metal_archives_checker.py
```

This will:
- Read the proper nouns from `reports/unique_proper_nouns.txt`
- Check each name against Metal Archives
- Save matches to `reports/metal_band_matches.csv`
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
- Page titles from Tolkien Gateway see  [`docs/tolkien_gateway_download_process.md`](docs/tolkien_gateway_download_process.md) and [`data/external-sources/tolkien_gateway_pages.txt`](data/external-sources/tolkien_gateway_pages.txt)

## Rate Limiting

The script includes a 0.3-second delay between Metal Archives requests to be respectful of their servers. Please do not modify this to make requests more frequent.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. Some areas that could use improvement:

- [ ] Add support for words from Tolkien constructed languages [Eldamo](https://eldamo.org/index.html)
    * These have been downloaded and added to `data/external-sources/Eldamo_dictionary.txt` but need to be curated and fed through metal_archives_checker.py
- [ ] Add support for abstracting this to any corpus of text
- [ ] Check pages from [The One Wiki](https://lotr.fandom.com/), currently in `data/external-sources/ORTRT_wiki.txt`

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- **Text Data**: Text data for Tolkien's works provided by [jblazzy/LOTR](https://github.com/jblazzy/LOTR).
- **Band Information**: Band data sourced from [Encyclopaedia Metallum: The Metal Archives](https://www.metal-archives.com/), © 2002-2024, Encyclopaedia Metallum. This database serves as a comprehensive resource on metal bands, albums, and related information.
- **Tolkien Gateway**: Contributors to [Tolkien Gateway](https://tolkiengateway.net/) for additional Tolkien-related resources.
- **Elvish Language and Constructed Language Data**: This project utilizes data from Paul Strack’s Elvish language lexicon, available at [Eldamo](https://eldamo.org), © 2008 - 2024. This data is licensed under the [Creative Commons Attribution 4.0 International License](http://creativecommons.org/licenses/by/4.0/), which allows for copying, distribution, and adaptation with proper attribution. We are grateful for Paul Strack’s work on a comprehensive Tolkien lexicon.
- All the metal bands keeping the legend of Middle-earth alive 🤘

### Special Attribution to J.R.R. Tolkien

This project is inspired by the works of **J.R.R. Tolkien**, including *The Hobbit*, *The Lord of the Rings*, and *The Silmarillion*. These texts are the original creations of Tolkien and remain protected under copyright.


---

*One script to find them all, one script to mine them,  
One script to bring them all, and in Python bind them*
