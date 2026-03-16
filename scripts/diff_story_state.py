#!/usr/bin/env python3
import argparse
import difflib
import json
from pathlib import Path

from inkos_common import iso_now, read_text
from snapshot_story_state import TRACKED_FILES


def resolve_snapshot(project, ref):
    project = Path(project)
    root = project / '.inkos-state' / 'snapshots'
    if ref == 'current':
        return {'kind': 'current', 'id': 'current', 'path': project, 'path_str': str(project)}
    if ref == 'latest':
        if not root.exists():
            raise SystemExit('No snapshots found under %s' % root)
        choices = sorted([p for p in root.iterdir() if p.is_dir()])
        if not choices:
            raise SystemExit('No snapshots found under %s' % root)
        target = choices[-1]
        return {'kind': 'snapshot', 'id': target.name, 'path': target, 'path_str': str(target)}
    path = Path(ref)
    if path.exists():
        return {'kind': 'snapshot', 'id': path.name, 'path': path, 'path_str': str(path)}
    target = root / ref
    if target.exists():
        return {'kind': 'snapshot', 'id': target.name, 'path': target, 'path_str': str(target)}
    raise SystemExit('Snapshot ref not found: %s' % ref)


def load_file(base, rel):
    return read_text(Path(base) / rel)


def diff_report(project, from_ref, to_ref):
    project = Path(project)
    left = resolve_snapshot(project, from_ref)
    right = resolve_snapshot(project, to_ref)

    file_diffs = []
    added_total = 0
    removed_total = 0
    changed = 0

    for rel in TRACKED_FILES:
        before = load_file(left['path'], rel)
        after = load_file(right['path'], rel)
        if before == after:
            continue
        changed += 1
        before_lines = before.splitlines()
        after_lines = after.splitlines()
        udiff = list(difflib.unified_diff(before_lines, after_lines, fromfile='%s:%s' % (left['id'], rel), tofile='%s:%s' % (right['id'], rel), lineterm=''))
        added = sum(1 for line in udiff if line.startswith('+') and not line.startswith('+++'))
        removed = sum(1 for line in udiff if line.startswith('-') and not line.startswith('---'))
        added_total += added
        removed_total += removed
        status = 'changed'
        if not before and after:
            status = 'added'
        elif before and not after:
            status = 'removed'
        file_diffs.append({
            'path': rel,
            'status': status,
            'added_lines': added,
            'removed_lines': removed,
            'diff_excerpt': udiff[:80],
        })

    return {
        'schema_version': 'inkos.state-diff.v1',
        'tool': 'diff_story_state',
        'generated_at': iso_now(),
        'project': str(project),
        'from': {'kind': left['kind'], 'id': left['id'], 'path': left['path_str']},
        'to': {'kind': right['kind'], 'id': right['id'], 'path': right['path_str']},
        'summary': {
            'changed_files': changed,
            'added_lines': added_total,
            'removed_lines': removed_total,
        },
        'file_diffs': file_diffs,
    }


def print_markdown(report):
    print('# Story State Diff')
    print()
    print('## Summary')
    print('- from: %s' % report['from']['id'])
    print('- to: %s' % report['to']['id'])
    print('- changed_files: %s' % report['summary']['changed_files'])
    print('- added_lines: %s' % report['summary']['added_lines'])
    print('- removed_lines: %s' % report['summary']['removed_lines'])
    print()
    print('## File diffs')
    if not report['file_diffs']:
        print('- none')
        return
    for item in report['file_diffs']:
        print('- %s (%s, +%s/-%s)' % (item['path'], item['status'], item['added_lines'], item['removed_lines']))


def main():
    parser = argparse.ArgumentParser(description='Diff story-state snapshots or compare a snapshot to current state.')
    parser.add_argument('--project', required=True)
    parser.add_argument('--from', dest='from_ref', required=True)
    parser.add_argument('--to', dest='to_ref', default='current')
    parser.add_argument('--json', action='store_true')
    args = parser.parse_args()

    report = diff_report(args.project, args.from_ref, args.to_ref)
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print_markdown(report)


if __name__ == '__main__':
    main()
