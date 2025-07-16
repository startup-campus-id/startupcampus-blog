#!/usr/bin/env python3
"""
Generate a comprehensive SEO audit report with recommendations
"""

import json
from pathlib import Path

def generate_meta_description(title: str, first_paragraph: str, topics: list) -> str:
    """Generate suggested meta description based on content analysis"""
    
    # Extract key action words and benefits from title and content
    clean_paragraph = first_paragraph.replace('\n', ' ').strip()
    
    # Create focused meta descriptions based on topics
    if 'certification' in topics:
        if 'bnsp' in title.lower():
            return f"Pelajari cara mendapatkan sertifikasi BNSP untuk meningkatkan karir. {clean_paragraph[:100]}... Panduan lengkap dan mudah dipahami!"
        else:
            return f"Tingkatkan kredibilitas profesional dengan sertifikasi yang tepat. {clean_paragraph[:80]}... Mulai perjalanan karir impian Anda!"
    
    elif 'bootcamp' in topics:
        return f"Temukan bootcamp terbaik untuk mengembangkan skill digital. {clean_paragraph[:80]}... Siap kerja dalam hitungan bulan!"
    
    elif 'career' in topics:
        if 'gaji' in title.lower() or 'salary' in title.lower():
            return f"Ketahui peluang karir dan gaji di bidang teknologi. {clean_paragraph[:80]}... Raih penghasilan impian Anda!"
        else:
            return f"Panduan karir lengkap untuk mencapai kesuksesan profesional. {clean_paragraph[:70]}... Tips praktis yang terbukti efektif!"
    
    elif 'technology' in topics:
        if 'ai' in title.lower():
            return f"Pelajari teknologi AI terbaru dan penerapannya. {clean_paragraph[:80]}... Jadilah ahli di era digital!"
        else:
            return f"Kuasai teknologi terkini untuk kemajuan karir. {clean_paragraph[:80]}... Solusi praktis dan mudah dipahami!"
    
    elif 'startup' in topics:
        return f"Panduan membangun startup dan bisnis yang sukses. {clean_paragraph[:80]}... Tips dari para ahli dan praktisi!"
    
    else:
        # Generic meta description
        return f"{clean_paragraph[:120]}... Pelajari lebih lanjut di Startup Campus untuk mengembangkan skill dan karir impian!"

def generate_keywords(title: str, topics: list) -> list:
    """Generate relevant keywords based on title and topics"""
    keywords = []
    
    # Base keywords from title
    title_words = title.lower().split()
    important_words = [word for word in title_words if len(word) > 3 and word not in ['yang', 'untuk', 'dengan', 'dalam', 'dari', 'atau']]
    keywords.extend(important_words[:5])
    
    # Topic-based keywords
    if 'certification' in topics:
        keywords.extend(['sertifikasi', 'bnsp', 'kompetensi', 'kredensial'])
    if 'bootcamp' in topics:
        keywords.extend(['bootcamp', 'pelatihan', 'kursus', 'skill digital'])
    if 'career' in topics:
        keywords.extend(['karir', 'pekerjaan', 'kerja', 'profesi'])
    if 'technology' in topics:
        keywords.extend(['teknologi', 'digital', 'ai', 'data science'])
    if 'startup' in topics:
        keywords.extend(['startup', 'bisnis', 'entrepreneur'])
    
    # General keywords
    keywords.extend(['startup campus', 'indonesia', 'panduan', 'tips'])
    
    return list(set(keywords))[:10]  # Remove duplicates and limit to 10

def main():
    """Generate comprehensive SEO audit report"""
    
    # Load audit results
    with open('/home/idos/sc/startupcampus-blog/seo_audit_results.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Generate report
    report = []
    
    report.append("# 🚀 COMPREHENSIVE SEO AUDIT REPORT")
    report.append("## Startup Campus Blog - 125 Posts Analysis")
    report.append("=" * 80)
    report.append("")
    
    # Executive Summary
    report.append("## 📋 EXECUTIVE SUMMARY")
    report.append("")
    report.append(f"**Total Posts Analyzed:** {data['total_posts']}")
    report.append(f"**Critical Finding:** 100% of posts are missing essential SEO fields")
    report.append("")
    report.append("### ⚠️ CRITICAL SEO GAPS:")
    report.append(f"- **{data['missing_description']} posts** missing meta descriptions (100%)")
    report.append(f"- **{data['missing_meta_title']} posts** missing meta titles (100%)")
    report.append(f"- **{data['missing_excerpt']} posts** missing excerpts (100%)")
    report.append(f"- **{data['missing_keywords']} posts** missing keywords/tags (100%)")
    report.append("")
    
    # Title Analysis
    report.append("### 📏 TITLE LENGTH ANALYSIS:")
    report.append(f"- **Optimal length (30-60 chars):** {data['title_analysis']['optimal']} posts (57.6%)")
    report.append(f"- **Too long (>60 chars):** {data['title_analysis']['too_long']} posts (41.6%)")
    report.append(f"- **Too short (<30 chars):** {data['title_analysis']['too_short']} posts (0.8%)")
    report.append("")
    
    # Priority Analysis
    high_priority = [p for p in data['posts'] if p['priority_score'] >= 9]
    medium_priority = [p for p in data['posts'] if 7 <= p['priority_score'] < 9]
    
    report.append("### 🎯 PRIORITY ANALYSIS:")
    report.append(f"- **High Priority (Score 9-10):** {len(high_priority)} posts")
    report.append(f"- **Medium Priority (Score 7-8):** {len(medium_priority)} posts")
    report.append(f"- **Lower Priority (Score <7):** {len(data['posts']) - len(high_priority) - len(medium_priority)} posts")
    report.append("")
    
    # Recommendations
    report.append("## 🎯 IMMEDIATE ACTION RECOMMENDATIONS")
    report.append("")
    report.append("### 1. CRITICAL PRIORITY - Add Meta Descriptions to Top 20 Posts")
    report.append("Focus on high-impact posts about certifications, bootcamps, and career advice.")
    report.append("")
    report.append("### 2. OPTIMIZE TITLE LENGTHS")
    report.append("52 posts have titles longer than 60 characters - these should be shortened for better SEO.")
    report.append("")
    report.append("### 3. ADD STRUCTURED DATA")
    report.append("Implement keywords/tags for better categorization and discoverability.")
    report.append("")
    
    # Top 20 Posts with Suggestions
    report.append("## 🏆 TOP 20 PRIORITY POSTS WITH SEO RECOMMENDATIONS")
    report.append("")
    
    for i, post in enumerate(data['posts'][:20], 1):
        report.append(f"### {i}. {post['title']}")
        report.append(f"**File:** `{post['filename']}`")
        report.append(f"**Priority Score:** {post['priority_score']}/10")
        report.append(f"**Title Length:** {post['title_length']} chars ({post['title_category']})")
        report.append(f"**Topics:** {', '.join(post['topics'])}")
        report.append("")
        
        # Generate suggestions
        suggested_desc = generate_meta_description(post['title'], post['first_paragraph'], post['topics'])
        suggested_keywords = generate_keywords(post['title'], post['topics'])
        
        report.append("**🔧 SUGGESTED FRONTMATTER ADDITIONS:**")
        report.append("```yaml")
        report.append(f'description: "{suggested_desc}"')
        report.append(f'meta_title: "{post["title"]} | Startup Campus"')
        report.append(f'excerpt: "{suggested_desc[:100]}..."')
        report.append(f'keywords: {suggested_keywords}')
        report.append("```")
        report.append("")
        
        if post['title_length'] > 60:
            # Suggest shorter title
            short_title = post['title'][:55] + "..."
            report.append(f"**⚠️ TITLE TOO LONG:** Consider shortening to: `{short_title}`")
            report.append("")
        
        report.append("---")
        report.append("")
    
    # Category-specific analysis
    report.append("## 📊 CONTENT CATEGORY ANALYSIS")
    report.append("")
    
    # Count posts by topic
    topic_counts = {}
    for post in data['posts']:
        for topic in post['topics']:
            topic_counts[topic] = topic_counts.get(topic, 0) + 1
    
    report.append("### Content Distribution by Topic:")
    for topic, count in sorted(topic_counts.items(), key=lambda x: x[1], reverse=True):
        percentage = (count / data['total_posts']) * 100
        report.append(f"- **{topic.title()}:** {count} posts ({percentage:.1f}%)")
    report.append("")
    
    # Implementation timeline
    report.append("## 🗓️ IMPLEMENTATION TIMELINE")
    report.append("")
    report.append("### Week 1-2: Critical Posts (Priority 10)")
    week1_posts = [p for p in data['posts'] if p['priority_score'] == 10]
    report.append(f"Add meta descriptions to {len(week1_posts)} highest priority posts")
    report.append("")
    
    report.append("### Week 3-4: High Priority Posts (Priority 8-9)")
    week2_posts = [p for p in data['posts'] if 8 <= p['priority_score'] < 10]
    report.append(f"Complete SEO optimization for {len(week2_posts)} high priority posts")
    report.append("")
    
    report.append("### Month 2: Medium Priority Posts (Priority 6-7)")
    month2_posts = [p for p in data['posts'] if 6 <= p['priority_score'] < 8]
    report.append(f"Optimize {len(month2_posts)} medium priority posts")
    report.append("")
    
    report.append("### Month 3: Remaining Posts")
    remaining_posts = [p for p in data['posts'] if p['priority_score'] < 6]
    report.append(f"Complete SEO optimization for remaining {len(remaining_posts)} posts")
    report.append("")
    
    # Tools and process
    report.append("## 🛠️ RECOMMENDED TOOLS & PROCESS")
    report.append("")
    report.append("### SEO Tools to Use:")
    report.append("- **Google Search Console** - Monitor search performance")
    report.append("- **Google Analytics** - Track organic traffic improvements")
    report.append("- **Yoast SEO** (if using WordPress) - Real-time SEO scoring")
    report.append("- **SEMrush/Ahrefs** - Keyword research and competitor analysis")
    report.append("")
    
    report.append("### Quality Assurance Checklist:")
    report.append("- [ ] Meta description 150-160 characters")
    report.append("- [ ] Title 50-60 characters for optimal display")
    report.append("- [ ] 5-10 relevant keywords per post")
    report.append("- [ ] Excerpt summarizes main value proposition")
    report.append("- [ ] Internal linking to related posts")
    report.append("")
    
    # Expected impact
    report.append("## 📈 EXPECTED IMPACT")
    report.append("")
    report.append("### Short-term (1-3 months):")
    report.append("- 25-40% improvement in click-through rates from search results")
    report.append("- Better categorization and internal linking")
    report.append("- Improved user experience with clear post summaries")
    report.append("")
    
    report.append("### Long-term (3-6 months):")
    report.append("- 15-30% increase in organic search traffic")
    report.append("- Higher rankings for target keywords")
    report.append("- Improved domain authority and search visibility")
    report.append("")
    
    # Save report
    report_content = "\n".join(report)
    
    with open('/home/idos/sc/startupcampus-blog/SEO_AUDIT_REPORT.md', 'w', encoding='utf-8') as f:
        f.write(report_content)
    
    print("✅ Comprehensive SEO Audit Report generated!")
    print("📄 Report saved as: SEO_AUDIT_REPORT.md")
    print(f"📊 Total analysis: {data['total_posts']} posts")
    print(f"🎯 High priority posts: {len(high_priority)}")
    print(f"⚠️ Critical finding: 100% of posts missing SEO fields")

if __name__ == "__main__":
    main()