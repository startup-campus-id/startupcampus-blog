#!/usr/bin/env python3
import os
import re
import requests
import json

def check_post_images():
    """Check which posts have featured images and list missing ones"""
    posts_dir = "/home/idos/sc/startupcampus-blog/content/posts"
    
    posts_with_featured = []
    posts_without_featured = []
    posts_with_content_images = []
    
    for filename in os.listdir(posts_dir):
        if filename.endswith('.md'):
            file_path = os.path.join(posts_dir, filename)
            
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            lines = content.split('\n')
            slug = filename.replace('.md', '')
            title = ""
            has_featured_image = False
            has_content_images = False
            
            # Parse frontmatter
            in_frontmatter = False
            for line in lines:
                if line.strip() == '---':
                    if not in_frontmatter:
                        in_frontmatter = True
                    else:
                        break
                elif in_frontmatter:
                    if line.startswith('title:'):
                        title = line.split(':', 1)[1].strip().strip('"')
                    elif line.startswith('featured_image:'):
                        has_featured_image = True
            
            # Check for images in content
            if re.search(r'!\[.*?\]\(.*?\)', content):
                has_content_images = True
            
            post_info = {
                'slug': slug,
                'title': title,
                'filename': filename,
                'has_featured': has_featured_image,
                'has_content_images': has_content_images
            }
            
            if has_featured_image:
                posts_with_featured.append(post_info)
            else:
                posts_without_featured.append(post_info)
            
            if has_content_images:
                posts_with_content_images.append(post_info)
    
    return posts_with_featured, posts_without_featured, posts_with_content_images

def fetch_wordpress_post_image(slug):
    """Fetch image from WordPress for a specific post"""
    try:
        url = f"https://www.startupcampus.id/blog/wp-json/wp/v2/posts"
        params = {"slug": slug}
        
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            posts = response.json()
            if posts:
                post = posts[0]
                content = post['content']['rendered']
                
                # Find first image
                img_patterns = [
                    r'<img[^>]*src=["\']([^"\']+)["\'][^>]*>',
                    r'!\[.*?\]\(([^)]+)\)'
                ]
                
                for pattern in img_patterns:
                    matches = re.findall(pattern, content, re.IGNORECASE)
                    if matches:
                        return matches[0]
        
        return None
    except Exception as e:
        return f"Error: {e}"

def main():
    print("Checking image status for all posts...")
    
    posts_with_featured, posts_without_featured, posts_with_content_images = check_post_images()
    
    # Write summary report
    with open('/home/idos/sc/startupcampus-blog/IMAGE_STATUS_REPORT.md', 'w', encoding='utf-8') as f:
        f.write("# Image Status Report\n\n")
        f.write(f"Generated on: {os.popen('date').read().strip()}\n\n")
        
        f.write(f"## Summary\n")
        f.write(f"- Total posts: {len(posts_with_featured) + len(posts_without_featured)}\n")
        f.write(f"- Posts with featured images: {len(posts_with_featured)}\n")
        f.write(f"- Posts without featured images: {len(posts_without_featured)}\n")
        f.write(f"- Posts with content images: {len(posts_with_content_images)}\n\n")
        
        f.write("## Posts WITH Featured Images\n\n")
        for post in posts_with_featured:
            f.write(f"✅ **{post['title']}**\n")
            f.write(f"   - Slug: `{post['slug']}`\n")
            f.write(f"   - URL: https://localhost:1313/{post['slug']}/\n")
            f.write(f"   - WordPress: https://www.startupcampus.id/blog/{post['slug']}/\n\n")
        
        f.write("## Posts WITHOUT Featured Images (Need Manual Check)\n\n")
        for post in posts_without_featured:
            f.write(f"❌ **{post['title']}**\n")
            f.write(f"   - Slug: `{post['slug']}`\n")
            f.write(f"   - URL: https://localhost:1313/{post['slug']}/\n")
            f.write(f"   - WordPress: https://www.startupcampus.id/blog/{post['slug']}/\n")
            f.write(f"   - Has content images: {'Yes' if post['has_content_images'] else 'No'}\n\n")
    
    # Create a specific file with URLs for manual checking
    with open('/home/idos/sc/startupcampus-blog/POSTS_TO_CHECK.txt', 'w', encoding='utf-8') as f:
        f.write("# Posts without featured images - WordPress URLs for manual checking\n\n")
        for post in posts_without_featured:
            f.write(f"https://www.startupcampus.id/blog/{post['slug']}/\n")
    
    # Check the specific post mentioned
    print("Checking specific post: volunteer-vibes-edisi-siaran-crast-1078-fm-x-aiesec-in-upnvy")
    img_url = fetch_wordpress_post_image("volunteer-vibes-edisi-siaran-crast-1078-fm-x-aiesec-in-upnvy")
    print(f"Image found: {img_url}")
    
    print(f"\n📊 SUMMARY:")
    print(f"- Total posts: {len(posts_with_featured) + len(posts_without_featured)}")
    print(f"- With featured images: {len(posts_with_featured)}")
    print(f"- Without featured images: {len(posts_without_featured)}")
    print(f"- With content images: {len(posts_with_content_images)}")
    
    print(f"\n📄 Reports generated:")
    print(f"- IMAGE_STATUS_REPORT.md (detailed report)")
    print(f"- POSTS_TO_CHECK.txt (URLs for manual checking)")

if __name__ == "__main__":
    main()