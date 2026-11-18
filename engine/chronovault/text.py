"""ChronoVault 2.0 — text helpers (stdlib only)."""
from __future__ import annotations

import html
import re
import xml.etree.ElementTree as ET


def clean(text: str) -> str:
    text = html.unescape(text or "")
    text = re.sub(r"<script.*?</script>", " ", text, flags=re.S | re.I)
    text = re.sub(r"<style.*?</style>", " ", text, flags=re.S | re.I)
    text = re.sub(r"<[^>]+>", " ", text)
    return " ".join(text.split())


def shorten(text: str, n: int = 320) -> str:
    text = " ".join((text or "").split())
    if len(text) <= n:
        return text
    cut = text[:n]
    for sep in (". ", "! ", "? ", "; "):
        i = cut.rfind(sep)
        if i > n * 0.55:
            return cut[: i + 1].strip()
    return cut.rsplit(" ", 1)[0] + "…"


def strip_html(text: str) -> str:
    return clean(text)


def parse_rss(xml_text: str, limit: int = 8) -> list[dict]:
    """Parse RSS 2.0 / Atom without third-party libraries."""
    if not xml_text:
        return []
    xml_text = xml_text.strip()
    try:
        root = ET.fromstring(xml_text)
    except Exception:
        # some feeds include leading junk
        i = xml_text.find("<rss")
        j = xml_text.find("<feed")
        start = min([x for x in (i, j) if x >= 0], default=-1)
        if start < 0:
            return []
        try:
            root = ET.fromstring(xml_text[start:])
        except Exception:
            return []

    def local(tag: str) -> str:
        return tag.split("}", 1)[-1].lower()

    items = []
    for el in root.iter():
        if local(el.tag) not in ("item", "entry"):
            continue
        rec = {"title": "", "link": "", "date": "", "summary": "", "source": ""}
        for child in list(el):
            name = local(child.tag)
            val = (child.text or "").strip()
            if name == "title":
                rec["title"] = clean(val)
            elif name == "link":
                rec["link"] = val or child.attrib.get("href", "")
            elif name in ("pubdate", "published", "updated", "date"):
                rec["date"] = val
            elif name in ("description", "summary", "content"):
                rec["summary"] = shorten(clean(val), 200)
            elif name == "source":
                rec["source"] = clean(val)
        if rec["title"]:
            items.append(rec)
        if len(items) >= limit:
            break
    return items


def bullet_list(items: list[str], limit: int = 6) -> str:
    return "\n".join(f"• {x}" for x in items[:limit])


def title_case(s: str) -> str:
    return " ".join(w[:1].upper() + w[1:] for w in s.split())


def looks_roman_urdu(text: str) -> bool:
    words = set(re.findall(r"[a-zA-Z]+", text.lower()))
    markers = {"kya", "hai", "hoga", "kaise", "kaun", "kab", "kahan", "kyun",
               "mujhe", "batao", "bata", "acha", "abhi", "kitna", "kitne",
               "konsa", "konsi", "chahiye", "karo", "kro", "mein", "me", "ka",
               "ki", "ke", "se", "ko", "aur", "nahi", "haan", "theek"}
    return len(words & markers) >= 2
