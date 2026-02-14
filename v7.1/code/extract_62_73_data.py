#!/usr/bin/env python3
"""
Extract Jones polynomial and volume data for 6_2 and 7_3 from KnotInfo SSoT

Author: Claude Opus 4.6
Date: 2026-02-14
"""

import csv
from pathlib import Path

# Load SSoT
data_file = Path(__file__).parent.parent.parent / 'data' / 'knotinfo_data_complete.csv'

with open(data_file, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f, delimiter='|')

    for row in reader:
        name = row['name']
        if name in ['6_2', '7_3', '6_1', '7_2', '4_1']:  # Include 4_1, 6_1, 7_2 for reference
            jones = row.get('jones_polynomial', 'N/A')
            volume = row.get('volume', 'N/A')

            print(f"\n{'='*70}")
            print(f"Knot: {name}")
            print(f"{'='*70}")
            print(f"Volume: {volume}")
            print(f"\nJones Polynomial:")
            print(f"{jones}")
            print()
