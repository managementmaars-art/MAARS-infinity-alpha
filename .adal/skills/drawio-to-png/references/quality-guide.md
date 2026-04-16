# Quality and Resolution Guide

Guidelines for choosing the right export quality settings for different use cases.

## Understanding Scale Factor

The scale factor multiplies the diagram's native resolution:

- Scale `1.0` = 100% = Original size
- Scale `2.0` = 200% = 4x more pixels (2x width × 2x height)
- Scale `3.0` = 300% = 9x more pixels
- Scale `4.0` = 400% = 16x more pixels

## DPI Equivalents

Assuming a base DPI of 96 (standard screen resolution):

| Scale | Effective DPI | Use Case |
|-------|---------------|----------|
| 0.5   | 48 DPI       | Thumbnails, icons |
| 1.0   | 96 DPI       | Web images, basic documentation |
| 1.5   | 144 DPI      | High-DPI displays, better web quality |
| 2.0   | 192 DPI      | **Recommended default** - High quality for all screens |
| 3.0   | 288 DPI      | Presentations on large displays |
| 4.0   | 384 DPI      | Print materials, professional publishing |
| 5.0   | 480 DPI      | High-quality printing |

## Recommended Settings by Use Case

### Web Publishing

**Standard Web Page**
```bash
# Good balance of quality and file size
drawio -x -f png -s 1.5 -o output.png input.drawio
```
- Scale: 1.5x
- DPI: ~144
- File size: Moderate
- Quality: Good for all modern displays

**Retina/HiDPI Display**
```bash
# Crisp on high-DPI displays
drawio -x -f png -s 2 -o output.png input.drawio
```
- Scale: 2x
- DPI: ~192
- File size: Larger
- Quality: Excellent on retina displays

**Thumbnail/Preview**
```bash
# Small file size for previews
drawio -x -f png -s 0.5 -w 400 -o thumbnail.png input.drawio
```
- Scale: 0.5x or fixed width
- DPI: ~48
- File size: Small
- Quality: Sufficient for previews

### Documentation

**Markdown/Wiki Documentation**
```bash
# Good for GitHub, Confluence, Notion
drawio -x -f png -s 2 --border 10 -o diagram.png input.drawio
```
- Scale: 2x
- Border: 10px (better visibility)
- DPI: ~192
- Quality: Crisp and readable

**Technical Manuals (Digital)**
```bash
# High quality for PDF documentation
drawio -x -f png -s 3 -o diagram.png input.drawio
```
- Scale: 3x
- DPI: ~288
- Quality: Professional digital documentation

**Technical Manuals (Print)**
```bash
# Print-ready quality
drawio -x -f png -s 4 -o diagram.png input.drawio
```
- Scale: 4x
- DPI: ~384
- Quality: Professional printing

### Presentations

**Standard Presentation (1080p)**
```bash
# For Full HD (1920×1080) displays
drawio -x -f png -s 2 -o slide-diagram.png input.drawio
```
- Scale: 2x
- DPI: ~192
- Resolution: Sufficient for 1080p

**4K Presentation (2160p)**
```bash
# For 4K (3840×2160) displays
drawio -x -f png -s 3 -o slide-diagram.png input.drawio
```
- Scale: 3x
- DPI: ~288
- Resolution: Sharp on 4K displays

**Conference/Large Screen**
```bash
# For large projection screens
drawio -x -f png -s 4 -o slide-diagram.png input.drawio
```
- Scale: 4x
- DPI: ~384
- Resolution: Crisp on very large displays

### Print Materials

**Office Printing (Letter/A4)**
```bash
# 300 DPI print quality
drawio -x -f png -s 3 -o print-diagram.png input.drawio
```
- Scale: 3x
- Effective DPI: ~288-300
- Quality: Good for office printers

**Professional Printing**
```bash
# 400+ DPI for high-quality printing
drawio -x -f png -s 4 -o print-diagram.png input.drawio
```
- Scale: 4x
- Effective DPI: ~384
- Quality: Professional print shops

**Large Format (Posters, Banners)**
```bash
# Very high resolution
drawio -x -f png -s 5 -o poster-diagram.png input.drawio
```
- Scale: 5x
- Effective DPI: ~480
- Quality: Large format printing

### Social Media

**Twitter/X**
```bash
# Optimized for Twitter's image compression
drawio -x -f png -s 2 --transparent -o twitter.png input.drawio
```
- Scale: 2x
- Transparent: Yes
- Max dimensions: 4096×4096

**LinkedIn**
```bash
# LinkedIn article images
drawio -x -f png -s 2 -w 1200 -o linkedin.png input.drawio
```
- Scale: 2x or fixed width
- Recommended width: 1200px

**Instagram**
```bash
# Square format for Instagram
drawio -x -f png -s 2 -w 1080 -h 1080 -o instagram.png input.drawio
```
- Scale: 2x
- Aspect ratio: 1:1 (square)
- Size: 1080×1080

## File Size Considerations

### Typical File Sizes (for medium complexity diagram)

| Scale | Approximate Size | Growth Factor |
|-------|-----------------|---------------|
| 1.0   | 100 KB         | 1x (baseline) |
| 2.0   | 400 KB         | 4x |
| 3.0   | 900 KB         | 9x |
| 4.0   | 1.6 MB         | 16x |

**Notes**:
- Actual size depends on diagram complexity
- Transparent background slightly increases size
- PNG compression is lossless

### Optimization Strategies

**1. Use Appropriate Scale**
- Don't over-export (4x for web is wasteful)
- Match scale to intended display size

**2. Post-processing Compression**
```bash
# Using pngquant (lossy but high quality)
pngquant --quality=80-95 --speed 1 output.png -o optimized.png

# Using optipng (lossless)
optipng -o7 output.png

# Using ImageMagick
convert output.png -strip -quality 85 optimized.png
```

**3. Consider SVG for Web**
```bash
# SVG is often smaller and scalable
drawio -x -f svg -o output.svg input.drawio
```
- Pros: Scalable, often smaller, crisp at any size
- Cons: Compatibility, complex diagrams may render slowly

**4. Progressive Loading**
```html
<!-- Load low-res first, high-res on demand -->
<img src="diagram-1x.png" 
     data-src-2x="diagram-2x.png"
     loading="lazy">
```

## Quality Checklist

### Before Export

- [ ] Verify diagram content is correct
- [ ] Check all text is readable at target size
- [ ] Remove unnecessary elements
- [ ] Ensure proper alignment and spacing

### Choosing Settings

- [ ] Determine primary use case (web, print, presentation)
- [ ] Select appropriate scale factor
- [ ] Decide on transparent vs. solid background
- [ ] Consider border for better visibility
- [ ] Estimate final file size

### After Export

- [ ] Verify text is crisp and readable
- [ ] Check colors match original diagram
- [ ] Confirm file size is acceptable
- [ ] Test on target platform/device
- [ ] Consider compression if file is too large

## Common Quality Issues

### Blurry Text

**Problem**: Text appears fuzzy or pixelated

**Solutions**:
- Increase scale factor (2x minimum recommended)
- Use larger fonts in original diagram
- Ensure text is not inside rotated or transformed groups

### Large File Size

**Problem**: PNG file is too large for web use

**Solutions**:
- Reduce scale factor if over-exported
- Compress with pngquant or similar
- Consider SVG format instead
- Remove embedded images or simplify diagram

### Transparent Background Issues

**Problem**: Transparency not working or showing artifacts

**Solutions**:
- Ensure `--transparent` flag is used
- Check original diagram has no background color set
- Verify PNG format supports transparency (not JPEG)

### Color Differences

**Problem**: Colors look different after export

**Solutions**:
- Check color profile settings
- Ensure consistent lighting in original diagram
- Verify export format supports full color range
- Test on multiple displays

## Best Practices Summary

1. **Default to 2x scale** for most use cases
2. **Use transparent background** for flexibility
3. **Add border** (10-20px) for documentation
4. **Compress for web** but keep originals at high quality
5. **Test on target platform** before finalizing
6. **Keep source files** to regenerate if needed
7. **Automate export** for consistency across project
8. **Document your settings** for reproducibility

## Quick Reference Table

| Use Case | Scale | Transparent | Border | Notes |
|----------|-------|-------------|--------|-------|
| Web thumbnail | 0.5-1.0 | Yes | 0 | Small file size |
| Web image | 1.5-2.0 | Yes | 10 | Default choice |
| Documentation | 2.0 | No | 10 | Clear background |
| Slides (1080p) | 2.0 | Yes | 0 | Standard presentation |
| Slides (4K) | 3.0 | Yes | 0 | High-res display |
| Print (office) | 3.0 | No | 0 | 300 DPI equivalent |
| Print (pro) | 4.0 | No | 0 | Professional quality |
| Social media | 2.0 | Yes | 0 | Platform-specific sizes |
