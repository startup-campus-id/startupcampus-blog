# 📋 Manual Testing Guide - Startup Campus Blog

## ✅ Fixed Issues Summary

All requested issues have been resolved by the sub-agents:

- **🧪 QAAgent**: ✅ Fixed duplicate image in iLEAD 2025 post
- **🎨 DesignAgent**: ✅ Fixed horizontal scrolling, container width, and pagination

---

## 🔍 Testing Checklist

### 1. **Responsive Design Testing**

#### Desktop (1200px+)
- [ ] Visit `http://localhost:1313/`
- [ ] Verify 3-column post grid displays properly
- [ ] Check that posts don't overflow container width
- [ ] Confirm navigation menu is horizontal

#### Tablet (768px - 1200px)
- [ ] Resize browser window to ~800px width
- [ ] Verify posts adapt to 2-column layout
- [ ] Check navigation still works properly

#### Mobile (< 768px)
- [ ] Resize browser window to ~400px width
- [ ] **Critical**: Verify NO horizontal scrolling occurs
- [ ] Confirm posts display in single column
- [ ] Check navigation collapses vertically
- [ ] Test that all content fits within screen width

#### Extra Small Mobile (< 480px)
- [ ] Test on ~350px width
- [ ] Verify all elements are still readable
- [ ] Check padding/margins are appropriate

---

### 2. **Pagination Testing**

#### Test Smart Pagination with Ellipsis
- [ ] Go to `http://localhost:1313/`
- [ ] **Expected**: See pagination like `1 2 3 ... 20` instead of `1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20`
- [ ] Click to page 5
- [ ] **Expected**: See pagination like `1 ... 3 4 5 6 7 ... 20`
- [ ] Click to page 15
- [ ] **Expected**: See pagination like `1 ... 13 14 15 16 17 ... 20`
- [ ] Test on mobile (< 768px) - pagination should wrap properly

---

### 3. **Content Quality Testing**

#### Duplicate Image Fix
- [ ] Visit `http://localhost:1313/ilead-2025-perjalanan-menemukan-diri-di-wonderland-of-ayodya/`
- [ ] **Critical**: Verify there's only ONE featured image (not duplicate)
- [ ] Check that date shows "11 Juni 2025" (not "11 Juni 2**025")

#### Random Post Checks
- [ ] Visit 3-5 random posts from homepage
- [ ] Verify images load properly
- [ ] Check formatting looks consistent
- [ ] Test post navigation works

---

### 4. **Cross-Browser Testing**

#### Essential Browsers
- [ ] **Chrome**: Test all above scenarios
- [ ] **Firefox**: Test responsive design
- [ ] **Safari** (if available): Test layout consistency
- [ ] **Edge**: Test pagination behavior

#### Mobile Browser Testing (if possible)
- [ ] **Chrome Mobile**: Test horizontal scrolling
- [ ] **Safari Mobile**: Test navigation collapse

---

### 5. **Performance Testing**

#### Page Load Speed
- [ ] Use browser dev tools (F12)
- [ ] Check homepage loads in < 3 seconds
- [ ] Verify CSS and images are cached properly

#### Console Errors
- [ ] Open dev tools console (F12)
- [ ] Navigate between pages
- [ ] **Critical**: Verify NO JavaScript errors appear
- [ ] Check for any missing resource warnings

---

## 🚨 Critical Issues to Report

If you find any of these, please report immediately:

### High Priority
- ❌ Horizontal scrolling on mobile (< 768px)
- ❌ Posts extending beyond container width
- ❌ Pagination showing all 20 numbers instead of ellipsis
- ❌ Duplicate images in any posts
- ❌ Navigation menu breaking on mobile

### Medium Priority
- ⚠️ Images not loading properly
- ⚠️ Layout inconsistencies between pages
- ⚠️ Text wrapping issues on small screens

### Low Priority
- 💡 Minor styling adjustments
- 💡 Color contrast improvements
- 💡 Performance optimizations

---

## 🛠️ How to Test

### Start Local Server
```bash
cd /home/idos/sc/startupcampus-blog
./hugo server -D
```

### Access Site
- **Homepage**: http://localhost:1313/
- **Post example**: http://localhost:1313/ilead-2025-perjalanan-menemukan-diri-di-wonderland-of-ayodya/
- **Category page**: http://localhost:1313/categories/

### Browser Dev Tools
- **Responsive Mode**: F12 → Device Toolbar (mobile icon)
- **Console**: F12 → Console tab
- **Network**: F12 → Network tab (for performance)

---

## 📱 Recommended Test Devices/Sizes

| Device Type | Width | Test Focus |
|-------------|-------|------------|
| Desktop | 1920px | Layout, full features |
| Laptop | 1366px | Standard desktop view |
| Tablet | 768px | Layout transitions |
| Mobile Large | 414px | Navigation, scrolling |
| Mobile Small | 320px | Content accessibility |

---

## 📊 Expected Results

### ✅ Success Criteria
- No horizontal scrolling on any screen size
- Pagination shows ellipsis (not all 20 pages)
- Clean single image in iLEAD post
- 3-column → 2-column → 1-column responsive flow
- All navigation elements accessible on mobile

### 🔄 Fallback Options
If issues persist:
1. Clear browser cache
2. Restart Hugo server
3. Test in incognito/private browsing mode

---

**Happy Testing! 🚀**

*If all tests pass, the blog is ready for production deployment!*