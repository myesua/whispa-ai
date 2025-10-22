import re

def extract_title_and_body(markdown_text: str):
    """
    Extracts the first Markdown header (# Heading) as title.
    Returns (title, body).
    """
    match = re.search(r"^#\s+(.+)", markdown_text, re.MULTILINE)
    if match:
        title = match.group(1).strip()
        body = re.sub(r"^#\s+.+\n?", "", markdown_text, count=1).strip()
    else:
        lines = markdown_text.strip().splitlines()
        title = (lines[0][:80] + "...") if lines else "Untitled"
        body = markdown_text
    return title, body
