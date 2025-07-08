#!/usr/bin/env python3
import requests
import json
import os
import re
from datetime import datetime
from html import unescape
import time
from urllib.parse import urlparse, unquote
import hashlib

def download_image(url, destination_dir="/home/idos/sc/startupcampus-blog/static/images"):
    """Download an image and return the local path"""
    try:
        # Create images directory if it doesn't exist
        os.makedirs(destination_dir, exist_ok=True)
        
        # Get file extension from URL
        parsed_url = urlparse(url)
        path = unquote(parsed_url.path)
        ext = os.path.splitext(path)[1] if os.path.splitext(path)[1] else '.jpg'
        
        # Create a unique filename based on URL hash
        url_hash = hashlib.md5(url.encode()).hexdigest()[:12]
        filename = f"{url_hash}{ext}"
        local_path = os.path.join(destination_dir, filename)
        relative_path = f"/images/{filename}"
        
        # Skip if already downloaded
        if os.path.exists(local_path):
            return relative_path
        
        # Download the image
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        # Save the image
        with open(local_path, 'wb') as f:
            f.write(response.content)
        
        print(f"Downloaded: {filename}")
        return relative_path
        
    except Exception as e:
        print(f"Failed to download {url}: {e}")
        return url  # Return original URL if download fails

def extract_featured_image(content):
    """Extract the first image from content as featured image"""
    if not content:
        return None
    
    # Try to find images in various formats
    patterns = [
        r'<img[^>]*src=["\']([^"\']+)["\'][^>]*>',
        r'!\[[^\]]*\]\(([^)]+)\)',
        r'src=["\']([^"\']+)["\']'
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, content, re.IGNORECASE)
        if matches:
            # Return the first image URL found
            return matches[0]
    
    return None

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
    
    # Convert images - download them and update URLs
    img_pattern = r'<img[^>]*src="([^"]*)"[^>]*alt="([^"]*)"[^>]*/?>'
    def replace_img_with_download(match):
        img_url = match.group(1)
        alt_text = match.group(2)
        
        # Skip if already local
        if img_url.startswith('/'):
            return f'![{alt_text}]({img_url})'
        
        # Download and replace with local path
        local_path = download_image(img_url)
        return f'![{alt_text}]({local_path})'
    
    content = re.sub(img_pattern, replace_img_with_download, content, flags=re.DOTALL)
    
    # Handle images without alt text
    img_pattern_no_alt = r'<img[^>]*src="([^"]*)"[^>]*/?>'
    def replace_img_no_alt(match):
        img_url = match.group(1)
        
        # Skip if already local
        if img_url.startswith('/'):
            return f'![]({img_url})'
        
        # Download and replace with local path
        local_path = download_image(img_url)
        return f'![]({local_path})'
    
    content = re.sub(img_pattern_no_alt, replace_img_no_alt, content, flags=re.DOTALL)
    
    # Convert markdown images - download them too
    md_img_pattern = r'!\[([^\]]*)\]\(([^)]+)\)'
    def replace_md_img(match):
        alt_text = match.group(1)
        img_url = match.group(2)
        
        # Skip if already local
        if img_url.startswith('/'):
            return f'![{alt_text}]({img_url})'
        
        # Download and replace with local path
        local_path = download_image(img_url)
        return f'![{alt_text}]({local_path})'
    
    content = re.sub(md_img_pattern, replace_md_img, content)
    
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
    """Fetch ALL posts from WordPress API"""
    base_url = "https://www.startupcampus.id/blog/wp-json/wp/v2/posts"
    all_posts = []
    page = 1
    per_page = 100
    
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
            
            if not posts:
                break
                
            all_posts.extend(posts)
            print(f"  Got {len(posts)} posts from page {page}")
            
            if len(posts) < per_page:
                break
                
            page += 1
            time.sleep(0.5)
            
        except Exception as e:
            print(f"Error fetching page {page}: {e}")
            break
    
    # Fetch categories and authors
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

def create_markdown_file(post, categories, authors, overwrite=True):
    """Create a markdown file with proper featured image"""
    title = post['title']['rendered']
    slug = post['slug']
    raw_content = post['content']['rendered']
    date = post['date']
    
    # Extract featured image BEFORE cleaning content
    featured_image = extract_featured_image(raw_content)
    if featured_image:
        # Download featured image
        featured_image = download_image(featured_image)
    
    # Clean content (this will also download images within content)
    content = clean_html_content(raw_content)
    
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
    
    # Create frontmatter with featured image
    frontmatter = f"""---
title: "{title}"
date: {hugo_date}
author: "{author}"
categories: {json.dumps(post_categories)}
slug: "{slug}"
"""
    
    if featured_image:
        frontmatter += f'featured_image: "{featured_image}"\n'
    
    frontmatter += f"""---

{content}
"""
    
    # Write to file
    filename = f"/home/idos/sc/startupcampus-blog/content/posts/{slug}.md"
    
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(frontmatter)
        print(f"Updated: {slug}")
        return True
    except Exception as e:
        print(f"Error updating {slug}: {e}")
        return False

def main():
    print("🖼️  Downloading images and fixing layout...")
    
    # Fetch all posts
    posts, categories, authors = fetch_all_posts()
    
    if not posts:
        print("No posts found!")
        return
    
    print(f"\nProcessing {len(posts)} posts...")
    
    updated_count = 0
    
    for i, post in enumerate(posts, 1):
        print(f"[{i}/{len(posts)}] Processing: {post['slug']}")
        
        if create_markdown_file(post, categories, authors, overwrite=True):
            updated_count += 1
    
    print(f"\n=== SYNC WITH IMAGES COMPLETE ===")
    print(f"Total posts processed: {len(posts)}")
    print(f"Updated: {updated_count}")
    
    # Count total files
    total_files = len([f for f in os.listdir("/home/idos/sc/startupcampus-blog/content/posts") if f.endswith('.md')])
    print(f"Total posts in repo: {total_files}")

if __name__ == "__main__":
    main()