#!/usr/bin/env python3
import json
import re
from datetime import datetime
from pathlib import Path


def iso_now():
    return datetime.utcnow().replace(microsecond=0).isoformat() + 'Z'


def read_text(path):
    path = Path(path)
    return path.read_text(encoding='utf-8') if path.exists() else ''


def write_json(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def limit_chars(text, max_chars):
    text = (text or '').strip()
    if len(text) <= max_chars:
        return text
    return text[: max_chars - 20].rstrip() + '\n...[truncated]'


def chapter_sections(text, heading_re):
    matches = list(re.finditer(heading_re, text or '', flags=re.M))
    if not matches:
        return []
    sections = []
    for i, match in enumerate(matches):
        start = match.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        sections.append((match.group(0), text[start:end].strip()))
    return sections


def latest_sections(markdown, heading_re, count):
    sections = chapter_sections(markdown, heading_re)
    if not sections:
        return limit_chars(markdown, 2000)
    return '\n\n'.join(section for _heading, section in sections[-count:])


def extract_bullets(text):
    return [m.group(1).strip() for m in re.finditer(r'^-\s+(.+)$', text or '', flags=re.M)]


def extract_keywords(text, min_len=2, limit=None):
    words = re.findall(r'[\u4e00-\u9fffA-Za-z]{%d,}' % min_len, text or '')
    out = []
    seen = set()
    for word in words:
        if word in seen:
            continue
        seen.add(word)
        out.append(word)
        if limit and len(out) >= limit:
            break
    return out
