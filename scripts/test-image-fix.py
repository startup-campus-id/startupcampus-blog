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
            print(f"Already exists: {filename}")
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
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, content, re.IGNORECASE)
        if matches:
            # Return the first image URL found
            url = matches[0]
            # Skip very small images (likely icons)
            if 'icon' in url.lower() or 'logo' in url.lower():
                continue
            return url
    
    return None

def test_single_post():
    """Test with the Bank Indonesia post"""
    url = "https://www.startupcampus.id/blog/wp-json/wp/v2/posts"
    params = {"slug": "bank-indonesia-dukung-pemerintah-dengan-gandeng-startup-campus-untuk-berikan-sertifikasi-kompetensi-bnsp-bagi-pegawai"}
    
    response = requests.get(url, params=params)
    if response.status_code == 200:
        posts = response.json()
        if posts:
            post = posts[0]
            print(f"Testing with post: {post['title']['rendered']}")
            
            # Extract featured image
            featured_image = extract_featured_image(post['content']['rendered'])
            print(f"Featured image found: {featured_image}")
            
            if featured_image:
                # Download it
                local_path = download_image(featured_image)
                print(f"Local path: {local_path}")
                
                # Update the post file
                slug = post['slug']
                filename = f"/home/idos/sc/startupcampus-blog/content/posts/{slug}.md"
                
                if os.path.exists(filename):
                    # Read current content
                    with open(filename, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Add featured_image to frontmatter if not present
                    if 'featured_image:' not in content:
                        # Find the end of frontmatter
                        lines = content.split('\n')
                        frontmatter_end = -1
                        for i, line in enumerate(lines):
                            if i > 0 and line.strip() == '---':
                                frontmatter_end = i
                                break
                        
                        if frontmatter_end > 0:
                            # Insert featured_image before the closing ---
                            lines.insert(frontmatter_end, f'featured_image: "{local_path}"')
                            new_content = '\n'.join(lines)
                            
                            # Write back
                            with open(filename, 'w', encoding='utf-8') as f:
                                f.write(new_content)
                            
                            print(f"Updated {slug} with featured image")
                        else:
                            print("Could not find frontmatter end")
                    else:
                        print("Featured image already present")
                else:
                    print(f"Post file not found: {filename}")

if __name__ == "__main__":
    test_single_post()