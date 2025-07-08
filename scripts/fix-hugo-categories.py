#!/usr/bin/env python3
"""
Fix Hugo Categories Script
Applies the correct categories from WordPress to Hugo posts
"""

import json
import os
import re
from typing import Dict, List

def load_corrections() -> Dict[str, List[str]]:
    """Load the category corrections from JSON file"""
    with open('category_corrections.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def update_post_categories(post_path: str, new_categories: List[str]) -> bool:
    """Update categories in a Hugo post file"""
    try:
        with open(post_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Format categories for Hugo frontmatter
        categories_str = json.dumps(new_categories)
        
        # Replace the categories line
        pattern = r'categories:\s*\[.*?\]'
        replacement = f'categories: {categories_str}'
        
        updated_content = re.sub(pattern, replacement, content, flags=re.MULTILINE | re.DOTALL)
        
        # Check if replacement was made
        if updated_content == content:
            print(f"Warning: No categories found to replace in {post_path}")
            return False
        
        # Write the updated content back
        with open(post_path, 'w', encoding='utf-8') as f:
            f.write(updated_content)
        
        return True
        
    except Exception as e:
        print(f"Error updating {post_path}: {e}")
        return False

def main():
    """Main function to fix all Hugo categories"""
    print("Loading category corrections...")
    corrections = load_corrections()
    
    posts_dir = "content/posts"
    if not os.path.exists(posts_dir):
        print(f"Posts directory not found: {posts_dir}")
        return
    
    successful_updates = 0
    failed_updates = 0
    
    print(f"Applying corrections to {len(corrections)} posts...")
    
    for slug, new_categories in corrections.items():
        post_path = os.path.join(posts_dir, f"{slug}.md")
        
        if os.path.exists(post_path):
            print(f"Updating {slug}...")
            print(f"  New categories: {new_categories}")
            
            if update_post_categories(post_path, new_categories):
                successful_updates += 1
                print(f"  ✓ Successfully updated")
            else:
                failed_updates += 1
                print(f"  ✗ Failed to update")
        else:
            print(f"Warning: Post file not found: {post_path}")
            failed_updates += 1
    
    print(f"\nUpdate Summary:")
    print(f"  Successfully updated: {successful_updates} posts")
    print(f"  Failed updates: {failed_updates} posts")
    print(f"  Total corrections applied: {successful_updates}")

if __name__ == "__main__":
    main()