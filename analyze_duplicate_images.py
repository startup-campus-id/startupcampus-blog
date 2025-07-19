#!/usr/bin/env python3
"""
Script to find blog posts where the featured image is duplicated in the post content body.
"""

import os
import re
import yaml
from pathlib import Path
from urllib.parse import urlparse
import sys

def extract_frontmatter_and_content(file_path):
    """Extract frontmatter and content from a markdown file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Split frontmatter and content
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

def normalize_url(url):
    """Normalize URL for comparison by removing protocol, trailing slashes, etc."""
    if not url:
        return ""
    
    # Remove leading/trailing whitespace
    url = url.strip()
    
    # Parse URL to get path
    parsed = urlparse(url)
    path = parsed.path.rstrip('/')
    
    # Extract filename from path
    filename = os.path.basename(path)
    
    return filename.lower()

def find_image_in_content_sections(content, max_paragraphs=3):
    """Find images that appear in the first few paragraphs of content."""
    # Split content into paragraphs
    paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
    
    # Check first few paragraphs
    early_content = '\n\n'.join(paragraphs[:max_paragraphs])
    
    return extract_images_from_content(early_content)

def are_images_similar(img1, img2):
    """Check if two image URLs might be similar/related."""
    if not img1 or not img2:
        return False
    
    # Exact filename match
    filename1 = normalize_url(img1)
    filename2 = normalize_url(img2)
    if filename1 == filename2:
        return True
    
    # Check if both contain same base filename (without extension)
    base1 = os.path.splitext(filename1)[0]
    base2 = os.path.splitext(filename2)[0]
    if base1 and base2 and base1 == base2:
        return True
    
    # Check if one URL contains the other filename
    if filename1 in img2.lower() or filename2 in img1.lower():
        return True
    
    return False

def analyze_posts(posts_dir):
    """Analyze all posts for duplicate featured images."""
    results = []
    stats = {
        'total_posts': 0,
        'posts_with_featured_image': 0,
        'posts_with_content_images': 0,
        'common_image_patterns': {}
    }
    
    posts_path = Path(posts_dir)
    if not posts_path.exists():
        print(f"Posts directory not found: {posts_dir}")
        return results, stats
    
    md_files = list(posts_path.glob("*.md"))
    print(f"Analyzing {len(md_files)} blog posts...")
    stats['total_posts'] = len(md_files)
    
    for md_file in md_files:
        frontmatter, content = extract_frontmatter_and_content(md_file)
        
        if not frontmatter or not content:
            continue
            
        featured_image = frontmatter.get('featured_image', '')
        
        # Extract all images from content
        content_images = extract_images_from_content(content)
        early_content_images = find_image_in_content_sections(content, max_paragraphs=5)
        
        # Update stats
        if featured_image:
            stats['posts_with_featured_image'] += 1
        if content_images:
            stats['posts_with_content_images'] += 1
            
        # Track image domain patterns
        for img in content_images:
            parsed = urlparse(img)
            domain = parsed.netloc or 'local'
            stats['common_image_patterns'][domain] = stats['common_image_patterns'].get(domain, 0) + 1
        
        if featured_image:
            parsed = urlparse(featured_image)
            domain = parsed.netloc or 'local'
            stats['common_image_patterns'][domain] = stats['common_image_patterns'].get(domain, 0) + 1
        
        # Look for similar/duplicate images
        duplicates = []
        similar_images = []
        early_duplicates = []
        
        for img in content_images:
            if are_images_similar(featured_image, img):
                duplicates.append(img)
                
        for img in early_content_images:
            if are_images_similar(featured_image, img):
                early_duplicates.append(img)
            elif featured_image and img:
                # Check for potential visual duplicates (same article topic)
                # This is a heuristic check
                similar_images.append(img)
        
        # Always include posts with interesting patterns for analysis
        include_in_results = False
        
        if duplicates:
            include_in_results = True
        elif featured_image and early_content_images:
            # Flag posts with featured image and early content images for manual review
            include_in_results = True
            
        if include_in_results:
            # Find line numbers where images appear
            image_locations = []
            lines = content.split('\n')
            for i, line in enumerate(lines, 1):
                for img in content_images:
                    if img in line:
                        image_locations.append(f"Line {i}: {line.strip()[:100]}...")
            
            results.append({
                'filename': md_file.name,
                'title': frontmatter.get('title', 'No title'),
                'featured_image': featured_image,
                'duplicate_images': duplicates,
                'early_content_duplicates': early_duplicates,
                'all_content_images': content_images,
                'early_content_images': early_content_images,
                'similar_images': similar_images,
                'image_locations': image_locations,
                'total_content_images': len(content_images)
            })
    
    return results, stats

def generate_report(results, stats):
    """Generate a detailed report of findings."""
    print("\n" + "="*80)
    print("BLOG POSTS IMAGE ANALYSIS REPORT")
    print("="*80)
    
    # General statistics
    print(f"\nOVERALL STATISTICS:")
    print(f"Total posts analyzed: {stats['total_posts']}")
    print(f"Posts with featured images: {stats['posts_with_featured_image']}")
    print(f"Posts with content images: {stats['posts_with_content_images']}")
    
    print(f"\nIMAGE SOURCE PATTERNS:")
    for domain, count in sorted(stats['common_image_patterns'].items(), key=lambda x: x[1], reverse=True):
        print(f"  {domain}: {count} images")
    
    # Separate exact duplicates from posts with potential issues
    exact_duplicates = [r for r in results if r['duplicate_images']]
    potential_issues = [r for r in results if not r['duplicate_images'] and r['early_content_images']]
    
    print("\n" + "="*80)
    print("EXACT DUPLICATE FEATURED IMAGES")
    print("="*80)
    
    if not exact_duplicates:
        print("No posts found with exact duplicate featured images.")
    else:
        print(f"\nFound {len(exact_duplicates)} posts with exact duplicate featured images:\n")
        
        for i, result in enumerate(exact_duplicates, 1):
            print(f"{i}. {result['filename']}")
            print(f"   Title: {result['title']}")
            print(f"   Featured Image: {result['featured_image']}")
            print(f"   Duplicate images found: {len(result['duplicate_images'])}")
            
            if result['early_content_duplicates']:
                print(f"   ⚠️  Duplicates in early content: {len(result['early_content_duplicates'])}")
            
            print("   Duplicate image URLs:")
            for dup in result['duplicate_images']:
                print(f"     - {dup}")
            print("")
    
    print("\n" + "="*80)
    print("POSTS WITH FEATURED IMAGES AND EARLY CONTENT IMAGES")
    print("(Potential for manual review)")
    print("="*80)
    
    if not potential_issues:
        print("No posts found requiring manual review.")
    else:
        print(f"\nFound {len(potential_issues)} posts with both featured images and early content images:\n")
        
        for i, result in enumerate(potential_issues[:10], 1):  # Show first 10
            print(f"{i}. {result['filename']}")
            print(f"   Title: {result['title']}")
            print(f"   Featured Image: {result['featured_image']}")
            print(f"   Early content images ({len(result['early_content_images'])}):")
            for img in result['early_content_images'][:3]:  # Show first 3
                print(f"     - {img}")
            if len(result['early_content_images']) > 3:
                print(f"     ... and {len(result['early_content_images']) - 3} more")
            print("")
        
        if len(potential_issues) > 10:
            print(f"... and {len(potential_issues) - 10} more posts with similar patterns")

def main():
    """Main function."""
    posts_dir = "/home/idos/sc/startupcampus-blog/content/posts"
    
    print("Starting analysis of blog posts for duplicate featured images...")
    results, stats = analyze_posts(posts_dir)
    generate_report(results, stats)
    
    # Summary statistics
    exact_duplicates = len([r for r in results if r['duplicate_images']])
    potential_issues = len([r for r in results if not r['duplicate_images'] and r['early_content_images']])
    
    print("\n" + "="*80)
    print("FINAL SUMMARY")
    print("="*80)
    print(f"Posts with exact duplicate featured images: {exact_duplicates}")
    print(f"Posts requiring manual review: {potential_issues}")
    print(f"Total posts analyzed: {stats['total_posts']}")
    print(f"Analysis complete!")

if __name__ == "__main__":
    main()