#!/usr/bin/env python3
import argparse
import json
from pathlib import Path

from inkos_common import CHAPTER_HEADING_RE, iso_now, limit_chars, latest_sections, read_text, require_project_markers

FILES = [
    'story_bible.md',
    'book_rules.md',
    'outline.md',
    'current_state.md',
    'chapter_summaries.md',
    'pending_hooks.md',
    'character_matrix.md',
    'emotional_arcs.md',
    'subplot_board.md',
    'style_guide.md',
]


def build_context_report(project, recent_chapters, max_chars_per_file):
    project = require_project_markers(project)
    sections = {}
    section_meta = {}

    for name in FILES:
        text = read_text(project / name)
        if not text:
            continue
        original_chars = len(text.strip())
        if name == 'chapter_summaries.md':
            text = latest_sections(text, CHAPTER_HEADING_RE, recent_chapters, max_chars=max_chars_per_file)
        else:
            text = limit_chars(text, max_chars_per_file)
        sections[name] = text.strip()
        section_meta[name] = {
            'chars': len(sections[name]),
            'truncated': len(sections[name]) < original_chars,
        }

    prompt = []
    prompt.append('# Next Chapter Context')
    prompt.append('')
    prompt.append('Use this context to plan and draft the next chapter. Preserve continuity, character locks, world rules, and hook discipline.')
    prompt.append('')
    for name in FILES:
        if name not in sections:
            continue
        prompt.append('## %s' % name)
        prompt.append(sections[name])
        prompt.append('')

    prompt.append('## Writing instructions')
    prompt.append('- State the chapter function before drafting.')
    prompt.append('- Advance at least one active hook unless the chapter is deliberately transitional.')
    prompt.append('- Respect information boundaries: do not let characters know what they should not know.')
    prompt.append('- Prefer spot-fixable prose over risky structural overreach.')
    prompt.append('- After acceptance, update chapter_summaries, current_state, pending_hooks, and relationship/emotion files.')

    return {
        'schema_version': 'inkos.next-context.v1',
        'tool': 'build_next_chapter_context',
        'generated_at': iso_now(),
        'project': str(project),
        'config': {
            'recent_chapters': recent_chapters,
            'max_chars_per_file': max_chars_per_file,
        },
        'files_loaded': list(sections.keys()),
        'summary': {
            'section_count': len(sections),
            'context_chars': len('\n'.join(prompt).strip()),
        },
        'section_meta': section_meta,
        'sections': sections,
        'context': '\n'.join(prompt).strip() + '\n',
    }


def main():
    parser = argparse.ArgumentParser(description='Build a compact next-chapter context from truth files.')
    parser.add_argument('--project', required=True)
    parser.add_argument('--recent-chapters', type=int, default=3)
    parser.add_argument('--max-chars-per-file', type=int, default=1800)
    parser.add_argument('--json', action='store_true')
    args = parser.parse_args()

    if args.recent_chapters < 0:
        raise SystemExit('--recent-chapters must be >= 0')
    if args.max_chars_per_file < 0:
        raise SystemExit('--max-chars-per-file must be >= 0')

    report = build_context_report(args.project, args.recent_chapters, args.max_chars_per_file)

    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(report['context'])


if __name__ == '__main__':
    main()
