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
        os.makedirs(destination_dir, exist_ok=True)
        
        parsed_url = urlparse(url)
        path = unquote(parsed_url.path)
        ext = os.path.splitext(path)[1] if os.path.splitext(path)[1] else '.jpg'
        
        url_hash = hashlib.md5(url.encode()).hexdigest()[:12]
        filename = f"{url_hash}{ext}"
        local_path = os.path.join(destination_dir, filename)
        relative_path = f"/images/{filename}"
        
        if os.path.exists(local_path):
            return relative_path
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        with open(local_path, 'wb') as f:
            f.write(response.content)
        
        print(f"Downloaded: {filename}")
        return relative_path
        
    except Exception as e:
        print(f"Failed to download {url}: {e}")
        return url

def extract_featured_image(content):
    """Extract the first image from content as featured image"""
    if not content:
        return None
    
    patterns = [
        r'<img[^>]*src=["\']([^"\']+)["\'][^>]*>',
        r'!\[[^\]]*\]\(([^)]+)\)',
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, content, re.IGNORECASE)
        if matches:
            url = matches[0]
            if 'icon' in url.lower() or 'logo' in url.lower():
                continue
            return url
    
    return None

def update_post_with_featured_image(slug, featured_image_url, categories):
    """Update a post file with featured image and correct categories"""
    filename = f"/home/idos/sc/startupcampus-blog/content/posts/{slug}.md"
    
    if not os.path.exists(filename):
        print(f"Post file not found: {filename}")
        return False
    
    # Download featured image
    local_image_path = download_image(featured_image_url)
    
    # Read current content
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()
    
    lines = content.split('\n')
    frontmatter_end = -1
    categories_line = -1
    featured_image_line = -1
    
    # Find frontmatter boundaries and existing fields
    for i, line in enumerate(lines):
        if i > 0 and line.strip() == '---':
            frontmatter_end = i
            break
        if line.startswith('categories:'):
            categories_line = i
        if line.startswith('featured_image:'):
            featured_image_line = i
    
    if frontmatter_end > 0:
        # Update categories
        if categories_line >= 0:
            lines[categories_line] = f'categories: {json.dumps(categories)}'
        else:
            lines.insert(frontmatter_end, f'categories: {json.dumps(categories)}')
            frontmatter_end += 1
        
        # Update featured image
        if featured_image_line >= 0:
            lines[featured_image_line] = f'featured_image: "{local_image_path}"'
        else:
            lines.insert(frontmatter_end, f'featured_image: "{local_image_path}"')
        
        # Write back
        new_content = '\n'.join(lines)
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print(f"Updated {slug}")
        return True
    
    return False

def fix_recent_posts():
    """Fix the most recent posts with correct categories and images"""
    url = "https://www.startupcampus.id/blog/wp-json/wp/v2/posts"
    params = {"per_page": 10}
    
    # Get categories mapping
    categories_url = "https://www.startupcampus.id/blog/wp-json/wp/v2/categories"
    cat_response = requests.get(categories_url, params={"per_page": 100})
    categories_map = {}
    if cat_response.status_code == 200:
        for cat in cat_response.json():
            categories_map[cat['id']] = cat['name']
    
    response = requests.get(url, params=params)
    if response.status_code == 200:
        posts = response.json()
        
        for post in posts:
            print(f"\nProcessing: {post['title']['rendered']}")
            
            # Get featured image
            featured_image = extract_featured_image(post['content']['rendered'])
            if not featured_image:
                print("  No featured image found")
                continue
            
            # Get category names
            post_categories = []
            for cat_id in post['categories']:
                cat_name = categories_map.get(cat_id, '')
                if cat_name:
                    post_categories.append(cat_name)
            
            if not post_categories:
                post_categories = ['Digital', 'Semua', 'Update']
            
            print(f"  Categories: {post_categories}")
            print(f"  Featured image: {featured_image}")
            
            # Update the post
            update_post_with_featured_image(post['slug'], featured_image, post_categories)

if __name__ == "__main__":
    fix_recent_posts()