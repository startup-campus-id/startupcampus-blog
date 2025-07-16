---
title: "{{ replace .File.ContentBaseName "-" " " | title }}"
date: {{ .Date }}
author: "Startup Campus"
categories: ["Digital"]
slug: "{{ .File.ContentBaseName }}"
featured_image: "/blog/images/placeholder.jpg"
description: "Write a compelling meta description (150-160 characters) that summarizes the post content and includes target keywords."
tags: ["tag1", "tag2", "tag3"]
draft: true
---
