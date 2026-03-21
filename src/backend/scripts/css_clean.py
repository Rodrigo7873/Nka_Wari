import os
import re

css_dir = r"d:\Mes projet\N'ka_Wari\src\frontend\static\css"

def clean_css_file(filepath):
    # skip base.css and theme.css
    if filepath.endswith('theme.css') or filepath.endswith('base.css'):
        return False
        
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
        
    original = content
    
    # 1. Backgrounds
    # Match background(-color): white | #fff | #ffffff;
    content = re.sub(r'(background(?:-color)?):\s*(?:white|#ffffff|#fff)\b', r'\1: var(--bg-card)', content, flags=re.IGNORECASE)
    # Match #f9fafb, #f8fafc, #f1f5f9 (Page backgrounds)
    content = re.sub(r'(background(?:-color)?):\s*(?:#f9fafb|#f8fafc|#f1f5f9|#f3f4f6)\b', r'\1: var(--bg-page)', content, flags=re.IGNORECASE)
    
    # 2. Text colors
    # Primary texts
    content = re.sub(r'(color):\s*(?:#1e2b3c|#111827|#1f2937|#1e293b|#0f172a|black|#000000|#000)\b', r'\1: var(--text-primary)', content, flags=re.IGNORECASE)
    # Secondary texts
    content = re.sub(r'(color):\s*(?:#4b5563|#64748b|#94a3b8|#6b7280|#475569|#334155)\b', r'\1: var(--text-secondary)', content, flags=re.IGNORECASE)
    
    # 3. Borders
    content = re.sub(r'(border(?:-[a-z]+)?):\s*([^;\}]+)(?:#e2e8f0|#d1d5db|#e5e7eb|#cbd5e1|#ccc|#cccccc)', r'\1: \2var(--border)', content, flags=re.IGNORECASE)
    content = re.sub(r'(border-color):\s*(?:#e2e8f0|#d1d5db|#e5e7eb|#cbd5e1|#ccc|#cccccc)', r'\1: var(--border)', content, flags=re.IGNORECASE)

    # 4. Box shadows using specific light colors might remain as is, or we can leave them for now.
    
    if content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False

c = 0
for root, dirs, files in os.walk(css_dir):
    for f in files:
        if f.endswith('.css'):
            if clean_css_file(os.path.join(root, f)):
                print(f"Updated {f}")
                c += 1

print(f"Updated {c} CSS files.")
