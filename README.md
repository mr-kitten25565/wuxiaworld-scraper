# Wuxiaworld Scraper

# credits
@Nobody1902

A Python scraper that fetches a book from a URL, splits the HTML into chapter‑wise Markdown files, and packages everything into a ZIP archive.

## Overview

The scraper works with two scripts:

* `stelling.py` – Scrapes a novel chapter by chapter, writes each chapter as a Markdown file under `novels/<title>/`, and creates a ZIP archive in `finished/`.
* `stelling.py` – (the same script) can also be used as a one‑time‑use scraper for a single book (e.g., a technical book) by providing a URL; it will create a ZIP containing Markdown chapters under a `chapters/` directory.

## Features

- Derives a clean novel title from the URL (or uses `--title` to override).
- Creates the output directory `novels/<title>/` automatically.
- Downloads each chapter in the requested range (`--start`, `--end`, `--max`).
- Writes each chapter as `Chapter####.md` and appends a Markdown link to the *next* chapter.
- Zips the whole `novels/<title>/` folder into `finished/<title>.zip`.
- Also supports a simple book scraper mode that produces a `chapters/` directory inside a ZIP (useful for single‑book downloads).

## Usage

### Scrape a novel (full‑book workflow)

```bash
# Install dependencies (requires pip with --break-system-packages on Nix)
pip install -r requirements.txt --break-system-packages

# Run the scraper for a novel
python stelling.py <chapter_url> [--start N] [--end M] [--max M] [--title TITLE]
```

* `<chapter_url>` – URL of the first chapter (the script infers the title from this URL).
* `--start N` – First chapter number (default: 1).
* `--end M` – Last chapter number (default: 1 or URL‑derived max).
* `--max M` – Maximum chapter number to download (overrides URL‑derived max).
* `--title TITLE` – Override the inferred novel title.

Example:
```bash
python stelling.py https://example.com/Books/My%20Book/Chapter1 --title "My Book"
```

### Simple book scraper (single‑book mode)

```bash
python stelling.py https://example.com/Books/My%20Book/Chapter1
```

This will create a ZIP file with Markdown chapters under a `chapters/` directory.

## Requirements

- Python 3.11+
- `requests`
- `beautifulsoup4`
- `markdownify` (for converting HTML to Markdown)

These are listed in `requirements.txt`.

## Example Output

Running the script with the default test URL (`httpbin.org/html`) creates:

```
novels/
└── My%20Book/
    ├── Chapter001.md
    ├── Chapter002.md
    └── Chapter003.md

finished/
└── My%20Book.zip   # contains the Markdown files under a `chapters/` folder
```

When using the simple book scraper mode, the output looks like:

```
output/
├── chapters/
│   ├── 01_chapter_1.md
│   └── 02_chapter_2.md
└── httpbin_org.zip
```

## License

Public domain / CC0 – feel free to adapt and reuse.
