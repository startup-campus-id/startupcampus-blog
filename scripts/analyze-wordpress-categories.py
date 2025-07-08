#!/usr/bin/env python3
"""
WordPress Category Analysis Script
Fetches all posts from WordPress REST API and analyzes categories
"""

import requests
import json
import time
import os
from typing import Dict, List, Set, Tuple
from collections import defaultdict, Counter
import re

class WordPressAnalyzer:
    def __init__(self, base_url: str = "https://www.startupcampus.id/blog/wp-json/wp/v2"):
        self.base_url = base_url
        self.posts = []
        self.categories = {}
        self.category_mapping = {}
        
    def fetch_categories(self) -> Dict[int, str]:
        """Fetch all categories from WordPress"""
        print("Fetching categories from WordPress...")
        categories = {}
        page = 1
        
        while True:
            url = f"{self.base_url}/categories"
            params = {
                'page': page,
                'per_page': 100,
                '_fields': 'id,name,slug,count'
            }
            
            try:
                response = requests.get(url, params=params, timeout=30)
                response.raise_for_status()
                
                page_categories = response.json()
                if not page_categories:
                    break
                    
                for cat in page_categories:
                    categories[cat['id']] = {
                        'name': cat['name'],
                        'slug': cat['slug'],
                        'count': cat['count']
                    }
                    
                print(f"  Fetched {len(page_categories)} categories from page {page}")
                page += 1
                
            except requests.exceptions.RequestException as e:
                print(f"Error fetching categories page {page}: {e}")
                break
                
        print(f"Total categories fetched: {len(categories)}")
        return categories
    
    def fetch_posts_with_categories(self) -> List[Dict]:
        """Fetch all posts with their categories from WordPress"""
        print("Fetching posts from WordPress...")
        posts = []
        page = 1
        
        while True:
            url = f"{self.base_url}/posts"
            params = {
                'page': page,
                'per_page': 100,
                '_fields': 'id,title,slug,categories,date,link,status',
                'status': 'publish'
            }
            
            try:
                response = requests.get(url, params=params, timeout=30)
                response.raise_for_status()
                
                page_posts = response.json()
                if not page_posts:
                    break
                    
                posts.extend(page_posts)
                print(f"  Fetched {len(page_posts)} posts from page {page}")
                page += 1
                
                # Rate limiting
                time.sleep(0.5)
                
            except requests.exceptions.RequestException as e:
                print(f"Error fetching posts page {page}: {e}")
                break
                
        print(f"Total posts fetched: {len(posts)}")
        return posts
    
    def analyze_hugo_categories(self) -> Dict[str, List[str]]:
        """Analyze current Hugo post categories"""
        print("Analyzing Hugo categories...")
        hugo_categories = {}
        posts_dir = "content/posts"
        
        if not os.path.exists(posts_dir):
            print(f"Hugo posts directory not found: {posts_dir}")
            return {}
            
        for filename in os.listdir(posts_dir):
            if filename.endswith('.md'):
                filepath = os.path.join(posts_dir, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                        
                    # Extract categories from frontmatter
                    match = re.search(r'categories:\s*\[(.*?)\]', content, re.DOTALL)
                    if match:
                        categories_str = match.group(1)
                        # Parse categories - handle quoted strings
                        categories = []
                        for cat in categories_str.split(','):
                            cat = cat.strip().strip('"').strip("'")
                            if cat:
                                categories.append(cat)
                        
                        slug = filename.replace('.md', '')
                        hugo_categories[slug] = categories
                        
                except Exception as e:
                    print(f"Error reading {filename}: {e}")
                    
        print(f"Analyzed {len(hugo_categories)} Hugo posts")
        return hugo_categories
    
    def create_category_mapping(self) -> Dict[str, str]:
        """Create mapping between WordPress and Hugo categories"""
        print("Creating category mapping...")
        
        # Common mappings based on typical WordPress to Hugo conversions
        mapping = {
            'Digital': 'Digital',
            'Alumni': 'Alumni', 
            'Semua': 'Semua',
            'Update': 'Update',
            'Pengajar': 'Pengajar',
            'Uncategorized': 'Semua',
            'General': 'Semua',
            'Blog': 'Semua',
            'News': 'Update',
            'Articles': 'Digital',
            'Technology': 'Digital',
            'Education': 'Digital',
            'Career': 'Digital',
            'Business': 'Digital',
            'Startup': 'Digital',
            'AI': 'Digital',
            'Data Science': 'Digital',
            'Programming': 'Digital',
            'Design': 'Digital',
            'Marketing': 'Digital'
        }
        
        return mapping
    
    def compare_categories(self) -> Dict:
        """Compare WordPress and Hugo categories"""
        print("Comparing WordPress and Hugo categories...")
        
        # Get WordPress categories for each post
        wp_post_categories = {}
        for post in self.posts:
            slug = post['slug']
            categories = []
            for cat_id in post['categories']:
                if cat_id in self.categories:
                    categories.append(self.categories[cat_id]['name'])
            wp_post_categories[slug] = categories
        
        # Get Hugo categories
        hugo_categories = self.analyze_hugo_categories()
        
        # Compare
        discrepancies = []
        wp_category_distribution = Counter()
        hugo_category_distribution = Counter()
        
        for slug in wp_post_categories:
            wp_cats = wp_post_categories[slug]
            hugo_cats = hugo_categories.get(slug, [])
            
            # Count distributions
            for cat in wp_cats:
                wp_category_distribution[cat] += 1
            for cat in hugo_cats:
                hugo_category_distribution[cat] += 1
            
            # Check for discrepancies
            wp_cats_set = set(wp_cats)
            hugo_cats_set = set(hugo_cats)
            
            if wp_cats_set != hugo_cats_set:
                discrepancies.append({
                    'slug': slug,
                    'wordpress_categories': wp_cats,
                    'hugo_categories': hugo_cats,
                    'missing_in_hugo': list(wp_cats_set - hugo_cats_set),
                    'extra_in_hugo': list(hugo_cats_set - wp_cats_set)
                })
        
        return {
            'discrepancies': discrepancies,
            'wp_distribution': dict(wp_category_distribution),
            'hugo_distribution': dict(hugo_category_distribution),
            'total_wp_posts': len(wp_post_categories),
            'total_hugo_posts': len(hugo_categories)
        }
    
    def generate_correction_mapping(self, comparison_results: Dict) -> Dict[str, List[str]]:
        """Generate mapping file to correct categories"""
        print("Generating correction mapping...")
        
        corrections = {}
        category_mapping = self.create_category_mapping()
        
        for discrepancy in comparison_results['discrepancies']:
            slug = discrepancy['slug']
            wp_cats = discrepancy['wordpress_categories']
            
            # Map WordPress categories to Hugo categories
            mapped_cats = []
            for wp_cat in wp_cats:
                if wp_cat in category_mapping:
                    mapped_cat = category_mapping[wp_cat]
                    if mapped_cat not in mapped_cats:
                        mapped_cats.append(mapped_cat)
                else:
                    # If no mapping found, try to map to Digital or Semua
                    if any(keyword in wp_cat.lower() for keyword in ['tech', 'ai', 'data', 'digital', 'programming', 'design']):
                        if 'Digital' not in mapped_cats:
                            mapped_cats.append('Digital')
                    else:
                        if 'Semua' not in mapped_cats:
                            mapped_cats.append('Semua')
            
            # Ensure at least one category
            if not mapped_cats:
                mapped_cats = ['Semua']
            
            corrections[slug] = mapped_cats
        
        return corrections
    
    def save_results(self, comparison_results: Dict, corrections: Dict):
        """Save analysis results to files"""
        print("Saving results...")
        
        # Save detailed analysis
        analysis_file = 'wordpress_category_analysis.json'
        with open(analysis_file, 'w', encoding='utf-8') as f:
            json.dump({
                'wordpress_categories': self.categories,
                'comparison_results': comparison_results,
                'corrections': corrections,
                'analysis_date': time.strftime('%Y-%m-%d %H:%M:%S')
            }, f, indent=2, ensure_ascii=False)
        
        # Save human-readable report
        report_file = 'category_analysis_report.txt'
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("WordPress vs Hugo Category Analysis Report\n")
            f.write("=" * 50 + "\n\n")
            
            f.write(f"Analysis Date: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            f.write("CATEGORY DISTRIBUTION COMPARISON\n")
            f.write("-" * 30 + "\n")
            f.write(f"Total WordPress Posts: {comparison_results['total_wp_posts']}\n")
            f.write(f"Total Hugo Posts: {comparison_results['total_hugo_posts']}\n\n")
            
            f.write("WordPress Category Distribution:\n")
            for cat, count in sorted(comparison_results['wp_distribution'].items(), key=lambda x: x[1], reverse=True):
                f.write(f"  {cat}: {count} posts\n")
            
            f.write("\nHugo Category Distribution:\n")
            for cat, count in sorted(comparison_results['hugo_distribution'].items(), key=lambda x: x[1], reverse=True):
                f.write(f"  {cat}: {count} posts\n")
            
            f.write(f"\nDISCREPANCIES FOUND\n")
            f.write("-" * 20 + "\n")
            f.write(f"Posts with category mismatches: {len(comparison_results['discrepancies'])}\n\n")
            
            for i, disc in enumerate(comparison_results['discrepancies'][:20]):  # Show first 20
                f.write(f"{i+1}. {disc['slug']}\n")
                f.write(f"   WordPress: {disc['wordpress_categories']}\n")
                f.write(f"   Hugo: {disc['hugo_categories']}\n")
                if disc['missing_in_hugo']:
                    f.write(f"   Missing in Hugo: {disc['missing_in_hugo']}\n")
                if disc['extra_in_hugo']:
                    f.write(f"   Extra in Hugo: {disc['extra_in_hugo']}\n")
                f.write("\n")
            
            if len(comparison_results['discrepancies']) > 20:
                f.write(f"... and {len(comparison_results['discrepancies']) - 20} more discrepancies\n")
        
        # Save corrections mapping
        corrections_file = 'category_corrections.json'
        with open(corrections_file, 'w', encoding='utf-8') as f:
            json.dump(corrections, f, indent=2, ensure_ascii=False)
        
        print(f"Results saved to:")
        print(f"  - {analysis_file}")
        print(f"  - {report_file}")
        print(f"  - {corrections_file}")
    
    def run_analysis(self):
        """Run the complete analysis"""
        print("Starting WordPress Category Analysis...")
        print("=" * 50)
        
        # Fetch data
        self.categories = self.fetch_categories()
        self.posts = self.fetch_posts_with_categories()
        
        # Analyze
        comparison_results = self.compare_categories()
        corrections = self.generate_correction_mapping(comparison_results)
        
        # Save results
        self.save_results(comparison_results, corrections)
        
        print("\nAnalysis complete!")
        print(f"Found {len(comparison_results['discrepancies'])} posts with category discrepancies")
        print(f"Generated corrections for {len(corrections)} posts")

if __name__ == "__main__":
    analyzer = WordPressAnalyzer()
    analyzer.run_analysis()