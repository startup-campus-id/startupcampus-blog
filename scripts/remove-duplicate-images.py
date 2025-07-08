#!/usr/bin/env python3
import os
import re

def remove_first_image_from_content(file_path):
    """Remove the first image from post content if it has a featured image"""
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    lines = content.split('\n')
    
    # Check if post has featured_image in frontmatter
    has_featured_image = False
    frontmatter_end = -1
    
    for i, line in enumerate(lines):
        if i > 0 and line.strip() == '---':
            frontmatter_end = i
            break
        if line.startswith('featured_image:'):
            has_featured_image = True
    
    if not has_featured_image:
        return False
    
    # Find and remove the first image in content (after frontmatter)
    content_lines = lines[frontmatter_end + 1:]
    
    # Remove first empty lines
    while content_lines and content_lines[0].strip() == '':
        content_lines.pop(0)
    
    # Check if first non-empty line is an image
    if content_lines and re.match(r'!\[.*?\]\(.*?\)', content_lines[0].strip()):
        content_lines.pop(0)
        
        # Remove following empty line if exists
        if content_lines and content_lines[0].strip() == '':
            content_lines.pop(0)
        
        # Reconstruct the file
        new_content = '\n'.join(lines[:frontmatter_end + 1]) + '\n\n' + '\n'.join(content_lines)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        return True
    
    return False

def main():
    """Remove duplicate images from all posts that have featured images"""
    posts_dir = "/home/idos/sc/startupcampus-blog/content/posts"
    
    fixed_count = 0
    
    for filename in os.listdir(posts_dir):
        if filename.endswith('.md'):
            file_path = os.path.join(posts_dir, filename)
            if remove_first_image_from_content(file_path):
                print(f"Fixed: {filename}")
                fixed_count += 1
    
    print(f"\nFixed {fixed_count} posts with duplicate images")

if __name__ == "__main__":
    main()