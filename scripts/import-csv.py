#!/usr/bin/env python3
import csv
import os
import re
from datetime import datetime

def slugify(text):
    """Create URL-friendly slug"""
    if not text:
        return "untitled"
    text = re.sub(r'[^\w\s-]', '', text.lower())
    return re.sub(r'[-\s]+', '-', text).strip('-')

def create_post_from_csv(posts_csv, categories_csv):
    """Create Hugo posts from CSV data"""
    posts_created = 0
    
    # Read categories
    categories_dict = {}
    try:
        with open(categories_csv, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                categories_dict[row.get('term_id', '')] = row.get('name', '')
    except Exception as e:
        print(f"Warning: Could not read categories: {e}")
    
    # Read posts
    with open(posts_csv, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            title = row.get('post_title', 'Untitled')
            slug = slugify(title)
            
            # Create Hugo front matter
            escaped_title = title.replace('"', '\\"')
            front_matter = f"""---
title: "{escaped_title}"
date: {datetime.now().isoformat()}
slug: "{slug}"
categories: []
tags: []
draft: false
---

"""
            
            # Create sample content
            content = f"# {title}\n\nContent imported from WordPress. Please edit this post.\n"
            
            # Create output directory
            output_dir = 'content/posts'
            os.makedirs(output_dir, exist_ok=True)
            
            # Write file
            filename = f"{slug}.md"
            filepath = os.path.join(output_dir, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(front_matter)
                f.write(content)
            
            print(f"Created: {filepath}")
            posts_created += 1
    
    print(f"\n✅ Import complete!")
    print(f"📝 Posts created: {posts_created}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        print("Usage: python import-csv.py posts.csv categories.csv")
        sys.exit(1)
    
    create_post_from_csv(sys.argv[1], sys.argv[2])