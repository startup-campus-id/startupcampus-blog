#!/usr/bin/env python3
import os
import re
import html
from datetime import datetime
import xml.etree.ElementTree as ET
from html.parser import HTMLParser

class MLStripper(HTMLParser):
    def __init__(self):
        super().__init__()
        self.reset()
        self.strict = False
        self.convert_charrefs = True
        self.text = []
    def handle_data(self, d):
        self.text.append(d)
    def get_data(self):
        return ''.join(self.text)

def strip_html_tags(html_content):
    """Remove HTML tags from content"""
    s = MLStripper()
    s.feed(html_content)
    return s.get_data()

def clean_xml_content(file_path):
    """Clean XML file to fix common issues"""
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    # Fix common XML issues
    content = re.sub(r'&(?!amp;|lt;|gt;|quot;|apos;)', '&amp;', content)
    content = re.sub(r'<!\[CDATA\[(.*?)\]\]>', lambda m: '<![CDATA[' + m.group(1).replace(']]>', ']]&gt;') + ']]>', content, flags=re.DOTALL)
    
    # Save cleaned content
    cleaned_path = file_path + '.cleaned'
    with open(cleaned_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return cleaned_path

def clean_content(content):
    """Clean WordPress content for Hugo"""
    if not content:
        return ""
    
    # Decode HTML entities
    content = html.unescape(content)
    
    # Convert WordPress shortcodes to Hugo shortcodes or remove them
    content = re.sub(r'\[caption[^\]]*\](.*?)\[/caption\]', r'{{< figure src="\1" >}}', content)
    content = re.sub(r'\[gallery[^\]]*\]', '', content)
    content = re.sub(r'\[embed\](.*?)\[/embed\]', r'\1', content)
    
    # Fix image paths
    content = re.sub(r'https://startupcampus\.id/blog/wp-content/uploads/', '/uploads/', content)
    content = re.sub(r'https://www\.startupcampus\.id/blog/wp-content/uploads/', '/uploads/', content)
    
    # Convert WordPress blocks to markdown
    content = re.sub(r'<!-- wp:paragraph -->\s*<p>(.*?)</p>\s*<!-- /wp:paragraph -->', r'\1\n\n', content, flags=re.DOTALL)
    content = re.sub(r'<!-- wp:heading[^>]*-->\s*<h(\d)>(.*?)</h\d>\s*<!-- /wp:heading -->', lambda m: '#' * int(m.group(1)) + ' ' + m.group(2) + '\n\n', content, flags=re.DOTALL)
    content = re.sub(r'<!-- wp:list -->\s*(.*?)\s*<!-- /wp:list -->', r'\1\n', content, flags=re.DOTALL)
    content = re.sub(r'<!-- wp:image[^>]*-->\s*(.*?)\s*<!-- /wp:image -->', r'\1\n', content, flags=re.DOTALL)
    
    # Remove remaining WordPress comments
    content = re.sub(r'<!-- wp:.*?-->', '', content)
    content = re.sub(r'<!-- /wp:.*?-->', '', content)
    
    return content.strip()

def slugify(text):
    """Create URL-friendly slug"""
    if not text:
        return "untitled"
    text = re.sub(r'[^\w\s-]', '', text.lower())
    return re.sub(r'[-\s]+', '-', text).strip('-')

def parse_wordpress_xml(xml_file):
    """Parse WordPress export XML and convert to Hugo posts"""
    # Clean XML first
    print(f"Cleaning XML file...")
    cleaned_xml = clean_xml_content(xml_file)
    
    try:
        tree = ET.parse(cleaned_xml)
    except ET.ParseError as e:
        print(f"XML Parse Error: {e}")
        print("Attempting to parse with recovery mode...")
        # Try parsing with iterparse for large files
        return parse_wordpress_xml_iterative(cleaned_xml)
    
    root = tree.getroot()
    
    # Namespaces
    namespaces = {
        'wp': 'http://wordpress.org/export/1.2/',
        'content': 'http://purl.org/rss/1.0/modules/content/',
        'dc': 'http://purl.org/dc/elements/1.1/'
    }
    
    posts_created = 0
    pages_created = 0
    errors = []
    
    # Process all items
    for item in root.findall('.//item'):
        try:
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
            if post_date is not None and post_date.text:
                try:
                    dt = datetime.strptime(post_date.text, '%Y-%m-%d %H:%M:%S')
                    date = dt.isoformat()
                except:
                    date = datetime.now().isoformat()
            else:
                date = datetime.now().isoformat()
            
            # Get categories
            categories = []
            for category in item.findall('.//category[@domain="category"]'):
                if category.text and category.get('nicename'):
                    categories.append(category.get('nicename'))
            
            # Get tags
            tags = []
            for tag in item.findall('.//category[@domain="post_tag"]'):
                if tag.text and tag.get('nicename'):
                    tags.append(tag.get('nicename'))
            
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
            
        except Exception as e:
            error_msg = f"Error processing item: {str(e)}"
            print(error_msg)
            errors.append(error_msg)
            continue
    
    # Clean up temporary file
    os.remove(cleaned_xml)
    
    print(f"\n✅ Import complete!")
    print(f"📝 Posts created: {posts_created}")
    print(f"📄 Pages created: {pages_created}")
    if errors:
        print(f"⚠️  Errors encountered: {len(errors)}")

def parse_wordpress_xml_iterative(xml_file):
    """Parse WordPress XML using iterative parsing for large/problematic files"""
    posts_created = 0
    pages_created = 0
    
    # Namespaces
    ns = {
        'wp': 'http://wordpress.org/export/1.2/',
        'content': 'http://purl.org/rss/1.0/modules/content/',
        'dc': 'http://purl.org/dc/elements/1.1/'
    }
    
    context = ET.iterparse(xml_file, events=('start', 'end'))
    context = iter(context)
    event, root = next(context)
    
    for event, elem in context:
        if event == 'end' and elem.tag == 'item':
            try:
                # Process item
                post_type = elem.find('.//wp:post_type', ns)
                status = elem.find('.//wp:status', ns)
                
                if post_type is not None and status is not None and status.text == 'publish':
                    title = elem.find('title').text or 'Untitled'
                    content_elem = elem.find('.//content:encoded', ns)
                    content = clean_content(content_elem.text if content_elem is not None else '')
                    
                    post_name = elem.find('.//wp:post_name', ns)
                    slug = post_name.text if post_name is not None and post_name.text else slugify(title)
                    
                    if post_type.text == 'post':
                        output_dir = 'content/posts'
                        posts_created += 1
                    elif post_type.text == 'page':
                        output_dir = 'content/pages'
                        pages_created += 1
                    else:
                        continue
                    
                    os.makedirs(output_dir, exist_ok=True)
                    filepath = os.path.join(output_dir, f"{slug}.md")
                    
                    # Create simple frontmatter
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(f'---\ntitle: "{title}"\ndate: {datetime.now().isoformat()}\nslug: "{slug}"\n---\n\n')
                        f.write(content)
                    
                    print(f"Created: {filepath}")
                
            except Exception as e:
                print(f"Error processing item: {e}")
            
            # Clear the element to save memory
            elem.clear()
            root.clear()
    
    print(f"\n✅ Iterative import complete!")
    print(f"📝 Posts created: {posts_created}")
    print(f"📄 Pages created: {pages_created}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python import-wordpress-safe.py wordpress-export.xml")
        sys.exit(1)
    
    parse_wordpress_xml(sys.argv[1])