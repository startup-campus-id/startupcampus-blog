#!/usr/bin/env python3
import requests
import json
import os
import re
from datetime import datetime
from html import unescape

def clean_html_content(content):
    """Convert HTML content to markdown"""
    if not content:
        return ""
    
    # Remove script and style tags
    content = re.sub(r'<script[^>]*>.*?</script>', '', content, flags=re.DOTALL | re.IGNORECASE)
    content = re.sub(r'<style[^>]*>.*?</style>', '', content, flags=re.DOTALL | re.IGNORECASE)
    
    # Convert basic HTML to markdown
    content = re.sub(r'<h1[^>]*>(.*?)</h1>', r'# \1', content, flags=re.DOTALL)
    content = re.sub(r'<h2[^>]*>(.*?)</h2>', r'## \1', content, flags=re.DOTALL)
    content = re.sub(r'<h3[^>]*>(.*?)</h3>', r'### \1', content, flags=re.DOTALL)
    content = re.sub(r'<h4[^>]*>(.*?)</h4>', r'#### \1', content, flags=re.DOTALL)
    content = re.sub(r'<h5[^>]*>(.*?)</h5>', r'##### \1', content, flags=re.DOTALL)
    content = re.sub(r'<h6[^>]*>(.*?)</h6>', r'###### \1', content, flags=re.DOTALL)
    
    # Convert paragraphs
    content = re.sub(r'<p[^>]*>(.*?)</p>', r'\1\n\n', content, flags=re.DOTALL)
    
    # Convert lists
    content = re.sub(r'<ul[^>]*>(.*?)</ul>', r'\1', content, flags=re.DOTALL)
    content = re.sub(r'<ol[^>]*>(.*?)</ol>', r'\1', content, flags=re.DOTALL)
    content = re.sub(r'<li[^>]*>(.*?)</li>', r'- \1\n', content, flags=re.DOTALL)
    
    # Convert links
    content = re.sub(r'<a[^>]*href="([^"]*)"[^>]*>(.*?)</a>', r'[\2](\1)', content, flags=re.DOTALL)
    
    # Convert bold and italic
    content = re.sub(r'<strong[^>]*>(.*?)</strong>', r'**\1**', content, flags=re.DOTALL)
    content = re.sub(r'<b[^>]*>(.*?)</b>', r'**\1**', content, flags=re.DOTALL)
    content = re.sub(r'<em[^>]*>(.*?)</em>', r'*\1*', content, flags=re.DOTALL)
    content = re.sub(r'<i[^>]*>(.*?)</i>', r'*\1*', content, flags=re.DOTALL)
    
    # Convert images
    content = re.sub(r'<img[^>]*src="([^"]*)"[^>]*alt="([^"]*)"[^>]*/?>', r'![\2](\1)', content, flags=re.DOTALL)
    content = re.sub(r'<img[^>]*src="([^"]*)"[^>]*/?>', r'![](\1)', content, flags=re.DOTALL)
    
    # Convert blockquotes
    content = re.sub(r'<blockquote[^>]*>(.*?)</blockquote>', r'> \1\n', content, flags=re.DOTALL)
    
    # Remove remaining HTML tags
    content = re.sub(r'<[^>]+>', '', content)
    
    # Clean up HTML entities
    content = unescape(content)
    
    # Clean up extra whitespace
    content = re.sub(r'\n\s*\n\s*\n', '\n\n', content)
    content = content.strip()
    
    return content

def fetch_posts():
    """Fetch latest posts from WordPress API"""
    url = "https://www.startupcampus.id/blog/wp-json/wp/v2/posts"
    params = {"per_page": 20}
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        posts = response.json()
        
        # Also fetch categories
        categories_url = "https://www.startupcampus.id/blog/wp-json/wp/v2/categories"
        cat_response = requests.get(categories_url)
        categories = {}
        if cat_response.status_code == 200:
            for cat in cat_response.json():
                categories[cat['id']] = cat['name']
        
        # Also fetch authors
        authors_url = "https://www.startupcampus.id/blog/wp-json/wp/v2/users"
        authors_response = requests.get(authors_url)
        authors = {}
        if authors_response.status_code == 200:
            for author in authors_response.json():
                authors[author['id']] = author['name']
        
        return posts, categories, authors
        
    except Exception as e:
        print(f"Error fetching posts: {e}")
        return [], {}, {}

def create_markdown_file(post, categories, authors):
    """Create a markdown file from post data"""
    title = post['title']['rendered']
    slug = post['slug']
    content = clean_html_content(post['content']['rendered'])
    date = post['date']
    
    # Get author name
    author = authors.get(post['author'], 'Startup Campus')
    
    # Get category names
    post_categories = []
    for cat_id in post['categories']:
        cat_name = categories.get(cat_id, '')
        if cat_name:
            post_categories.append(cat_name)
    
    if not post_categories:
        post_categories = ['Digital', 'Semua', 'Update']
    
    # Format date for Hugo
    date_obj = datetime.fromisoformat(date.replace('Z', '+00:00'))
    hugo_date = date_obj.strftime('%Y-%m-%dT%H:%M:%S')
    
    # Create frontmatter
    frontmatter = f"""---
title: "{title}"
date: {hugo_date}
author: "{author}"
categories: {json.dumps(post_categories)}
slug: "{slug}"
---

{content}
"""
    
    # Write to file
    filename = f"/home/idos/sc/startupcampus-blog/content/posts/{slug}.md"
    
    # Check if file already exists
    if os.path.exists(filename):
        print(f"Skipping {slug} - file already exists")
        return False
    
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(frontmatter)
        print(f"Created: {slug}")
        return True
    except Exception as e:
        print(f"Error creating {slug}: {e}")
        return False

def main():
    print("Fetching latest posts from WordPress...")
    posts, categories, authors = fetch_posts()
    
    if not posts:
        print("No posts found!")
        return
    
    print(f"Found {len(posts)} posts")
    
    created_count = 0
    for post in posts:
        # Only process posts from 2024 onwards
        post_date = datetime.fromisoformat(post['date'].replace('Z', '+00:00'))
        if post_date.year >= 2024:
            if create_markdown_file(post, categories, authors):
                created_count += 1
    
    print(f"Created {created_count} new posts")

if __name__ == "__main__":
    main()