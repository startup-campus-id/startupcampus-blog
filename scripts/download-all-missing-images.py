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
        
        print(f"✅ Downloaded: {filename}")
        return relative_path
        
    except Exception as e:
        print(f"❌ Failed to download {url}: {e}")
        return None

def extract_featured_image(content):
    """Extract the first meaningful image from content as featured image"""
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
            for url in matches:
                # Skip small/icon images
                if any(skip in url.lower() for skip in ['icon', 'logo', 'favicon', 'avatar', '24x24', '48x48', '96x96']):
                    continue
                # Skip very long URLs that might be data URIs
                if len(url) > 500:
                    continue
                return url
    
    return None

def get_posts_without_featured_images():
    """Get all posts that don't have featured images"""
    posts_dir = "/home/idos/sc/startupcampus-blog/content/posts"
    posts_without_featured = []
    
    for filename in os.listdir(posts_dir):
        if filename.endswith('.md'):
            file_path = os.path.join(posts_dir, filename)
            
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check if already has featured_image
            if 'featured_image:' not in content:
                slug = filename.replace('.md', '')
                posts_without_featured.append(slug)
    
    return posts_without_featured

def fetch_and_process_post(slug):
    """Fetch post from WordPress API and add featured image"""
    try:
        # Fetch from WordPress API
        url = "https://www.startupcampus.id/blog/wp-json/wp/v2/posts"
        params = {"slug": slug}
        
        response = requests.get(url, params=params, timeout=10)
        if response.status_code != 200:
            print(f"❌ Failed to fetch {slug}: HTTP {response.status_code}")
            return False
        
        posts = response.json()
        if not posts:
            print(f"❌ No post found for slug: {slug}")
            return False
        
        post = posts[0]
        
        # Extract featured image
        featured_image_url = extract_featured_image(post['content']['rendered'])
        if not featured_image_url:
            print(f"⚠️  No image found for: {slug}")
            return False
        
        print(f"🔍 Processing: {slug}")
        print(f"   Image URL: {featured_image_url}")
        
        # Download the image
        local_image_path = download_image(featured_image_url)
        if not local_image_path:
            return False
        
        # Update the post file
        post_file = f"/home/idos/sc/startupcampus-blog/content/posts/{slug}.md"
        if not os.path.exists(post_file):
            print(f"❌ Post file not found: {post_file}")
            return False
        
        # Read current content
        with open(post_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        lines = content.split('\n')
        frontmatter_end = -1
        
        # Find frontmatter end
        for i, line in enumerate(lines):
            if i > 0 and line.strip() == '---':
                frontmatter_end = i
                break
        
        if frontmatter_end > 0:
            # Insert featured_image before the closing ---
            lines.insert(frontmatter_end, f'featured_image: "{local_image_path}"')
            new_content = '\n'.join(lines)
            
            # Write back
            with open(post_file, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            print(f"✅ Updated: {slug}")
            
            # Remove first image from content if it's the same
            remove_duplicate_image_from_content(post_file, featured_image_url)
            
            return True
        else:
            print(f"❌ Could not find frontmatter end in: {slug}")
            return False
            
    except Exception as e:
        print(f"❌ Error processing {slug}: {e}")
        return False

def remove_duplicate_image_from_content(file_path, featured_image_url):
    """Remove the featured image from content if it appears there"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        lines = content.split('\n')
        
        # Find frontmatter end
        frontmatter_end = -1
        for i, line in enumerate(lines):
            if i > 0 and line.strip() == '---':
                frontmatter_end = i
                break
        
        if frontmatter_end > 0:
            content_lines = lines[frontmatter_end + 1:]
            
            # Remove empty lines from start
            while content_lines and content_lines[0].strip() == '':
                content_lines.pop(0)
            
            # Check if first line is an image that matches our featured image
            if content_lines:
                first_line = content_lines[0].strip()
                if re.match(r'!\[.*?\]\(.*?\)', first_line):
                    # Extract URL from markdown image
                    img_match = re.search(r'!\[.*?\]\(([^)]+)\)', first_line)
                    if img_match:
                        img_url = img_match.group(1)
                        # If it's the same image, remove it
                        if img_url == featured_image_url or img_url in featured_image_url:
                            content_lines.pop(0)
                            # Remove following empty line if exists
                            if content_lines and content_lines[0].strip() == '':
                                content_lines.pop(0)
                            
                            # Reconstruct and save
                            new_content = '\n'.join(lines[:frontmatter_end + 1]) + '\n\n' + '\n'.join(content_lines)
                            with open(file_path, 'w', encoding='utf-8') as f:
                                f.write(new_content)
                            
                            print(f"   🗑️  Removed duplicate image from content")
        
    except Exception as e:
        print(f"   ⚠️  Error removing duplicate image: {e}")

def main():
    print("🖼️  Starting automatic image download for all posts...")
    print("=" * 60)
    
    # Get posts without featured images
    posts_to_process = get_posts_without_featured_images()
    
    print(f"📊 Found {len(posts_to_process)} posts without featured images")
    print("=" * 60)
    
    success_count = 0
    error_count = 0
    no_image_count = 0
    
    for i, slug in enumerate(posts_to_process, 1):
        print(f"\n[{i}/{len(posts_to_process)}] Processing: {slug}")
        
        result = fetch_and_process_post(slug)
        if result:
            success_count += 1
        else:
            if "No image found" in str(result):
                no_image_count += 1
            else:
                error_count += 1
        
        # Be nice to the server
        time.sleep(0.5)
        
        # Progress update every 10 posts
        if i % 10 == 0:
            print(f"\n📈 Progress: {i}/{len(posts_to_process)} processed")
            print(f"   ✅ Success: {success_count}")
            print(f"   ❌ Errors: {error_count}")
            print(f"   ⚠️  No images: {no_image_count}")
    
    print("\n" + "=" * 60)
    print("🎉 DOWNLOAD COMPLETE!")
    print("=" * 60)
    print(f"📊 Final Results:")
    print(f"   📝 Total posts processed: {len(posts_to_process)}")
    print(f"   ✅ Successfully added images: {success_count}")
    print(f"   ❌ Errors: {error_count}")
    print(f"   ⚠️  Posts without images: {no_image_count}")
    print(f"   📈 Success rate: {success_count/len(posts_to_process)*100:.1f}%")
    
    # Generate updated report
    print(f"\n📄 Generating updated image status report...")
    os.system("python3 /home/idos/sc/startupcampus-blog/scripts/check-images-status.py")

if __name__ == "__main__":
    main()