"""Link handling. In templates, write links either as [Label](https://url) or as a bare https://url."""
import html
import re

TOKEN = re.compile(r"\[([^\]]+)\]\((https?://[^\s)]+)\)|(https?://[^\s<>\"]+)")
_TRAIL = ".,;:!?)"

def extract_urls(text: str) -> list[str]:
    urls = []
    for m in TOKEN.finditer(text):
        urls.append(m.group(2) if m.group(2) else m.group(3).rstrip(_TRAIL))
    return list(dict.fromkeys(urls))

def missing_links(template: str, draft: str) -> list[str]:
    """URLs present in the template but absent (or altered) in the draft."""
    return [u for u in extract_urls(template) if u not in draft]

def to_plain(text: str) -> str:
    """Plain-text version: [Label](url) -> 'Label: url'."""
    return TOKEN.sub(lambda m: f"{m.group(1)}: {m.group(2)}" if m.group(2) else m.group(0), text)

def _inline(text: str) -> str:
    out, pos = [], 0
    for m in TOKEN.finditer(text):
        out.append(html.escape(text[pos:m.start()], quote=False))
        if m.group(2):
            label, url, trail = m.group(1), m.group(2), ""
        else:
            raw = m.group(3)
            url = raw.rstrip(_TRAIL)
            trail, label = raw[len(url):], url
        out.append(f'<a href="{html.escape(url)}">{html.escape(label)}</a>{html.escape(trail, quote=False)}')
        pos = m.end()
    out.append(html.escape(text[pos:], quote=False))
    return "".join(out)

def to_html(text: str) -> str:
    paras = re.split(r"\n\s*\n", text.strip())
    body = "".join(f"<p>{_inline(p).replace(chr(10), '<br>')}</p>" for p in paras)
    return ('<div style="font-family:Arial,Helvetica,sans-serif;font-size:15px;'
            f'line-height:1.5;color:#222">{body}</div>')
