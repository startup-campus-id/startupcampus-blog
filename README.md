# Startup Campus Blog

![Deploy to GCS](https://github.com/startupcampus/startupcampus-blog/actions/workflows/deploy.yml/badge.svg)

Hugo-based blog for Startup Campus, automatically deployed to Google Cloud Storage.

## 🚀 Quick Start

### Prerequisites
- Hugo v0.147.9 (extended version)
- Node.js 18+
- npm

### Local Development

```bash
# Clone the repository
git clone https://github.com/startupcampus/startupcampus-blog.git
cd startupcampus-blog

# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build:production
```

### Manual Deployment

```bash
# Build and deploy to GCS
npm run build:production && gsutil -m rsync -r -d public/ gs://startupcampus-blog-static/blog/
```

## 🤖 Automated Deployment

This repository uses GitHub Actions for automated deployment. Every push to `main` or `master` branch triggers:

1. Hugo build process
2. Deployment to Google Cloud Storage
3. Site available at https://startupcampus.id/blog/

### Setup Instructions

See [GITHUB-ACTIONS-SETUP.md](./GITHUB-ACTIONS-SETUP.md) for detailed setup instructions.

## 📁 Project Structure

```
startupcampus-blog/
├── .github/workflows/   # GitHub Actions workflows
├── archetypes/         # Hugo archetypes
├── assets/            # CSS and other assets
├── content/           # Blog content
│   ├── posts/        # Blog posts
│   └── pages/        # Static pages
├── layouts/           # Hugo templates
├── static/            # Static files
├── themes/            # Hugo themes
└── config.toml        # Hugo configuration
```

## 📝 Content Management

### Creating a New Post

```bash
hugo new posts/my-new-post.md
```

### Post Front Matter

```yaml
---
title: "Your Post Title"
date: 2025-07-09
description: "Brief description"
tags: ["tag1", "tag2"]
categories: ["category"]
author: "Author Name"
image: "images/featured-image.jpg"
---
```

## 🛠️ Configuration

- **Hugo Config**: `config.toml`
- **Build Scripts**: `package.json`
- **GitHub Actions**: `.github/workflows/deploy.yml`

## 📊 Performance

- Hugo static site generation
- Deployed to Google Cloud Storage
- Served via CDN for optimal performance

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is proprietary to Startup Campus.

## 🆘 Support

For issues or questions:
- Check existing [GitHub Issues](https://github.com/startupcampus/startupcampus-blog/issues)
- Contact the development team