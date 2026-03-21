import os
import re

directory = r"d:\Mes projet\N'ka_Wari\src\frontend\templates\modules"

def process_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    original_content = content

    # Les remplacements basiques directement sur les chaînes courantes (pour éviter les erreurs de parsing complexe)
    # Pour text-main
    content = re.sub(r'color:\s*#1e2b3c;?', '', content)
    content = re.sub(r'class="([^"]*)"([^>]*)class="text-main"', r'class="\1 text-main"\2', content)
    
    # Nous allons remplacer le style et si la balise n'a pas class="", nous l'ajoutons à côté du style=
    # Ce n'est pas trivial par regex simple. Faisons une passe ciblée.
    
    # On va rechercher toutes les balises ayant style="..."
    def style_replacer(match):
        full_tag = match.group(0)
        
        style_match = re.search(r'style="([^"]*)"', full_tag)
        if not style_match:
            return full_tag
            
        style_content = style_match.group(1)
        classes_to_add = set()
        
        # 1. Backgrounds
        if re.search(r'background(?:-color)?:\s*(?:white|#ffffff|#fff)\b;?', style_content, re.IGNORECASE):
            classes_to_add.add('bg-card')
            style_content = re.sub(r'background(?:-color)?:\s*(?:white|#ffffff|#fff)\b;?', '', style_content, flags=re.IGNORECASE)
            
        # 2. Colors text-main
        if re.search(r'color:\s*(?:#1e2b3c|#111827|#1f2937)\b;?', style_content, re.IGNORECASE):
            classes_to_add.add('text-main')
            style_content = re.sub(r'color:\s*(?:#1e2b3c|#111827|#1f2937)\b;?', '', style_content, flags=re.IGNORECASE)
            
        # 3. Colors text-muted
        if re.search(r'color:\s*(?:#64748b|#94a3b8|#6b7280|#475569)\b;?', style_content, re.IGNORECASE):
            classes_to_add.add('text-muted')
            style_content = re.sub(r'color:\s*(?:#64748b|#94a3b8|#6b7280|#475569)\b;?', '', style_content, flags=re.IGNORECASE)
            
        # 4. Success / Danger
        if re.search(r'color:\s*#10b981\b;?', style_content, re.IGNORECASE):
            classes_to_add.add('text-success')
            style_content = re.sub(r'color:\s*#10b981\b;?', '', style_content, flags=re.IGNORECASE)
            
        if re.search(r'color:\s*#ef4444\b;?', style_content, re.IGNORECASE):
            classes_to_add.add('text-danger')
            style_content = re.sub(r'color:\s*#ef4444\b;?', '', style_content, flags=re.IGNORECASE)
            
        if re.search(r'color:\s*#f59e0b\b;?', style_content, re.IGNORECASE):
            classes_to_add.add('text-warning')
            style_content = re.sub(r'color:\s*#f59e0b\b;?', '', style_content, flags=re.IGNORECASE)

        if not classes_to_add:
            return full_tag
            
        # Clean up style
        style_content = style_content.strip()
        if style_content.endswith(';'):
            # clean up extra spaces
            style_content = re.sub(r'\s+', ' ', style_content)
            
        # Reconstruct the tag
        # add classes to existing class attr or create new one
        class_match = re.search(r'class="([^"]*)"', full_tag)
        if class_match:
            existing_classes = set(class_match.group(1).split())
            existing_classes.update(classes_to_add)
            new_class_str = f'class="{" ".join(existing_classes)}"'
            full_tag = full_tag.replace(class_match.group(0), new_class_str)
        else:
            full_tag = full_tag.replace('style=', f'class="{" ".join(classes_to_add)}" style=')
            
        # update style attribute
        if not style_content or style_content == ';':
            full_tag = re.sub(r'\s*style="[^"]*"\s*', ' ', full_tag)
        else:
            full_tag = re.sub(r'style="[^"]*"', f'style="{style_content}"', full_tag)
            
        return full_tag

    # Match an HTML tag containing style="..."
    content = re.sub(r'<[^>]+style="[^"]*"[^>]*>', style_replacer, content)

    if content != original_content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False

count = 0
for root, dirs, files in os.walk(directory):
    for file in files:
        if file.endswith('.html'):
            if process_file(os.path.join(root, file)):
                count += 1
                print(f"Updated {file}")

print(f"Total files updated: {count}")
