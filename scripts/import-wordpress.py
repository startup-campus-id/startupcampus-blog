#!/usr/bin/env python3
import xml.etree.ElementTree as ET
import os
import re
import html
from datetime import datetime
from urllib.parse import urlparse

def clean_content(content):
    """Clean WordPress content for Hugo"""
    if not content:
        return ""
    
    # Decode HTML entities
    content = html.unescape(content)
    
    # Convert WordPress shortcodes to Hugo shortcodes
    content = re.sub(r'\[caption[^\]]*\](.*?)\[/caption\]', r'{{< figure src="\1" >}}', content)
    
    # Fix image paths
    content = re.sub(r'https://startupcampus\.id/blog/wp-content/uploads/', '/uploads/', content)
    
    return content

def slugify(text):
    """Create URL-friendly slug"""
    if not text:
        return "untitled"
    text = re.sub(r'[^\w\s-]', '', text.lower())
    return re.sub(r'[-\s]+', '-', text).strip('-')

def parse_wordpress_xml(xml_file):
    """Parse WordPress export XML and convert to Hugo posts"""
    tree = ET.parse(xml_file)
    root = tree.getroot()
    
    # Namespaces
    namespaces = {
        'wp': 'http://wordpress.org/export/1.2/',
        'content': 'http://purl.org/rss/1.0/modules/content/',
        'dc': 'http://purl.org/dc/elements/1.1/'
    }
    
    posts_created = 0
    pages_created = 0
    
    # Process all items
    for item in root.findall('.//item'):
        post_type = item.find('.//wp:post_type', namespaces)
        status = item.find('.//wp:status', namespaces)
        
        if post_type is None or status is None:
            continue
            
        if status.text != 'publish':
            continue
        
        # Extract post data
        title = item.find('title').text or 'Untitled'
        content_elem = item.find('.//content:encoded', namespaces)
        content = clean_content(content_elem.text if content_elem is not None else '')
        
        post_name = item.find('.//wp:post_name', namespaces)
        slug = post_name.text if post_name is not None and post_name.text else slugify(title)
        
        post_date = item.find('.//wp:post_date', namespaces)
        date = post_date.text if post_date is not None else datetime.now().isoformat()
        
        # Get categories
        categories = []
        for category in item.findall('.//category[@domain="category"]'):
            if category.text:
                categories.append(category.text)
        
        # Get tags
        tags = []
        for tag in item.findall('.//category[@domain="post_tag"]'):
            if tag.text:
                tags.append(tag.text)
        
        # Create Hugo front matter
        escaped_title = title.replace('"', '\\"')
        front_matter = f"""---
title: "{escaped_title}"
date: {date}
slug: "{slug}"
categories: {categories}
tags: {tags}
draft: false
---

"""
        
        # Determine output path
        if post_type.text == 'post':
            output_dir = 'content/posts'
            posts_created += 1
        elif post_type.text == 'page':
            output_dir = 'content/pages'
            pages_created += 1
        else:
            continue
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Write file
        filename = f"{slug}.md"
        filepath = os.path.join(output_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(front_matter)
            f.write(content)
        
        print(f"Created: {filepath}")
    
    print(f"\n✅ Import complete!")
    print(f"📝 Posts created: {posts_created}")
    print(f"📄 Pages created: {pages_created}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python import-wordpress.py wordpress-export.xml")
        sys.exit(1)
    
    parse_wordpress_xml(sys.argv[1])