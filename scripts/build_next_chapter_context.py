#!/usr/bin/env python3
import argparse
import json
import re
from pathlib import Path

FILES = [
    "story_bible.md",
    "book_rules.md",
    "outline.md",
    "current_state.md",
    "chapter_summaries.md",
    "pending_hooks.md",
    "character_matrix.md",
    "emotional_arcs.md",
    "subplot_board.md",
    "style_guide.md",
]


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def limit_chars(text: str, max_chars: int) -> str:
    text = text.strip()
    if len(text) <= max_chars:
        return text
    return text[: max_chars - 20].rstrip() + "\n...[truncated]"


def latest_sections(markdown: str, heading_re: str, count: int) -> str:
    parts = re.split(heading_re, markdown, flags=re.M)
    headers = re.findall(heading_re, markdown, flags=re.M)
    if not headers:
        return limit_chars(markdown, 2000)
    sections = []
    for i, body in enumerate(parts[1:]):
        sections.append(headers[i] + body)
    return "\n\n".join(s.strip() for s in sections[-count:])


def main():
    parser = argparse.ArgumentParser(description="Build a compact next-chapter context from truth files.")
    parser.add_argument("--project", required=True)
    parser.add_argument("--recent-chapters", type=int, default=3)
    parser.add_argument("--max-chars-per-file", type=int, default=1800)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    project = Path(args.project)
    sections = {}

    for name in FILES:
        text = read_text(project / name)
        if not text:
            continue
        if name == "chapter_summaries.md":
            text = latest_sections(text, r"^##\s+Chapter\s+\d+.*$", args.recent_chapters)
        else:
            text = limit_chars(text, args.max_chars_per_file)
        sections[name] = text.strip()

    prompt = []
    prompt.append("# Next Chapter Context")
    prompt.append("")
    prompt.append("Use this context to plan and draft the next chapter. Preserve continuity, character locks, world rules, and hook discipline.")
    prompt.append("")
    order = [
        "story_bible.md",
        "book_rules.md",
        "outline.md",
        "current_state.md",
        "chapter_summaries.md",
        "pending_hooks.md",
        "character_matrix.md",
        "emotional_arcs.md",
        "subplot_board.md",
        "style_guide.md",
    ]
    for name in order:
        if name not in sections:
            continue
        prompt.append(f"## {name}")
        prompt.append(sections[name])
        prompt.append("")

    prompt.append("## Writing instructions")
    prompt.append("- State the chapter function before drafting.")
    prompt.append("- Advance at least one active hook unless the chapter is deliberately transitional.")
    prompt.append("- Respect information boundaries: do not let characters know what they should not know.")
    prompt.append("- Prefer spot-fixable prose over risky structural overreach.")
    prompt.append("- After acceptance, update chapter_summaries, current_state, pending_hooks, and relationship/emotion files.")

    result = {
        "project": str(project),
        "sections": sections,
        "context": "\n".join(prompt).strip() + "\n",
    }

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(result["context"])


if __name__ == "__main__":
    main()
