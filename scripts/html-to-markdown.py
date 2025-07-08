#!/usr/bin/env python3
"""
Convert HTML content in Hugo posts to proper markdown format.
"""

import os
import re
import glob
from pathlib import Path

def convert_html_to_markdown(content):
    """Convert HTML elements to markdown equivalents."""
    
    # Convert WordPress figure blocks to markdown images
    content = re.sub(
        r'<figure class="[^"]*"><img src="([^"]*)" alt="([^"]*)"[^>]*/?></figure>',
        r'![(\2)](\1)',
        content
    )
    
    # Convert simple img tags to markdown
    content = re.sub(
        r'<img[^>]*src="([^"]*)"[^>]*alt="([^"]*)"[^>]*/?>', 
        r'![(\2)](\1)',
        content
    )
    
    # Convert blockquotes
    content = re.sub(
        r'<blockquote[^>]*>(.*?)</blockquote>',
        lambda m: '\n> ' + m.group(1).strip().replace('\n', '\n> ') + '\n',
        content,
        flags=re.DOTALL
    )
    
    # Convert nested blockquotes
    content = re.sub(
        r'<blockquote[^>]*><blockquote[^>]*>(.*?)</blockquote></blockquote>',
        lambda m: '\n> > ' + m.group(1).strip().replace('\n', '\n> > ') + '\n',
        content,
        flags=re.DOTALL
    )
    
    # Convert headings
    content = re.sub(r'<h1[^>]*>(.*?)</h1>', r'# \1', content, flags=re.DOTALL)
    content = re.sub(r'<h2[^>]*>(.*?)</h2>', r'## \1', content, flags=re.DOTALL)
    content = re.sub(r'<h3[^>]*>(.*?)</h3>', r'### \1', content, flags=re.DOTALL)
    content = re.sub(r'<h4[^>]*>(.*?)</h4>', r'#### \1', content, flags=re.DOTALL)
    content = re.sub(r'<h5[^>]*>(.*?)</h5>', r'##### \1', content, flags=re.DOTALL)
    content = re.sub(r'<h6[^>]*>(.*?)</h6>', r'###### \1', content, flags=re.DOTALL)
    
    # Convert unordered lists
    content = re.sub(r'<ul[^>]*>', '', content)
    content = re.sub(r'</ul>', '', content)
    content = re.sub(r'<li[^>]*>(.*?)</li>', r'- \1', content, flags=re.DOTALL)
    
    # Convert ordered lists
    content = re.sub(r'<ol[^>]*>', '', content)
    content = re.sub(r'</ol>', '', content)
    
    # Convert ordered list items (this is more complex, need to track numbers)
    def convert_ol_items(text):
        lines = text.split('\n')
        result = []
        ol_counter = 1
        
        for line in lines:
            if '<li' in line and '</li>' in line:
                # Extract content between <li> tags
                li_content = re.sub(r'<li[^>]*>(.*?)</li>', r'\1', line, flags=re.DOTALL)
                result.append(f'{ol_counter}. {li_content.strip()}')
                ol_counter += 1
            else:
                result.append(line)
                if not line.strip():  # Reset counter on empty line
                    ol_counter = 1
        
        return '\n'.join(result)
    
    content = convert_ol_items(content)
    
    # Convert links
    content = re.sub(r'<a[^>]*href="([^"]*)"[^>]*>(.*?)</a>', r'[\2](\1)', content, flags=re.DOTALL)
    
    # Convert strong/bold
    content = re.sub(r'<strong[^>]*>(.*?)</strong>', r'**\1**', content, flags=re.DOTALL)
    content = re.sub(r'<b[^>]*>(.*?)</b>', r'**\1**', content, flags=re.DOTALL)
    
    # Convert emphasis/italic
    content = re.sub(r'<em[^>]*>(.*?)</em>', r'*\1*', content, flags=re.DOTALL)
    content = re.sub(r'<i[^>]*>(.*?)</i>', r'*\1*', content, flags=re.DOTALL)
    
    # Convert code
    content = re.sub(r'<code[^>]*>(.*?)</code>', r'`\1`', content, flags=re.DOTALL)
    
    # Convert paragraphs (remove p tags but keep content)
    content = re.sub(r'<p[^>]*>', '', content)
    content = re.sub(r'</p>', '\n\n', content)
    
    # Remove remaining HTML tags
    content = re.sub(r'<[^>]+>', '', content)
    
    # Clean up HTML entities
    content = content.replace('&nbsp;', ' ')
    content = content.replace('&amp;', '&')
    content = content.replace('&lt;', '<')
    content = content.replace('&gt;', '>')
    content = content.replace('&quot;', '"')
    content = content.replace('&#8220;', '"')
    content = content.replace('&#8221;', '"')
    content = content.replace('&#8217;', "'")
    content = content.replace('&#8211;', '–')
    content = content.replace('&#8212;', '—')
    
    # Clean up multiple empty lines
    content = re.sub(r'\n\s*\n\s*\n', '\n\n', content)
    
    # Clean up spaces
    content = re.sub(r'[ \t]+', ' ', content)
    
    return content.strip()

def process_post_file(filepath):
    """Process a single post file."""
    print(f"Processing {filepath}...")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Split frontmatter and content
    parts = content.split('---', 2)
    if len(parts) < 3:
        print(f"Warning: Could not parse frontmatter in {filepath}")
        return False
    
    frontmatter = parts[1]
    post_content = parts[2]
    
    # Convert HTML to markdown
    converted_content = convert_html_to_markdown(post_content)
    
    # Reconstruct the file
    new_content = f"---{frontmatter}---\n{converted_content}"
    
    # Write back to file
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"✓ Converted {filepath}")
    return True

def main():
    """Main function to process all posts."""
    posts_dir = Path(__file__).parent.parent / 'content' / 'posts'
    
    if not posts_dir.exists():
        print(f"Posts directory not found: {posts_dir}")
        return
    
    post_files = list(posts_dir.glob('*.md'))
    
    if not post_files:
        print("No markdown files found in posts directory")
        return
    
    print(f"Found {len(post_files)} posts to process")
    
    converted_count = 0
    for post_file in post_files:
        if process_post_file(post_file):
            converted_count += 1
    
    print(f"\nConversion complete! Processed {converted_count} posts.")

if __name__ == '__main__':
    main()