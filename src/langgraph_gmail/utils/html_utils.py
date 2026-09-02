from html.parser import HTMLParser
import re

# Only tags that always carry a closing tag; void tags would leak the skip counter.
_SKIP_TAGS = {'script', 'style', 'title'}
_BLOCK_TAGS = {
    'p', 'div', 'br', 'tr', 'td', 'th', 'li', 'ul', 'ol', 'table',
    'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'section', 'article',
}


class _TextExtractor(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self._chunks: list[str] = []
        self._skip_depth = 0

    def handle_starttag(self, tag, attrs):
        if tag in _SKIP_TAGS:
            self._skip_depth += 1
        elif tag in _BLOCK_TAGS:
            self._chunks.append('\n')

    def handle_endtag(self, tag):
        if tag in _SKIP_TAGS and self._skip_depth:
            self._skip_depth -= 1
        elif tag in _BLOCK_TAGS:
            self._chunks.append('\n')

    def handle_data(self, data):
        if not self._skip_depth:
            self._chunks.append(data)

    def get_text(self) -> str:
        return ''.join(self._chunks)


def html_to_text(html: str) -> str:
    """Convert an HTML email body into readable plain text."""
    parser = _TextExtractor()
    try:
        parser.feed(html)
        parser.close()
        text = parser.get_text()
    except Exception:
        text = re.sub(r'<[^>]+>', ' ', html)

    # Collapse spaces/tabs, then collapse runs of blank lines.
    text = re.sub(r'[ \t\r\f\v]+', ' ', text)
    text = re.sub(r' *\n *', '\n', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()
