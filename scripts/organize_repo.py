#!/usr/bin/env python3
"""
Repository organizer script for awhitmana0.github.io
Automatically organizes files and generates READMEs with previews and URLs
"""

import os
import re
import shutil
from pathlib import Path
from urllib.parse import quote, unquote

# Configuration
BASE_URL = "https://awhitmana0.github.io"
REPO_ROOT = Path(__file__).parent.resolve()

# File type mappings
IMAGE_EXTENSIONS = {'.svg', '.png', '.jpg', '.jpeg', '.gif', '.webp'}
TEMPLATE_EXTENSIONS = {'.handlebars', '.hbs'}
CODE_EXTENSIONS = {'.js', '.css', '.html'}
FONT_EXTENSIONS = {'.woff', '.woff2', '.ttf', '.otf'}

# Files/directories to ignore
IGNORE_PATTERNS = {
    '.git', '.gitignore', '.DS_Store', 'README.md',
    '_config.yml', 'index.html', 'organize_repo.py',
    'untitled folder', 'scripts'
}

def get_url(file_path):
    """Generate GitHub Pages URL for a file"""
    rel_path = file_path.relative_to(REPO_ROOT)
    encoded_path = '/'.join(quote(part) for part in rel_path.parts)
    return f"{BASE_URL}/{encoded_path}"

def is_image(file_path):
    """Check if file is an image"""
    return file_path.suffix.lower() in IMAGE_EXTENSIONS

def organize_files():
    """Organize files into appropriate directories"""
    print("Organizing files...")

    # Create directories
    dirs = {
        'images': REPO_ROOT / 'images',
        'templates': REPO_ROOT / 'templates',
        'fonts': REPO_ROOT / 'fonts'
    }

    for dir_path in dirs.values():
        dir_path.mkdir(exist_ok=True)

    # Move files from root
    for item in REPO_ROOT.iterdir():
        if item.name in IGNORE_PATTERNS or item.is_dir():
            continue

        moved = False

        # Move images
        if item.suffix.lower() in IMAGE_EXTENSIONS:
            dest = dirs['images'] / item.name
            if not dest.exists():
                shutil.move(str(item), str(dest))
                print(f"  Moved {item.name} → images/")
                moved = True

        # Move templates
        elif item.suffix.lower() in TEMPLATE_EXTENSIONS:
            dest = dirs['templates'] / item.name
            if not dest.exists():
                shutil.move(str(item), str(dest))
                print(f"  Moved {item.name} → templates/")
                moved = True

        # Move fonts
        elif item.suffix.lower() in FONT_EXTENSIONS:
            dest = dirs['fonts'] / item.name
            if not dest.exists():
                shutil.move(str(item), str(dest))
                print(f"  Moved {item.name} → fonts/")
                moved = True

        # Move loose code files
        elif item.suffix.lower() in CODE_EXTENSIONS and item.name not in {'index.html', 'exampleCustomTemplate.html'}:
            dest = REPO_ROOT / 'code' / item.name
            dest.parent.mkdir(exist_ok=True)
            if not dest.exists():
                shutil.move(str(item), str(dest))
                print(f"  Moved {item.name} → code/")
                moved = True

    # Also check code directory for misplaced templates
    code_dir = REPO_ROOT / 'code'
    if code_dir.exists():
        for item in code_dir.rglob('*'):
            if item.is_file() and item.suffix.lower() in TEMPLATE_EXTENSIONS:
                dest = dirs['templates'] / item.name
                if not dest.exists():
                    shutil.move(str(item), str(dest))
                    print(f"  Moved {item.name} from code/ → templates/")


def generate_images_readme():
    """Generate README for images directory"""
    images_dir = REPO_ROOT / 'images'
    if not images_dir.exists():
        return

    readme_content = ["# Images\n"]
    readme_content.append("Preview and links for all image assets.\n\n")

    # Get all image files sorted by name
    image_files = sorted([f for f in images_dir.iterdir() if f.is_file() and is_image(f)])

    for img_file in image_files:
        name = img_file.stem.replace('_', ' ').replace('-', ' ')
        url = get_url(img_file)

        # Add preview for images
        readme_content.append(f"## {name}\n")
        readme_content.append(f'<img src="{img_file.name}" alt="{name}" width="300">\n\n')
        readme_content.append("```text\n")
        readme_content.append(f"{url}\n")
        readme_content.append("```\n\n")

    # Write README
    readme_path = images_dir / 'README.md'
    with open(readme_path, 'w') as f:
        f.write(''.join(readme_content))
    print(f"Generated {readme_path}")

def generate_code_readme():
    """Generate README for code directory"""
    code_dir = REPO_ROOT / 'code'
    if not code_dir.exists():
        return

    readme_content = ["# Code Assets\n"]
    readme_content.append("Links to all code files and stylesheets.\n\n")

    # Walk through code directory
    for root, dirs, files in os.walk(code_dir):
        root_path = Path(root)

        # Skip README files and hidden files
        files = [f for f in files if f != 'README.md' and not f.startswith('.')]

        if not files:
            continue

        # Get relative path for grouping
        rel_path = root_path.relative_to(code_dir)
        if str(rel_path) != '.':
            readme_content.append(f"## {str(rel_path).replace('/', ' - ').title()}\n\n")

        for file in sorted(files):
            file_path = root_path / file
            url = get_url(file_path)
            name = file_path.stem

            readme_content.append(f"### {name}{file_path.suffix}\n")
            readme_content.append("```text\n")
            readme_content.append(f"{url}\n")
            readme_content.append("```\n\n")

    # Write README
    readme_path = code_dir / 'README.md'
    with open(readme_path, 'w') as f:
        f.write(''.join(readme_content))
    print(f"Generated {readme_path}")

def generate_templates_readme():
    """Generate README for templates directory"""
    templates_dir = REPO_ROOT / 'templates'
    if not templates_dir.exists() or not any(templates_dir.iterdir()):
        return

    readme_content = ["# Templates\n"]
    readme_content.append("Handlebars and other template files.\n\n")

    # Get all template files sorted by name
    template_files = sorted([f for f in templates_dir.iterdir() if f.is_file()])

    for template_file in template_files:
        name = template_file.stem.replace('-', ' ').replace('_', ' ').title()
        url = get_url(template_file)

        readme_content.append(f"## {name}\n")
        readme_content.append("```text\n")
        readme_content.append(f"{url}\n")
        readme_content.append("```\n\n")

    # Write README
    readme_path = templates_dir / 'README.md'
    with open(readme_path, 'w') as f:
        f.write(''.join(readme_content))
    print(f"Generated {readme_path}")

def generate_fonts_readme():
    """Generate README for fonts directory"""
    fonts_dir = REPO_ROOT / 'fonts'
    if not fonts_dir.exists() or not any(fonts_dir.iterdir()):
        return

    readme_content = ["# Fonts\n"]
    readme_content.append("Web font files.\n\n")

    # Get all font files sorted by name
    font_files = sorted([f for f in fonts_dir.iterdir() if f.is_file()])

    for font_file in font_files:
        name = font_file.stem
        url = get_url(font_file)

        readme_content.append(f"## {name}\n")
        readme_content.append("```text\n")
        readme_content.append(f"{url}\n")
        readme_content.append("```\n\n")

    # Write README
    readme_path = fonts_dir / 'README.md'
    with open(readme_path, 'w') as f:
        f.write(''.join(readme_content))
    print(f"Generated {readme_path}")

def generate_main_readme():
    """Generate main landing page README"""
    readme_content = ["# Public Assets Repository\n"]
    readme_content.append("\nPublic file hosting for demos and projects.\n\n")
    readme_content.append("## Quick Access\n\n")

    # Add base site
    readme_content.append("### Base Site\n")
    readme_content.append("```text\n")
    readme_content.append(f"{BASE_URL}/\n")
    readme_content.append("```\n\n")

    # Add directory links
    sections = []

    if (REPO_ROOT / 'images').exists():
        sections.append(("Images", "images", "Brand assets, logos, and graphics"))

    if (REPO_ROOT / 'code').exists():
        sections.append(("Code Assets", "code", "CSS, JavaScript, and other code files"))

    if (REPO_ROOT / 'templates').exists():
        sections.append(("Templates", "templates", "Handlebars and HTML templates"))

    if (REPO_ROOT / 'fonts').exists():
        sections.append(("Fonts", "fonts", "Web font files"))

    if sections:
        readme_content.append("## Asset Categories\n\n")
        for title, path, description in sections:
            readme_content.append(f"### [{title}](./{path}/)\n")
            readme_content.append(f"{description}\n\n")

    # Write README
    readme_path = REPO_ROOT / 'README.md'
    with open(readme_path, 'w') as f:
        f.write(''.join(readme_content))
    print(f"Generated {readme_path}")

def find_similar_file(missing_file):
    """Try to find a similar file that exists"""
    missing_path = Path(missing_file)
    filename = missing_path.name

    # Search for files with similar names in the repo
    for existing_file in REPO_ROOT.rglob('*'):
        if existing_file.is_file() and existing_file.name == filename:
            return existing_file

    return None

def review_readme_links():
    """Review all links in READMEs and suggest fixes for broken references"""
    print("Reviewing links in READMEs...")
    print()

    # Pattern to extract URLs from code blocks
    url_pattern = re.compile(r'```text\s*\n\s*' + re.escape(BASE_URL) + r'/(.+?)\s*\n\s*```', re.MULTILINE)

    # Pattern to extract image src references
    img_pattern = re.compile(r'<img src="([^"]+)"')

    # Find all README files
    readme_files = list(REPO_ROOT.rglob('README.md'))

    updates_made = False
    all_changes = []

    for readme_path in readme_files:
        with open(readme_path, 'r') as f:
            content = f.read()

        original_content = content
        changes = []

        # Check URLs in code blocks
        for match in url_pattern.finditer(content):
            url_path = unquote(match.group(1))
            file_path = REPO_ROOT / url_path

            if not file_path.exists():
                similar_file = find_similar_file(file_path)

                if similar_file:
                    suggested_url = get_url(similar_file)
                    current_url = f"{BASE_URL}/{match.group(1)}"

                    changes.append({
                        'type': 'url',
                        'current': current_url,
                        'suggested': suggested_url,
                        'reason': f"File not found: {url_path}\n         Found similar: {similar_file.relative_to(REPO_ROOT)}"
                    })

        # Check image src paths (relative paths in READMEs)
        readme_dir = readme_path.parent
        for match in img_pattern.finditer(content):
            img_src = match.group(1)

            # Skip absolute URLs
            if img_src.startswith('http'):
                continue

            img_path = readme_dir / img_src

            if not img_path.exists():
                similar_file = find_similar_file(img_path)

                if similar_file:
                    # Calculate new relative path
                    try:
                        new_relative = os.path.relpath(similar_file, readme_dir)
                        changes.append({
                            'type': 'img',
                            'current': img_src,
                            'suggested': new_relative,
                            'reason': f"Image not found: {img_src}\n         Found at: {new_relative}"
                        })
                    except ValueError:
                        pass

        # If there are suggested changes, prompt user
        if changes:
            print(f"\n{'='*60}")
            print(f"README: {readme_path.relative_to(REPO_ROOT)}")
            print('='*60)

            applied_changes = []

            for i, change in enumerate(changes, 1):
                print(f"\n[{i}/{len(changes)}] {change['reason']}")
                print(f"\n  Current:   {change['current']}")
                print(f"  Suggested: {change['suggested']}")

                while True:
                    response = input("\n  Apply this change? [y/n/q to quit]: ").lower().strip()

                    if response == 'q':
                        print("\nQuitting review process.")
                        return updates_made

                    if response in ['y', 'n']:
                        break

                    print("  Please enter 'y', 'n', or 'q'")

                if response == 'y':
                    # Apply the change
                    if change['type'] == 'url':
                        old_val = change['current']
                        new_val = change['suggested']
                        content = content.replace(old_val, new_val)
                        print(f"  ✓ Applied: Updated URL")
                        print(f"    FROM: {old_val}")
                        print(f"    TO:   {new_val}")
                        applied_changes.append(f"URL: {old_val} → {new_val}")
                    elif change['type'] == 'img':
                        old_val = change['current']
                        new_val = change['suggested']
                        content = content.replace(f'src="{old_val}"', f'src="{new_val}"')
                        print(f"  ✓ Applied: Updated image path")
                        print(f"    FROM: {old_val}")
                        print(f"    TO:   {new_val}")
                        applied_changes.append(f"Image: {old_val} → {new_val}")

                    updates_made = True
                else:
                    print("  ✗ Skipped")

            # Write updated content if changes were made
            if content != original_content:
                with open(readme_path, 'w') as f:
                    f.write(content)
                print(f"\n{'='*60}")
                print(f"✓ SAVED: {readme_path.relative_to(REPO_ROOT)}")
                print(f"  Changes applied: {len(applied_changes)}")
                for change in applied_changes:
                    print(f"  - {change}")
                print('='*60)

                # Track changes for final summary
                all_changes.append({
                    'readme': readme_path.relative_to(REPO_ROOT),
                    'changes': applied_changes
                })

    if not updates_made:
        print("  All links look good!")
    else:
        # Print final summary
        print(f"\n{'='*60}")
        print("SUMMARY OF ALL CHANGES")
        print('='*60)
        for item in all_changes:
            print(f"\n{item['readme']}:")
            for change in item['changes']:
                print(f"  • {change}")
        print(f"\nTotal READMEs updated: {len(all_changes)}")
        print('='*60)

    return updates_made

def main():
    """Main execution"""
    print("=" * 60)
    print("Repository Organizer")
    print("=" * 60)
    print()

    # Step 1: Review and fix broken links in existing READMEs (before reorganizing)
    print("=" * 60)
    review_readme_links()
    print()

    # Step 2: Organize files
    organize_files()
    print()

    # Step 3: Generate READMEs
    print("Generating READMEs...")
    generate_images_readme()
    generate_code_readme()
    generate_templates_readme()
    generate_fonts_readme()
    generate_main_readme()
    print()

    print("=" * 60)
    print("Done! Repository organized and READMEs generated.")
    print("=" * 60)

if __name__ == '__main__':
    main()
