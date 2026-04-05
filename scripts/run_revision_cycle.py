#!/usr/bin/env python3
import argparse
import json
from pathlib import Path

from audit_chapter import build_report as build_audit_report
from build_revision_plan import build_plan
from hook_report import build_report as build_hook_report
from inkos_common import iso_now, write_json
from knowledge_check import build_report as build_knowledge_report
from suggest_spot_fixes import build_suggestions


def overall_status(knowledge_report, audit_report):
    knowledge_counts = knowledge_report['summary']['counts']
    audit_counts = audit_report['summary']['counts']
    if knowledge_counts['critical'] or knowledge_counts['major']:
        return 'block'
    if audit_counts['critical']:
        return 'block'
    if audit_counts['major']:
        return 'revise'
    return 'pass'


def build_cycle(project, chapter_file, run_knowledge_check=True):
    knowledge_report = build_knowledge_report(project, chapter_file) if run_knowledge_check else None
    audit_report = build_audit_report(project, chapter_file)
    revision_plan = build_plan(project, chapter_file, None)
    spot_fixes = build_suggestions(project, chapter_file, None)
    hook_report = build_hook_report(project, stale_after=5)

    status = overall_status(
        knowledge_report or {'summary': {'counts': {'critical': 0, 'major': 0}}},
        audit_report,
    )
    blocking_items = 0
    if knowledge_report:
        blocking_items += knowledge_report['summary']['counts']['critical'] + knowledge_report['summary']['counts']['major']
    blocking_items += audit_report['summary']['counts']['critical'] + audit_report['summary']['counts']['major']

    return {
        'schema_version': 'inkos.revision-cycle.v1',
        'tool': 'run_revision_cycle',
        'generated_at': iso_now(),
        'project': str(project),
        'chapter': str(chapter_file),
        'status': status,
        'summary': {
            'knowledge_check_run': run_knowledge_check,
            'blocking_item_count': blocking_items,
            'audit_overall': audit_report['overall'],
            'spot_fix_count': spot_fixes['summary']['suggestion_count'],
            'human_review_needed': revision_plan['summary']['human_review_needed'],
            'stale_hook_count': hook_report['summary']['stale_hook_count'],
        },
        'recommended_sequence': [
            '先修 knowledge-boundary 和 audit 里的 critical / major 问题。',
            '再按 revision_plan 处理 scene-level 或 local-level 修订。',
            '最后应用 spot-fixes，并在接受后更新 truth files。',
        ],
        'hook_pressure': hook_report,
        'knowledge_check': knowledge_report,
        'audit': audit_report,
        'revision_plan': revision_plan,
        'spot_fixes': spot_fixes,
    }


def print_markdown(data):
    print('# Revision Cycle')
    print()
    print('- status: %s' % data['status'])
    print('- audit_overall: %s' % data['summary']['audit_overall'])
    print('- blocking_item_count: %s' % data['summary']['blocking_item_count'])
    print('- human_review_needed: %s' % data['summary']['human_review_needed'])
    print('- stale_hook_count: %s' % data['summary']['stale_hook_count'])
    print()

    if data['knowledge_check']:
        print('## Knowledge Check')
        print('- ok: %s' % ('yes' if data['knowledge_check']['ok'] else 'no'))
        print('- violations: %s' % data['knowledge_check']['summary']['violation_count'])
        print()

    print('## Minimal Fix Plan')
    for item in data['revision_plan']['minimal_fix_plan']:
        print('- %s' % item)
    print()

    print('## Spot Fixes')
    if not data['spot_fixes']['suggestions']:
        print('- none')
    else:
        for item in data['spot_fixes']['suggestions']:
            print('- [%s/%s] %s' % (item['suggestion_id'], item['rule_id'], item['suggested_action']))
    print()

    print('## Hook Pressure')
    if not data['hook_pressure']['stale_hooks']:
        print('- no stale hooks')
    else:
        for item in data['hook_pressure']['stale_hooks']:
            print('- [%s] %s' % (item['status'] if 'status' in item else 'stale', item['hook']))


def main():
    parser = argparse.ArgumentParser(description='Run a full revision cycle for a chapter draft.')
    parser.add_argument('--project', required=True)
    parser.add_argument('--chapter-file', required=True)
    parser.add_argument('--skip-knowledge-check', action='store_true')
    parser.add_argument('--json', action='store_true')
    parser.add_argument('--write-report', action='store_true')
    args = parser.parse_args()

    data = build_cycle(args.project, args.chapter_file, run_knowledge_check=not args.skip_knowledge_check)

    if args.write_report:
        chapter_stem = Path(args.chapter_file).stem
        out = Path(args.project) / 'reviews' / ('%s.revision-cycle.json' % chapter_stem)
        data['report_path'] = str(out)
        write_json(out, data)

    if args.json:
        print(json.dumps(data, ensure_ascii=False, indent=2))
    else:
        print_markdown(data)


if __name__ == '__main__':
    main()
