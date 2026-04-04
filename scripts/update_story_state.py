#!/usr/bin/env python3
import argparse
import json
import re
from pathlib import Path

from inkos_common import iso_now, require_project_markers, write_json


def append_block(path, text):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('a', encoding='utf-8') as f:
        if path.exists() and path.stat().st_size > 0:
            f.write('\n')
        f.write(text.rstrip() + '\n')


def upsert_section(text, heading, body_lines):
    body = '\n'.join(body_lines).strip()
    block = '## %s\n%s\n' % (heading, body)
    pattern = r'(?ms)^##\s+%s\s*$.*?(?=^##\s+|\Z)' % re.escape(heading)
    if re.search(pattern, text):
        updated = re.sub(pattern, block, text, count=1)
    else:
        updated = text.rstrip() + '\n\n' + block if text.strip() else block
    return updated.rstrip() + '\n'


def sync_current_state(path, chapter, title, summary, state_changes):
    path = Path(path)
    text = path.read_text(encoding='utf-8') if path.exists() else ''
    timeline_value = 'ch%s accepted - %s' % (chapter, title)
    text = upsert_section(text, 'Timeline position', ['- %s' % timeline_value])

    latest_update = [
        '- chapter: %s' % chapter,
        '- title: %s' % title,
        '- summary: %s' % summary,
        '- state changes:',
    ]
    if state_changes:
        latest_update.extend(['  - %s' % item for item in state_changes])
    else:
        latest_update.append('  - none')
    text = upsert_section(text, 'Latest accepted update', latest_update)
    path.write_text(text, encoding='utf-8')


def apply_update(project, chapter, title, summary, state_changes, hook_open, hook_advance, hook_close, relationships, emotions):
    project = require_project_markers(project)
    summary_path = project / 'chapter_summaries.md'
    current_state_path = project / 'current_state.md'
    hooks_path = project / 'pending_hooks.md'
    matrix_path = project / 'character_matrix.md'
    emotion_path = project / 'emotional_arcs.md'
    updated_files = []

    chapter_block = [
        '## Chapter %s - %s' % (chapter, title),
        '- Summary: %s' % summary,
    ]

    if state_changes:
        chapter_block.append('- State changes:')
        chapter_block.extend(['  - %s' % x for x in state_changes])
    if hook_open:
        chapter_block.append('- Hooks opened:')
        chapter_block.extend(['  - %s' % x for x in hook_open])
    if hook_advance:
        chapter_block.append('- Hooks advanced:')
        chapter_block.extend(['  - %s' % x for x in hook_advance])
    if hook_close:
        chapter_block.append('- Hooks closed:')
        chapter_block.extend(['  - %s' % x for x in hook_close])
    if relationships:
        chapter_block.append('- Relationship changes:')
        chapter_block.extend(['  - %s' % x for x in relationships])
    if emotions:
        chapter_block.append('- Emotional arc changes:')
        chapter_block.extend(['  - %s' % x for x in emotions])

    append_block(summary_path, '\n'.join(chapter_block))
    updated_files.append(str(summary_path))

    sync_current_state(current_state_path, chapter, title, summary, state_changes)
    updated_files.append(str(current_state_path))

    if hook_open or hook_advance or hook_close:
        for hook in hook_open:
            append_block(hooks_path, '- [OPEN] %s (opened: ch%s)' % (hook, chapter))
        for hook in hook_advance:
            append_block(hooks_path, '- [ADVANCED] %s (updated: ch%s)' % (hook, chapter))
        for hook in hook_close:
            append_block(hooks_path, '- [PAID OFF] %s (closed: ch%s)' % (hook, chapter))
        updated_files.append(str(hooks_path))

    if relationships:
        for rel in relationships:
            append_block(matrix_path, '- %s (updated: ch%s)' % (rel, chapter))
        updated_files.append(str(matrix_path))

    if emotions:
        for emo in emotions:
            append_block(emotion_path, '- %s (updated: ch%s)' % (emo, chapter))
        updated_files.append(str(emotion_path))

    return {
        'schema_version': 'inkos.state-update.v1',
        'tool': 'update_story_state',
        'generated_at': iso_now(),
        'project': str(project),
        'chapter': chapter,
        'title': title,
        'summary': summary,
        'operations': {
            'state_changes': state_changes,
            'hooks_opened': hook_open,
            'hooks_advanced': hook_advance,
            'hooks_closed': hook_close,
            'relationship_changes': relationships,
            'emotion_changes': emotions,
        },
        'updated_files': updated_files,
    }


def main():
    parser = argparse.ArgumentParser(description='Append structured story-state updates.')
    parser.add_argument('--project', required=True)
    parser.add_argument('--chapter', required=True, type=int)
    parser.add_argument('--title', required=True)
    parser.add_argument('--summary', required=True)
    parser.add_argument('--state-change', action='append', default=[])
    parser.add_argument('--hook-open', action='append', default=[])
    parser.add_argument('--hook-advance', action='append', default=[])
    parser.add_argument('--hook-close', action='append', default=[])
    parser.add_argument('--relationship', action='append', default=[])
    parser.add_argument('--emotion', action='append', default=[])
    parser.add_argument('--json', action='store_true', help='Output JSON report.')
    parser.add_argument('--write-report', action='store_true', help='Write JSON report into project/reviews/.')
    args = parser.parse_args()

    report = apply_update(
        args.project,
        args.chapter,
        args.title,
        args.summary,
        args.state_change,
        args.hook_open,
        args.hook_advance,
        args.hook_close,
        args.relationship,
        args.emotion,
    )

    if args.write_report:
        out = Path(args.project) / 'reviews' / ('ch%02d.state-update.json' % args.chapter)
        report['report_path'] = str(out)
        write_json(out, report)

    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print('Updated story state in %s' % args.project)


if __name__ == '__main__':
    main()
