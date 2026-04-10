from bs4 import BeautifulSoup
import re

with open('data.html', 'r', encoding='utf-8') as f:
    soup = BeautifulSoup(f, 'html.parser')

main = soup.find('div', class_='htmlcontent')
if not main:
    raise RuntimeError("Could not find htmlcontent div")

output = []

def get_text(el):
    return el.get_text(separator='', strip=True)

def process(el, depth=0):
    if not hasattr(el, 'name') or el.name is None:
        return

    tag = el.name
    cls = ' '.join(el.get('class', []))

    if tag in ('script', 'style'):
        return

    # Headings by class
    if 'he-h1' in cls:
        text = get_text(el)
        if text:
            output.append(f'\n# {text}\n')
        return
    if 'he-h2' in cls:
        text = get_text(el)
        if text:
            output.append(f'\n## {text}\n')
        return
    if 'he-h3' in cls:
        text = get_text(el)
        if text:
            output.append(f'\n### {text}\n')
        return

    # Table: render as plain text rows
    if tag == 'table':
        for row in el.find_all('tr'):
            cells = [td.get_text(strip=True) for td in row.find_all(['td', 'th'])]
            row_text = '　'.join(cells)
            if row_text.strip():
                output.append(row_text)
        output.append('')
        return

    # Paragraph-level block elements: treat each div/p as its own paragraph
    if tag in ('div', 'p'):
        # Check if it has block children - if so, recurse
        has_block_children = any(
            hasattr(c, 'name') and c.name in ('div', 'p', 'table', 'ul', 'ol', 'li')
            for c in el.children
        )
        if has_block_children:
            for child in el.children:
                process(child, depth + 1)
        else:
            text = get_text(el)
            if text:
                output.append(text)
                output.append('')
        return

    # List items
    if tag in ('ul', 'ol'):
        for li in el.find_all('li', recursive=False):
            text = get_text(li)
            if text:
                output.append(f'- {text}')
        output.append('')
        return

    # Inline elements and others: recurse
    for child in el.children:
        process(child, depth + 1)

process(main)

# Clean up: collapse multiple blank lines
result = []
prev_blank = False
for line in output:
    if line.strip() == '':
        if not prev_blank:
            result.append('')
        prev_blank = True
    else:
        result.append(line)
        prev_blank = False

md_content = '\n'.join(result)

with open('判決書全文.md', 'w', encoding='utf-8') as f:
    f.write(md_content)

print(f"Done. {len(result)} lines, {len(md_content)} chars written to 判決書全文.md")
