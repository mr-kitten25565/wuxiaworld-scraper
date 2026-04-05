#!/usr/bin/env python3
"""Improved novel scraper that writes chapters into ./novels/<title>/ and then
creates a zip in ./finished/.  After each chapter is written, a Markdown
link to the *next* chapter is appended automatically.

Usage:
    python stelling.py <chapter_url> [--start N] [--end M] [--max M] [--title TITLE]

Arguments:
    <chapter_url>   URL of the first chapter page (used to infer the novel title).

Options:
    --start N       First chapter number (default: 1).
    --end M         Last chapter number (default: 1 or URL‑derived max).
    --max M         Maximum chapter number to download (overrides URL‑derived max).
    --title TITLE   Override the inferred novel title. If omitted, the title is
                    derived from the URL in a more readable way.

The script will:
    1. Derive a clean novel title from the URL (or use --title).
    2. Create ``novels/<title>`` (if it does not exist).
    3. Download each chapter in the requested range.
    4. Write each chapter as ``Chapter####.md``.
    5. Append a Markdown link to the *next* chapter at the end of each file.
    6. Zip the whole folder into ``finished/<title>.zip``.
"""

import sys
import os
import re
import argparse
import zipfile
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, unquote

# ----------------------------------------------------------------------
# Re‑use the parsing helpers from stealingintelectualpropert.py
# ----------------------------------------------------------------------
def getraw(chapter_url):
    """Fetch raw HTML of a chapter URL."""
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 '
                      '(KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36'
    }
    resp = requests.get(chapter_url, headers=headers, timeout=10)
    resp.raise_for_status()
    return resp.text

def unhtml(html):
    """Strip the HTML to plain text, keeping only the content inside
    tags with id='chapterText' (same as stealingintelectualpropert.py)."""
    soup = BeautifulSoup(html, "html.parser")
    paragraphs = []
    for el in soup.find_all(id="chapterText"):
        # ``str(el)`` yields the full XML tag; strip the wrapper tags.
        paragraphs.append(str(el)[65:-6])
    return "\n\n".join(paragraphs)

# ----------------------------------------------------------------------
# Helper to turn a URL into a clean, pretty novel title
# ----------------------------------------------------------------------
def clean_title_from_url(url):
    """Return a human‑readable title for the novel.

    The heuristic:
        - Take the last path component (e.g. "reverend-insanity-1").
        - Remove any trailing chapter number (digits at the end).
        - Replace hyphens/underscores with spaces.
        - Capitalise each word.
    """
    parsed = urlparse(url)
    segments = [seg for seg in parsed.path.split('/') if seg]
    if not segments:
        return "novel"
    title = unquote(segments[-1])
    # strip trailing digits (chapter number) and possible hyphens
    title = re.sub(r'[-_]?\d+$', '', title)
    title = title.replace('_', ' ').replace('-', ' ')
    title = title.title()
    return title or "novel"

def extract_folder_name(url):
    """Legacy helper – keep for backward compatibility (used for the folder)."""
    parsed = urlparse(url)
    segments = [seg for seg in parsed.path.split('/') if seg]
    if not segments:
        return "download"
    title = unquote(segments[-1])
    if not title:
        title = "download"
    title = title.replace('/', '_').replace('\\', '_')
    return title

def format_chapter_number(num):
    """Return a zero‑padded 4‑digit string, e.g. 5 → "0005"."""
    return f"{num:04d}"

def fileName(chapterNumber):
    """Return a filename like Chapter0001.md for a given chapter number."""
    return f"Chapter{format_chapter_number(chapterNumber)}.md"

def next_link(chapter_number, total_chapters, title):
    """Generate a Markdown link to the next chapter.

    The link points to ``novels/<title>/ChapterXXXX.md`` where the number
    is ``chapter_number+1`` (unless we are already at the last chapter).
    """
    next_num = chapter_number + 1
    # If we are at the last chapter we don't want a link – caller should guard.
    next_file = fileName(next_num)
    return f"[[novels/{title}/{next_file}|Next Chapter]]"

# ----------------------------------------------------------------------
# Determine the highest chapter number from the URL (or from a supplied arg)
# ----------------------------------------------------------------------
def max_chapter_from_url(url):
    """Very simple heuristic: look for a pattern like .../chapter/...-NNN
    and extract the number. If none is found, fall back to 1."""
    m = re.search(r'(\d+)$', url.rstrip('/').split('/')[-1])
    return int(m.group(1)) if m else 1

# ----------------------------------------------------------------------
# Main workflow
# ----------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(
        description="Scrape a novel chapter page and store it in ./novels/"
    )
    parser.add_argument("url", help="URL of the first chapter page")
    parser.add_argument("--start", type=int, default=1,
                        help="First chapter number to download (default: 1)")
    parser.add_argument("--end", type=int, default=None,
                        help="Last chapter number to download (default: 1 or URL‑derived max)")
    parser.add_argument("--max", type=int, default=None,
                        help="Maximum chapter number to download (overrides URL‑derived max)")
    parser.add_argument("--title", type=str, default=None,
                        help="Explicit novel title (overrides title extracted from URL)")

    args = parser.parse_args()

    if not args.url:
        parser.error("URL is required")

    # 1️⃣  Determine the novel title and the folder name
    if args.title:
        novel_title = args.title.replace('/', '_')
    else:
        novel_title = clean_title_from_url(args.url)

    folder = extract_folder_name(args.url)  # legacy folder name for the zip
    novel_dir = os.path.join("novels", novel_title)
    os.makedirs(novel_dir, exist_ok=True)

    # 2️⃣  Determine chapter range
    max_from_url = max_chapter_from_url(args.url)
    end = args.end if args.end is not None else (args.max if args.max is not None else max_from_url)
    start = max(args.start, 1)
    if end < start:
        parser.error("end must be >= start")
    print(f"Scraping '{novel_title}' – chapters {start} … {end}")

    # 3️⃣  Loop over chapters, write Markdown files and add a "next chapter" link
    for i in range(start, end + 1):
        # Build chapter URL – replace the trailing number in the original URL
        chap_url = re.sub(r'(\d+)$', f'{i}', args.url.rstrip('/'))
        try:
            raw_html = getraw(chap_url)
            text = unhtml(raw_html)
            chapter_file = fileName(i)
            chapter_path = os.path.join(novel_dir, chapter_file)
            with open(chapter_path, "w", encoding="utf-8") as f:
                f.write(text)
            # Append a link to the *next* chapter unless this is the final chapter
            if i < end:
                link = next_link(i, end, novel_title)
                with open(chapter_path, "a", encoding="utf-8") as f:
                    f.write("\n" + link + "\n")
            print(f"  [+] Chapter {i:04d} → {chapter_file}")
        except Exception as e:
            print(f"  [-] Failed chapter {i}: {e}", file=sys.stderr)
            # Continue with the next chapter instead of aborting completely
            continue

    # 4️⃣  Zip the folder into the finished directory
    zip_name = f"{novel_title.replace(' ', '_')}.zip"
    zip_path = os.path.abspath(os.path.join("finished", zip_name))
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, _, files in os.walk(novel_dir):
            for file in files:
                full_path = os.path.join(root, file)
                arcname = os.path.relpath(full_path, start=os.path.dirname(zip_path))
                zf.write(full_path, arcname)
    print(f"✅  Finished – created {zip_path}")

if __name__ == "__main__":
    # If no command‑line arguments were given, fall back to an
    # interactive prompt.  This makes the script usable both from the
    # dev‑shell (`python stelling.py <url> …`) and from the packaged
    # wrapper (`run-scraper` without arguments).
    if len(sys.argv) == 1:
        # Prompt for missing data
        url = input("Enter chapter URL: ").strip()
        title = input("Enter novel title (optional): ").strip()
        start_str = input("Enter start chapter number (default 1): ").strip()
        end_str = input("Enter end chapter number (default: inferred from URL): ").strip()
        # Build a fake argv list and invoke main()
        sys.argv = ["stelling.py", url]
        if title:
            sys.argv.append("--title")
            sys.argv.append(title)
        if start_str:
            sys.argv.append("--start")
            sys.argv.append(start_str)
        if end_str:
            sys.argv.append("--end")
            sys.argv.append(end_str)
        main()
    else:
        main()
