#!/usr/bin/env python3
"""
SEO Implementation Helper - Add meta descriptions and other SEO fields to blog posts
"""

import json
import yaml
import re
from pathlib import Path

def generate_meta_description(title: str, first_paragraph: str, topics: list) -> str:
    """Generate optimized meta description"""
    clean_paragraph = first_paragraph.replace('\n', ' ').strip()
    
    if 'certification' in topics:
        if 'bnsp' in title.lower():
            return f"Pelajari cara mendapatkan sertifikasi BNSP untuk meningkatkan karir. {clean_paragraph[:85]}... Panduan lengkap di Startup Campus!"
        else:
            return f"Tingkatkan kredibilitas profesional dengan sertifikasi yang tepat. {clean_paragraph[:70]}... Mulai perjalanan karir impian!"
    
    elif 'bootcamp' in topics:
        return f"Temukan bootcamp terbaik untuk mengembangkan skill digital. {clean_paragraph[:70]}... Siap kerja dalam hitungan bulan!"
    
    elif 'career' in topics:
        if 'gaji' in title.lower():
            return f"Ketahui peluang karir dan gaji di bidang teknologi. {clean_paragraph[:70]}... Raih penghasilan impian!"
        else:
            return f"Panduan karir lengkap untuk mencapai kesuksesan profesional. {clean_paragraph[:60]}... Tips praktis yang terbukti efektif!"
    
    elif 'technology' in topics:
        if 'ai' in title.lower():
            return f"Pelajari teknologi AI terbaru dan penerapannya. {clean_paragraph[:70]}... Jadilah ahli di era digital!"
        else:
            return f"Kuasai teknologi terkini untuk kemajuan karir. {clean_paragraph[:70]}... Solusi praktis dan mudah dipahami!"
    
    elif 'startup' in topics:
        return f"Panduan membangun startup dan bisnis yang sukses. {clean_paragraph[:70]}... Tips dari para ahli dan praktisi!"
    
    else:
        return f"{clean_paragraph[:110]}... Pelajari lebih lanjut di Startup Campus untuk mengembangkan skill dan karir impian!"

def generate_keywords(title: str, topics: list) -> list:
    """Generate relevant keywords"""
    keywords = []
    
    # Extract important words from title
    title_words = [word.lower() for word in re.findall(r'\b\w+\b', title)]
    important_words = [word for word in title_words if len(word) > 3 and word not in 
                      ['yang', 'untuk', 'dengan', 'dalam', 'dari', 'atau', 'adalah', 'akan', 'dapat', 'bisa']]
    keywords.extend(important_words[:4])
    
    # Add topic-specific keywords
    topic_keywords = {
        'certification': ['sertifikasi', 'bnsp', 'kompetensi'],
        'bootcamp': ['bootcamp', 'pelatihan', 'kursus'],
        'career': ['karir', 'pekerjaan', 'kerja'],
        'technology': ['teknologi', 'digital', 'ai'],
        'startup': ['startup', 'bisnis']
    }
    
    for topic in topics:
        if topic in topic_keywords:
            keywords.extend(topic_keywords[topic][:2])
    
    # Add general keywords
    keywords.extend(['startup campus', 'indonesia'])
    
    return list(set(keywords))[:8]

def add_seo_fields_to_post(file_path: str, meta_description: str, keywords: list, meta_title: str) -> bool:
    """Add SEO fields to a specific post"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if not content.startswith('---'):
            print(f"❌ No frontmatter found in {file_path}")
            return False
        
        # Split frontmatter and content
        parts = content.split('---', 2)
        if len(parts) < 3:
            print(f"❌ Invalid frontmatter format in {file_path}")
            return False
        
        frontmatter = yaml.safe_load(parts[1])
        post_content = parts[2]
        
        # Add SEO fields
        frontmatter['description'] = meta_description
        frontmatter['meta_title'] = meta_title
        frontmatter['excerpt'] = meta_description[:100] + "..."
        frontmatter['keywords'] = keywords
        
        # Rebuild file content
        new_content = "---\n" + yaml.dump(frontmatter, default_flow_style=False, allow_unicode=True) + "---" + post_content
        
        # Write back to file (commented out for safety - uncomment when ready to implement)
        # with open(file_path, 'w', encoding='utf-8') as f:
        #     f.write(new_content)
        
        return True
        
    except Exception as e:
        print(f"❌ Error processing {file_path}: {str(e)}")
        return False

def generate_implementation_plan():
    """Generate implementation plan for top priority posts"""
    
    # Load audit results
    with open('/home/idos/sc/startupcampus-blog/seo_audit_results.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Create implementation plan for top 20 posts
    implementation_plan = []
    
    print("🚀 SEO IMPLEMENTATION PLAN - TOP 20 PRIORITY POSTS")
    print("=" * 70)
    print()
    
    for i, post in enumerate(data['posts'][:20], 1):
        title = post['title']
        filename = post['filename']
        topics = post['topics']
        first_paragraph = post['first_paragraph']
        
        # Generate SEO elements
        meta_description = generate_meta_description(title, first_paragraph, topics)
        keywords = generate_keywords(title, topics)
        meta_title = f"{title} | Startup Campus"
        
        # Ensure meta description is within limits
        if len(meta_description) > 160:
            meta_description = meta_description[:157] + "..."
        
        # Create implementation item
        item = {
            'priority': i,
            'filename': filename,
            'title': title,
            'meta_description': meta_description,
            'meta_title': meta_title,
            'keywords': keywords,
            'excerpt': meta_description[:100] + "...",
            'file_path': f'/home/idos/sc/startupcampus-blog/content/posts/{filename}'
        }
        
        implementation_plan.append(item)
        
        # Display plan item
        print(f"📝 {i:2d}. {title[:50]}{'...' if len(title) > 50 else ''}")
        print(f"     File: {filename}")
        print(f"     Description: {meta_description}")
        print(f"     Keywords: {', '.join(keywords)}")
        print()
    
    # Save implementation plan
    with open('/home/idos/sc/startupcampus-blog/seo_implementation_plan.json', 'w', encoding='utf-8') as f:
        json.dump(implementation_plan, f, indent=2, ensure_ascii=False)
    
    print("✅ Implementation plan saved to: seo_implementation_plan.json")
    
    # Generate sample frontmatter additions
    print("\n" + "=" * 70)
    print("📋 SAMPLE FRONTMATTER ADDITIONS FOR TOP 5 POSTS:")
    print("=" * 70)
    
    for i, item in enumerate(implementation_plan[:5], 1):
        print(f"\n{i}. FILE: {item['filename']}")
        print("ADD TO FRONTMATTER:")
        print("```yaml")
        print(f'description: "{item["meta_description"]}"')
        print(f'meta_title: "{item["meta_title"]}"')
        print(f'excerpt: "{item["excerpt"]}"')
        print(f'keywords: {item["keywords"]}')
        print("```")
    
    return implementation_plan

def main():
    """Main function"""
    print("🔧 SEO IMPLEMENTATION HELPER")
    print("=" * 50)
    
    # Generate implementation plan
    plan = generate_implementation_plan()
    
    print(f"\n📊 SUMMARY:")
    print(f"✅ Generated SEO recommendations for top 20 posts")
    print(f"📁 Implementation plan saved as JSON")
    print(f"🎯 Ready to implement SEO improvements systematically")
    
    print(f"\n⚠️  NEXT STEPS:")
    print(f"1. Review the generated meta descriptions and keywords")
    print(f"2. Customize descriptions for brand voice if needed")
    print(f"3. Add frontmatter fields to each post manually or via script")
    print(f"4. Test implementation on a few posts first")
    print(f"5. Monitor search performance improvements")

if __name__ == "__main__":
    main()