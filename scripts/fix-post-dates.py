#!/usr/bin/env python3
"""
Fix post dates to be in the past so Hugo displays them properly.
"""

import os
import re
import glob
from pathlib import Path
from datetime import datetime, timedelta
import random

def fix_post_dates():
    """Fix post dates to be distributed over the past 2 years."""
    posts_dir = Path(__file__).parent.parent / 'content' / 'posts'
    
    if not posts_dir.exists():
        print(f"Posts directory not found: {posts_dir}")
        return
    
    post_files = list(posts_dir.glob('*.md'))
    
    if not post_files:
        print("No markdown files found in posts directory")
        return
    
    print(f"Found {len(post_files)} posts to fix")
    
    # Generate dates spread over the past 2 years
    end_date = datetime.now()
    start_date = end_date - timedelta(days=730)  # 2 years ago
    
    # Create list of random dates
    dates = []
    for i in range(len(post_files)):
        random_days = random.randint(0, 730)
        post_date = start_date + timedelta(days=random_days)
        dates.append(post_date)
    
    # Sort dates in descending order (newest first)
    dates.sort(reverse=True)
    
    for i, post_file in enumerate(post_files):
        fix_single_post(post_file, dates[i])
    
    print(f"\nFixed dates for {len(post_files)} posts!")

def fix_single_post(filepath, new_date):
    """Fix the date in a single post file."""
    print(f"Fixing {filepath.name}...")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace the date line in frontmatter
    date_pattern = r'date: 2025-07-08T08:33:46\.\d+'
    new_date_str = new_date.strftime('%Y-%m-%dT%H:%M:%S')
    
    updated_content = re.sub(date_pattern, f'date: {new_date_str}', content)
    
    # Write back to file
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(updated_content)

if __name__ == '__main__':
    fix_post_dates()