# 🚀 Next Steps for Startup Campus Blog Migration — *Subagent Workflow*

## ✅ Current Status
- Hugo site initialized and configured
- WordPress posts and categories synced
- Basic layouts ready, git committed
- Featured images 93% downloaded (116/125)

---

## 🧩 Parallel Task Breakdown by Subagents

### 🎨 DesignAgent – CSS & Theme Improvements
- [ ] Improve **Landing Page Styling**:
  - Match layout/spacing with https://www.startupcampus.id/blog/
  - Tweak card spacing, font sizing, image sizing
  - Ensure grid layout + mobile responsiveness

- [ ] Enhance **Category Pages**:
  - Align with WP design
  - Fix pagination + add breadcrumb nav
  - Ensure theme consistency (colors, typography)

---

### 👩‍💻 DevAgent – Hugo Architecture & Build
- [ ] Finalize **Navigation & Information Architecture**:
  - Build header menu + logo
  - Configure sidebar: category widgets, recent posts
  - Design footer matching WP structure

- [ ] Implement **Redirection Logic**:
  - Map old WP URLs → new Hugo paths
  - Setup 404 page, redirect rules

- [ ] **Performance Optimization**:
  - Minify CSS/JS, optimize images, add caching headers

---

### 🔍 SEOAgent – Metadata & SEO Health
- [ ] Add **Meta Tags**:
  - Title, meta descriptions, Open Graph, Twitter Cards

- [ ] Configure **SEO**:
  - robots.txt, sitemap.xml, schema markup, Hugo SEO settings

- [ ] Set up **Icons**:
  - Favicon, Apple touch icons, manifest.json

---

### ☁️ InfraAgent – Deployment Setup
- [ ] Choose hosting (Netlify, Vercel, AWS)
- [ ] Configure Hugo build + custom domain
- [ ] Enable SSL, CDN, and caching layers

---

### 🧪 QAAgent – Content & Link Integrity
- [ ] Review all post formatting and image placement
- [ ] Check internal link correctness
- [ ] Confirm alt text and accessibility compliance
- [ ] Validate mobile rendering across screen sizes

---

### 📊 AnalyticsAgent – Metrics Integration
- [ ] Add Google Analytics or Matomo
- [ ] Configure basic pageview tracking
- [ ] Optional: Track newsletter signups or goal events

---

### 🧠 SynthAgent – Coordination & Consistency
- [ ] Monitor agent outputs for cross-team consistency
- [ ] Run integration checks (e.g., link working, layout coherent)
- [ ] Summarize status for each agent and flag blockers
- [ ] Review tools/scripts used and suggest any updates

---

## 📸 Remaining Image Gaps – QAAgent & DevAgent
These 9 posts are missing featured images. QAAgent should verify whether this is expected (check WordPress), and DevAgent may use fallback logic:

- `10-web-ai-gratis-yang-bisa-membantu-pekerjaan-sehari-hari`
- `semua-karyawan-wajib-punya-sertifikasi-data-analyst-atau-bakal-tergeser-ai`
- `pentingnya-design-system-dalam-pengembangan-produk-digital`
- `jenis-analisis-data-dan-manfaatnya-sehari-hari`
- `7-tips-apply-kerja-di-jobstreet-auto-dipanggil-wawancara`
- `studi-independen-tanpa-uang-saku-gak-masalah`
- `keliling-dunia-tanpa-paspor`
- `pilih-kursus-ai-atau-data-science-dulu-temukan-jawaban-dan-prospek-karirnya`
- `ai-vs-machine-learning-vs-deep-learning-apa-bedanya`

---

## 🧰 Tools & Scripts – For DevAgent & QAAgent
- `scripts/download-all-missing-images.py` – Image automation
- `scripts/fix-hugo-categories.py` – Category correction
- `scripts/analyze-wordpress-categories.py` – Source analyzer
- `IMAGE_STATUS_REPORT.md`, `CATEGORY_FIX_SUMMARY.md` – QA references

---

## 🌐 Reference Links
- **Live WordPress**: https://www.startupcampus.id/blog/
- **WP JSON API**: https://www.startupcampus.id/blog/wp-json/wp/v2/posts
- **Hugo Local**: http://localhost:1313/

---

## 🔧 Commands (for DevAgent or InfraAgent)
```bash
# Local dev server
hugo server -D

# Category count
find content/posts -name "*.md" -exec grep -l "Alumni" {} \; | wc -l

# Image check
python3 scripts/check-images-status.py

# Deploy (when ready)
hugo --minify
