#!/usr/bin/env python3
"""
SEO Audit Script for Startup Campus Blog Posts
Analyzes all markdown files in content/posts directory for SEO optimization
"""

import os
import re
import yaml
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import json

def extract_frontmatter_and_content(file_path: str) -> Tuple[Dict, str]:
    """Extract YAML frontmatter and content from markdown file"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Split frontmatter and content
    if content.startswith('---'):
        parts = content.split('---', 2)
        if len(parts) >= 3:
            try:
                frontmatter = yaml.safe_load(parts[1])
                content = parts[2].strip()
                return frontmatter, content
            except yaml.YAMLError:
                pass
    
    return {}, content

def get_first_paragraph(content: str) -> str:
    """Extract first meaningful paragraph from content"""
    # Remove markdown links, images, and other formatting
    clean_content = re.sub(r'!\[.*?\]\(.*?\)', '', content)  # Remove images
    clean_content = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', clean_content)  # Remove links but keep text
    clean_content = re.sub(r'[#*_`]', '', clean_content)  # Remove markdown formatting
    clean_content = re.sub(r'>\s*', '', clean_content)  # Remove blockquotes
    
    # Split into paragraphs and find first substantial one
    paragraphs = [p.strip() for p in clean_content.split('\n\n') if p.strip()]
    
    for paragraph in paragraphs:
        if len(paragraph) > 50 and not paragraph.startswith('Baca juga'):
            return paragraph[:200] + ('...' if len(paragraph) > 200 else '')
    
    return paragraphs[0][:200] + ('...' if len(paragraphs[0]) > 200 else '') if paragraphs else ""

def analyze_title_length(title: str) -> str:
    """Categorize title length for SEO optimization"""
    length = len(title)
    if length < 30:
        return "too_short"
    elif length <= 60:
        return "optimal"
    else:
        return "too_long"

def identify_important_topics(title: str, content: str) -> List[str]:
    """Identify if post is about important topics"""
    important_keywords = {
        'certification': ['sertifikasi', 'bnsp', 'certification', 'certified'],
        'bootcamp': ['bootcamp', 'pelatihan', 'kursus', 'training'],
        'career': ['karir', 'career', 'kerja', 'pekerjaan', 'gaji', 'salary'],
        'skills': ['skill', 'keterampilan', 'kompeten'],
        'education': ['belajar', 'learn', 'pendidikan', 'education', 'studi'],
        'technology': ['ai', 'artificial intelligence', 'data science', 'ui/ux', 'programming'],
        'startup': ['startup', 'bisnis', 'business', 'entrepreneur']
    }
    
    text = (title + ' ' + content[:500]).lower()
    topics = []
    
    for topic, keywords in important_keywords.items():
        if any(keyword in text for keyword in keywords):
            topics.append(topic)
    
    return topics

def calculate_priority_score(title: str, content: str, topics: List[str]) -> int:
    """Calculate priority score for SEO attention (1-10, 10 being highest priority)"""
    score = 5  # Base score
    
    # High priority topics
    high_priority_topics = ['certification', 'bootcamp', 'career']
    score += sum(2 for topic in topics if topic in high_priority_topics)
    
    # Medium priority topics
    medium_priority_topics = ['skills', 'technology']
    score += sum(1 for topic in topics if topic in medium_priority_topics)
    
    # Title quality factors
    title_length = len(title)
    if title_length < 30 or title_length > 70:
        score += 2  # Needs attention
    
    # Content indicators
    if len(content) > 2000:
        score += 1  # Substantial content
    
    return min(score, 10)

def main():
    """Main function to perform SEO audit"""
    posts_dir = Path('/home/idos/sc/startupcampus-blog/content/posts')
    
    # Initialize results
    audit_results = {
        'total_posts': 0,
        'missing_description': 0,
        'missing_meta_title': 0,
        'missing_excerpt': 0,
        'missing_keywords': 0,
        'title_analysis': {'too_short': 0, 'optimal': 0, 'too_long': 0},
        'posts': []
    }
    
    print("🔍 Starting SEO Audit of Startup Campus Blog Posts...")
    print("=" * 60)
    
    # Process each markdown file
    for file_path in sorted(posts_dir.glob('*.md')):
        frontmatter, content = extract_frontmatter_and_content(file_path)
        
        if not frontmatter:
            continue
            
        title = frontmatter.get('title', '')
        if not title:
            continue
            
        # Analyze SEO elements
        has_description = bool(frontmatter.get('description'))
        has_meta_title = bool(frontmatter.get('meta_title'))
        has_excerpt = bool(frontmatter.get('excerpt'))
        has_keywords = bool(frontmatter.get('keywords') or frontmatter.get('tags'))
        
        title_category = analyze_title_length(title)
        first_paragraph = get_first_paragraph(content)
        topics = identify_important_topics(title, content)
        priority_score = calculate_priority_score(title, content, topics)
        
        # Compile post data
        post_data = {
            'filename': file_path.name,
            'title': title,
            'title_length': len(title),
            'title_category': title_category,
            'has_description': has_description,
            'has_meta_title': has_meta_title,
            'has_excerpt': has_excerpt,
            'has_keywords': has_keywords,
            'first_paragraph': first_paragraph,
            'topics': topics,
            'priority_score': priority_score,
            'author': frontmatter.get('author', ''),
            'date': str(frontmatter.get('date', '')),
            'slug': frontmatter.get('slug', ''),
            'content_length': len(content)
        }
        
        audit_results['posts'].append(post_data)
        
        # Update counters
        audit_results['total_posts'] += 1
        if not has_description:
            audit_results['missing_description'] += 1
        if not has_meta_title:
            audit_results['missing_meta_title'] += 1
        if not has_excerpt:
            audit_results['missing_excerpt'] += 1
        if not has_keywords:
            audit_results['missing_keywords'] += 1
        
        audit_results['title_analysis'][title_category] += 1
        
        print(f"✅ Processed: {file_path.name}")
    
    # Sort posts by priority score (highest first)
    audit_results['posts'].sort(key=lambda x: x['priority_score'], reverse=True)
    
    # Save results to JSON file
    with open('/home/idos/sc/startupcampus-blog/seo_audit_results.json', 'w', encoding='utf-8') as f:
        json.dump(audit_results, f, indent=2, ensure_ascii=False)
    
    print("\n" + "=" * 60)
    print("📊 SEO AUDIT SUMMARY")
    print("=" * 60)
    print(f"Total posts analyzed: {audit_results['total_posts']}")
    print(f"Posts missing description: {audit_results['missing_description']} ({audit_results['missing_description']/audit_results['total_posts']*100:.1f}%)")
    print(f"Posts missing meta_title: {audit_results['missing_meta_title']} ({audit_results['missing_meta_title']/audit_results['total_posts']*100:.1f}%)")
    print(f"Posts missing excerpt: {audit_results['missing_excerpt']} ({audit_results['missing_excerpt']/audit_results['total_posts']*100:.1f}%)")
    print(f"Posts missing keywords/tags: {audit_results['missing_keywords']} ({audit_results['missing_keywords']/audit_results['total_posts']*100:.1f}%)")
    
    print(f"\n📏 TITLE LENGTH ANALYSIS:")
    print(f"Too short (<30 chars): {audit_results['title_analysis']['too_short']}")
    print(f"Optimal (30-60 chars): {audit_results['title_analysis']['optimal']}")
    print(f"Too long (>60 chars): {audit_results['title_analysis']['too_long']}")
    
    print(f"\n🚨 TOP 15 PRIORITY POSTS NEEDING SEO ATTENTION:")
    print("-" * 60)
    for i, post in enumerate(audit_results['posts'][:15], 1):
        print(f"{i:2d}. {post['title'][:50]}{'...' if len(post['title']) > 50 else ''}")
        print(f"    Priority: {post['priority_score']}/10 | Length: {post['title_length']} chars | Topics: {', '.join(post['topics'])}")
        print(f"    Missing: {', '.join([field for field, has in [('desc', post['has_description']), ('meta', post['has_meta_title']), ('excerpt', post['has_excerpt']), ('keywords', post['has_keywords'])] if not has])}")
        print()
    
    print("✅ Full results saved to: seo_audit_results.json")

if __name__ == "__main__":
    main()