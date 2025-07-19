#!/usr/bin/env python3
"""
Detailed manual analysis of specific cases that might have duplicate featured images.
"""

import os
import re
import yaml
from pathlib import Path
from urllib.parse import urlparse

def extract_frontmatter_and_content(file_path):
    """Extract frontmatter and content from a markdown file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if content.startswith('---'):
            parts = content.split('---', 2)
            if len(parts) >= 3:
                frontmatter_raw = parts[1]
                post_content = parts[2]
                try:
                    frontmatter = yaml.safe_load(frontmatter_raw)
                    return frontmatter, post_content
                except yaml.YAMLError as e:
                    print(f"Error parsing YAML in {file_path}: {e}")
                    return None, content
        
        return None, content
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return None, None

def extract_images_from_content(content):
    """Extract all image URLs from markdown content."""
    images = []
    
    # Find markdown images: ![alt](url)
    markdown_pattern = r'!\[.*?\]\((.*?)\)'
    markdown_images = re.findall(markdown_pattern, content)
    images.extend(markdown_images)
    
    # Find HTML img tags: <img src="url">
    html_pattern = r'<img[^>]+src=["\']([^"\']+)["\'][^>]*>'
    html_images = re.findall(html_pattern, content, re.IGNORECASE)
    images.extend(html_images)
    
    return images

def manual_analysis():
    """Manually analyze specific cases."""
    posts_dir = "/home/idos/sc/startupcampus-blog/content/posts"
    
    # Specific posts to examine based on automated analysis
    posts_to_check = [
        "rahasia-pengembangan-diri-dan-kunci-sukses-di-era-persaingan-global.md",
        "empowering-tomorrows-leaders-aiesec-in-ugm-and-danone-operations-international-join-forces-in-the-pursuit-of-equality-and-inclusion.md",
        "cara-mendaftar-prakerja-lewat-hp-panduan-lengkap-dan-cepat.md",
        "apa-itu-passion-dan-5-cara-menemukannya-dalam-karier.md",
        "school-of-data-digital-program-kolaborasi-startup-campus-dan-rumah-perubahan.md"
    ]
    
    print("MANUAL ANALYSIS OF POTENTIAL DUPLICATE CASES")
    print("="*60)
    
    for post_name in posts_to_check:
        file_path = os.path.join(posts_dir, post_name)
        if not os.path.exists(file_path):
            continue
            
        frontmatter, content = extract_frontmatter_and_content(file_path)
        if not frontmatter or not content:
            continue
            
        featured_image = frontmatter.get('featured_image', '')
        content_images = extract_images_from_content(content)
        
        # Get first few lines of content to see early images
        lines = content.split('\n')
        first_10_lines = '\n'.join(lines[:10])
        early_images = extract_images_from_content(first_10_lines)
        
        print(f"\nPost: {post_name}")
        print(f"Title: {frontmatter.get('title', 'No title')}")
        print(f"Featured Image: {featured_image}")
        print(f"Early content images ({len(early_images)}):")
        for img in early_images:
            print(f"  - {img}")
        
        # Check for same domain
        if featured_image and early_images:
            featured_domain = urlparse(featured_image).netloc or 'local'
            for early_img in early_images:
                early_domain = urlparse(early_img).netloc or 'local'
                if featured_domain == early_domain and featured_domain != 'local':
                    print(f"  ⚠️  SAME DOMAIN DETECTED: {featured_domain}")
                    
                    # Check if filenames are related
                    featured_filename = os.path.basename(urlparse(featured_image).path)
                    early_filename = os.path.basename(urlparse(early_img).path)
                    
                    # Remove extensions and common suffixes
                    featured_base = re.sub(r'-\d+x\d+', '', os.path.splitext(featured_filename)[0])
                    early_base = re.sub(r'-\d+x\d+', '', os.path.splitext(early_filename)[0])
                    
                    print(f"     Featured filename: {featured_filename} (base: {featured_base})")
                    print(f"     Early img filename: {early_filename} (base: {early_base})")
                    
                    if featured_base.lower() in early_base.lower() or early_base.lower() in featured_base.lower():
                        print(f"     🚨 POTENTIAL FILENAME SIMILARITY!")
        
        print("-" * 60)

def find_potential_visual_duplicates():
    """Look for posts where images might be visually the same but from different sources."""
    posts_dir = "/home/idos/sc/startupcampus-blog/content/posts"
    posts_path = Path(posts_dir)
    
    md_files = list(posts_path.glob("*.md"))
    
    print("\nLOOKING FOR POTENTIAL VISUAL DUPLICATES")
    print("="*60)
    print("(Cases where featured image and early content image might be the same image from different sources)")
    
    potential_cases = []
    
    for md_file in md_files:
        frontmatter, content = extract_frontmatter_and_content(md_file)
        
        if not frontmatter or not content:
            continue
            
        featured_image = frontmatter.get('featured_image', '')
        if not featured_image:
            continue
            
        # Check first 3 paragraphs for images
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
        early_content = '\n\n'.join(paragraphs[:3])
        early_images = extract_images_from_content(early_content)
        
        if early_images:
            # Check if featured image is local blog and early image is external (or vice versa)
            featured_domain = urlparse(featured_image).netloc or 'local'
            
            for early_img in early_images:
                early_domain = urlparse(early_img).netloc or 'local'
                
                # Flag cases where one is local blog image and other is external
                if ((featured_domain == 'local' and early_domain != 'local') or 
                    (featured_domain != 'local' and early_domain == 'local')):
                    
                    potential_cases.append({
                        'filename': md_file.name,
                        'title': frontmatter.get('title', 'No title'),
                        'featured_image': featured_image,
                        'featured_domain': featured_domain,
                        'early_image': early_img,
                        'early_domain': early_domain
                    })
    
    if potential_cases:
        print(f"\nFound {len(potential_cases)} potential cases where featured image and early content image")
        print("might be the same image from different sources:\n")
        
        for i, case in enumerate(potential_cases[:10], 1):  # Show first 10
            print(f"{i}. {case['filename']}")
            print(f"   Title: {case['title']}")
            print(f"   Featured ({case['featured_domain']}): {case['featured_image']}")
            print(f"   Early content ({case['early_domain']}): {case['early_image']}")
            print()
        
        if len(potential_cases) > 10:
            print(f"... and {len(potential_cases) - 10} more similar cases.")
    else:
        print("No obvious patterns found.")

if __name__ == "__main__":
    manual_analysis()
    find_potential_visual_duplicates()