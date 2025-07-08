#!/usr/bin/env python3
import requests
import json
import os
import re
from datetime import datetime
from html import unescape
import time

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

def fetch_all_posts():
    """Fetch ALL posts from WordPress API using pagination"""
    base_url = "https://www.startupcampus.id/blog/wp-json/wp/v2/posts"
    all_posts = []
    page = 1
    per_page = 100  # Maximum allowed by most WordPress sites
    
    print("Fetching all posts from WordPress...")
    
    while True:
        params = {
            "per_page": per_page,
            "page": page,
            "status": "publish"
        }
        
        try:
            print(f"Fetching page {page}...")
            response = requests.get(base_url, params=params)
            response.raise_for_status()
            
            posts = response.json()
            
            if not posts:  # No more posts
                break
                
            all_posts.extend(posts)
            print(f"  Got {len(posts)} posts from page {page}")
            
            # Check if we got fewer posts than requested (last page)
            if len(posts) < per_page:
                break
                
            page += 1
            time.sleep(0.5)  # Be nice to the server
            
        except Exception as e:
            print(f"Error fetching page {page}: {e}")
            break
    
    # Also fetch categories and authors
    try:
        categories_url = "https://www.startupcampus.id/blog/wp-json/wp/v2/categories"
        cat_response = requests.get(categories_url, params={"per_page": 100})
        categories = {}
        if cat_response.status_code == 200:
            for cat in cat_response.json():
                categories[cat['id']] = cat['name']
        
        authors_url = "https://www.startupcampus.id/blog/wp-json/wp/v2/users"
        authors_response = requests.get(authors_url, params={"per_page": 100})
        authors = {}
        if authors_response.status_code == 200:
            for author in authors_response.json():
                authors[author['id']] = author['name']
                
    except Exception as e:
        print(f"Error fetching categories/authors: {e}")
        categories = {}
        authors = {}
    
    print(f"Total posts fetched: {len(all_posts)}")
    return all_posts, categories, authors

def create_markdown_file(post, categories, authors, overwrite=False):
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
    if os.path.exists(filename) and not overwrite:
        print(f"Skipping {slug} - file already exists")
        return False
    
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(frontmatter)
        status = "Updated" if os.path.exists(filename) else "Created"
        print(f"{status}: {slug}")
        return True
    except Exception as e:
        print(f"Error creating {slug}: {e}")
        return False

def main():
    import argparse
    parser = argparse.ArgumentParser(description='Sync all posts from WordPress')
    parser.add_argument('--overwrite', action='store_true', 
                      help='Overwrite existing files')
    parser.add_argument('--backup', action='store_true',
                      help='Create backup of existing posts first')
    args = parser.parse_args()
    
    if args.backup:
        print("Creating backup of existing posts...")
        backup_dir = f"/home/idos/sc/startupcampus-blog/content/posts-backup-{int(time.time())}"
        os.makedirs(backup_dir, exist_ok=True)
        import shutil
        for file in os.listdir("/home/idos/sc/startupcampus-blog/content/posts"):
            if file.endswith('.md'):
                shutil.copy2(f"/home/idos/sc/startupcampus-blog/content/posts/{file}", 
                           f"{backup_dir}/{file}")
        print(f"Backup created at: {backup_dir}")
    
    # Fetch all posts
    posts, categories, authors = fetch_all_posts()
    
    if not posts:
        print("No posts found!")
        return
    
    print(f"\nProcessing {len(posts)} posts...")
    
    created_count = 0
    updated_count = 0
    skipped_count = 0
    
    for i, post in enumerate(posts, 1):
        print(f"[{i}/{len(posts)}] Processing: {post['slug']}")
        
        filename = f"/home/idos/sc/startupcampus-blog/content/posts/{post['slug']}.md"
        file_exists = os.path.exists(filename)
        
        if create_markdown_file(post, categories, authors, args.overwrite):
            if file_exists and args.overwrite:
                updated_count += 1
            elif not file_exists:
                created_count += 1
        else:
            skipped_count += 1
    
    print(f"\n=== SYNC COMPLETE ===")
    print(f"Total posts processed: {len(posts)}")
    print(f"Created: {created_count}")
    print(f"Updated: {updated_count}")
    print(f"Skipped: {skipped_count}")
    
    # Count total files now
    total_files = len([f for f in os.listdir("/home/idos/sc/startupcampus-blog/content/posts") if f.endswith('.md')])
    print(f"Total posts in repo: {total_files}")

if __name__ == "__main__":
    main()