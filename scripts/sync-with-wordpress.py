#!/usr/bin/env python3
"""
Sync Hugo posts with WordPress site data.
Fetch actual metadata and content from WordPress and update Hugo markdown files.
"""

import os
import re
import time
import requests
from pathlib import Path
from datetime import datetime
from bs4 import BeautifulSoup
import json

def fetch_wordpress_post(slug):
    """Fetch post data from WordPress site."""
    url = f"https://www.startupcampus.id/blog/{slug}/"
    
    try:
        print(f"Fetching: {url}")
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract metadata from JSON-LD structured data
        metadata = {}
        json_ld = soup.find('script', type='application/ld+json')
        if json_ld:
            try:
                data = json.loads(json_ld.string)
                if isinstance(data, list):
                    # Find BlogPosting object
                    for item in data:
                        if item.get('@type') == 'BlogPosting':
                            data = item
                            break
                
                if data.get('@type') == 'BlogPosting':
                    metadata['title'] = data.get('headline', '')
                    metadata['date'] = data.get('datePublished', '')
                    metadata['author'] = data.get('author', {}).get('name', '') if isinstance(data.get('author'), dict) else ''
                    metadata['description'] = data.get('description', '')
            except json.JSONDecodeError:
                pass
        
        # Fallback: Extract from HTML meta tags and content
        if not metadata.get('title'):
            title_tag = soup.find('title')
            if title_tag:
                metadata['title'] = title_tag.text.strip()
                # Clean up title (remove site name)
                metadata['title'] = re.sub(r'\s*-\s*Startup Campus.*$', '', metadata['title'])
        
        if not metadata.get('date'):
            # Look for date in various places
            date_meta = soup.find('meta', {'property': 'article:published_time'})
            if date_meta:
                metadata['date'] = date_meta.get('content', '')
            else:
                # Look for date in post content
                date_span = soup.find('time')
                if date_span:
                    metadata['date'] = date_span.get('datetime', date_span.text.strip())
        
        if not metadata.get('author'):
            # Look for author in meta tags
            author_meta = soup.find('meta', {'name': 'author'})
            if author_meta:
                metadata['author'] = author_meta.get('content', '')
            else:
                # Look for author in post content
                author_span = soup.find('span', class_=re.compile(r'author'))
                if author_span:
                    metadata['author'] = author_span.text.strip()
        
        # Extract categories and tags
        categories = []
        tags = []
        
        # Look for category links
        cat_links = soup.find_all('a', href=re.compile(r'/category/'))
        for link in cat_links:
            categories.append(link.text.strip())
        
        # Look for tag links  
        tag_links = soup.find_all('a', href=re.compile(r'/tag/'))
        for link in tag_links:
            tags.append(link.text.strip())
        
        metadata['categories'] = list(set(categories)) if categories else []
        metadata['tags'] = list(set(tags)) if tags else []
        
        # Extract main content
        content = ""
        
        # Try different content selectors
        content_selectors = [
            'article .entry-content',
            '.post-content',
            '.content',
            'article',
            '.post'
        ]
        
        for selector in content_selectors:
            content_div = soup.select_one(selector)
            if content_div:
                content = str(content_div)
                break
        
        if not content:
            # Fallback: get all p tags within main content area
            main = soup.find('main') or soup.find('body')
            if main:
                paragraphs = main.find_all('p')
                content = '\n'.join(str(p) for p in paragraphs[:20])  # First 20 paragraphs
        
        return {
            'metadata': metadata,
            'content': content,
            'success': True
        }
        
    except requests.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return {'success': False, 'error': str(e)}
    except Exception as e:
        print(f"Error processing {url}: {e}")
        return {'success': False, 'error': str(e)}

def html_to_markdown_basic(html_content):
    """Convert HTML to basic markdown."""
    if not html_content:
        return ""
    
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Remove script and style elements
    for script in soup(["script", "style"]):
        script.decompose()
    
    # Convert to text and basic markdown
    text = soup.get_text()
    
    # Clean up whitespace
    lines = (line.strip() for line in text.splitlines())
    text = '\n'.join(line for line in lines if line)
    
    return text

def parse_date(date_string):
    """Parse various date formats and return ISO format."""
    if not date_string:
        return ""
    
    # Common date formats to try
    formats = [
        '%Y-%m-%dT%H:%M:%S',
        '%Y-%m-%dT%H:%M:%S%z',
        '%Y-%m-%d %H:%M:%S',
        '%Y-%m-%d',
        '%d %B %Y',
        '%B %d, %Y',
        '%d/%m/%Y',
        '%m/%d/%Y'
    ]
    
    for fmt in formats:
        try:
            dt = datetime.strptime(date_string.strip(), fmt)
            return dt.strftime('%Y-%m-%dT%H:%M:%S')
        except ValueError:
            continue
    
    # If no format works, try to extract just the year-month-day
    date_match = re.search(r'(\d{4})-(\d{1,2})-(\d{1,2})', date_string)
    if date_match:
        year, month, day = date_match.groups()
        return f"{year}-{month:0>2}-{day:0>2}T10:00:00"
    
    return ""

def update_hugo_post(slug, wp_data):
    """Update Hugo markdown file with WordPress data."""
    if not wp_data['success']:
        print(f"Skipping {slug} due to fetch error: {wp_data.get('error', 'Unknown error')}")
        return False
    
    hugo_file = Path(f"/home/idos/sc/startupcampus-blog/content/posts/{slug}.md")
    
    if not hugo_file.exists():
        print(f"Hugo file not found: {hugo_file}")
        return False
    
    # Read current Hugo file
    with open(hugo_file, 'r', encoding='utf-8') as f:
        current_content = f.read()
    
    # Extract current frontmatter and content
    parts = current_content.split('---', 2)
    if len(parts) < 3:
        print(f"Invalid frontmatter in {hugo_file}")
        return False
    
    metadata = wp_data['metadata']
    
    # Build new frontmatter
    frontmatter = ['---']
    
    # Title
    title = metadata.get('title', slug.replace('-', ' ').title())
    frontmatter.append(f'title: "{title}"')
    
    # Date
    date = parse_date(metadata.get('date', ''))
    if not date:
        # Keep existing date if we can't parse the new one
        existing_date = re.search(r'date:\s*([^\n]+)', parts[1])
        if existing_date:
            date = existing_date.group(1).strip()
        else:
            date = "2023-01-01T10:00:00"
    frontmatter.append(f'date: {date}')
    
    # Author
    author = metadata.get('author', '')
    if author:
        frontmatter.append(f'author: "{author}"')
    
    # Categories
    categories = metadata.get('categories', [])
    if categories:
        cat_str = ', '.join(f'"{cat}"' for cat in categories)
        frontmatter.append(f'categories: [{cat_str}]')
    
    # Tags
    tags = metadata.get('tags', [])
    if tags:
        tag_str = ', '.join(f'"{tag}"' for tag in tags)
        frontmatter.append(f'tags: [{tag_str}]')
    
    # Slug
    frontmatter.append(f'slug: "{slug}"')
    
    frontmatter.append('---')
    
    # Use existing content if available, otherwise convert from HTML
    post_content = parts[2].strip()
    if not post_content and wp_data.get('content'):
        post_content = html_to_markdown_basic(wp_data['content'])
    
    # Write updated file
    new_content = '\n'.join(frontmatter) + '\n\n' + post_content
    
    with open(hugo_file, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"✓ Updated {slug}")
    print(f"  Title: {title}")
    print(f"  Date: {date}")
    print(f"  Author: {author}")
    print(f"  Categories: {categories}")
    print(f"  Tags: {tags}")
    print()
    
    return True

def main():
    """Main function to sync all posts."""
    posts_dir = Path("/home/idos/sc/startupcampus-blog/content/posts")
    
    if not posts_dir.exists():
        print(f"Posts directory not found: {posts_dir}")
        return
    
    # Get all post slugs
    slugs = []
    for md_file in posts_dir.glob("*.md"):
        slugs.append(md_file.stem)
    
    print(f"Found {len(slugs)} posts to sync")
    
    successful = 0
    failed = 0
    
    for i, slug in enumerate(slugs, 1):
        print(f"[{i}/{len(slugs)}] Processing: {slug}")
        
        # Fetch WordPress data
        wp_data = fetch_wordpress_post(slug)
        
        # Update Hugo file
        if update_hugo_post(slug, wp_data):
            successful += 1
        else:
            failed += 1
        
        # Rate limiting - be nice to the server
        time.sleep(2)
    
    print(f"\nSync complete!")
    print(f"Successfully updated: {successful}")
    print(f"Failed: {failed}")

if __name__ == '__main__':
    main()