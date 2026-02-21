"""
KSAU arXiv Monitor Script (v38.0)
---------------------------------
Designed to fetch recent papers from arXiv (astro-ph.CO) matching S8 tension keywords.
This script is a helper for the human maintainer to update s8_monitoring_log.md.

Usage:
    python v38.0/arxiv_monitor.py

Dependencies:
    None (uses standard library)

Author: Gemini SSoT Auditor
Date: 2026-02-21
"""

import urllib.request
import urllib.error
import xml.etree.ElementTree as ET
import datetime
import sys

# Search Configuration
KEYWORDS = [
    "Euclid weak lensing",
    "LSST cosmic shear",
    "S8 tension",
    "KiDS-1000",
    "DES Y3",
    "HSC-SSP",
    "sigma8",
    "structure growth"
]

ARXIV_API_URL = "http://export.arxiv.org/api/query?search_query=cat:astro-ph.CO&sortBy=submittedDate&sortOrder=descending&max_results=50"

def get_text(element, default=''):
    return element.text if element is not None and element.text else default

def check_arxiv():
    print(f"--- KSAU arXiv Monitor ({datetime.date.today()}) ---")
    print(f"Fetching latest 50 astro-ph.CO papers from {ARXIV_API_URL}...")
    
    try:
        with urllib.request.urlopen(ARXIV_API_URL) as response:
            xml_data = response.read()
    except urllib.error.URLError as e:
        print(f"Error fetching arXiv feed: {e}")
        return
    except Exception as e:
        print(f"Unexpected error: {e}")
        return

    try:
        root = ET.fromstring(xml_data)
        # Atom namespace
        ns = {'atom': 'http://www.w3.org/2005/Atom', 'arxiv': 'http://arxiv.org/schemas/atom'}
    except ET.ParseError as e:
        print(f"Error parsing XML: {e}")
        return

    found_count = 0
    print("-" * 60)

    entries = root.findall('atom:entry', ns)
    if not entries:
        print("No entries found in feed.")
        return

    for entry in entries:
        title_elem = entry.find('atom:title', ns)
        summary_elem = entry.find('atom:summary', ns)
        id_elem = entry.find('atom:id', ns)
        link_elem = entry.find('atom:link[@rel="alternate"]', ns) # usually the abstract page
        published_elem = entry.find('atom:published', ns)

        title = get_text(title_elem).replace('\n', ' ').strip()
        summary = get_text(summary_elem).replace('\n', ' ').strip()
        paper_id = get_text(id_elem).split('/abs/')[-1]
        link = link_elem.attrib.get('href') if link_elem is not None else "N/A"
        published = get_text(published_elem)

        # Check for keywords (case-insensitive)
        hit = False
        for kw in KEYWORDS:
            if kw.lower() in title.lower() or kw.lower() in summary.lower():
                hit = True
                break
        
        if hit:
            found_count += 1
            print(f"MATCH: {title}")
            print(f"ID: {paper_id}")
            print(f"URL: {link}")
            print(f"Published: {published}")
            print(f"Summary: {summary[:200]}...")
            print("-" * 60)

    if found_count == 0:
        print("No new papers found matching S8 keywords in the latest 50 entries.")
    else:
        print(f"Found {found_count} potential papers. Please review and update s8_monitoring_log.md if relevant.")

if __name__ == "__main__":
    check_arxiv()
