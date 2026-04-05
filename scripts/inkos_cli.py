#!/usr/bin/env python3
import argparse
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent
PROJECT_ROOT = ROOT.parent
TEMPLATE_DIR = PROJECT_ROOT / 'assets' / 'project-template'


def run(cmd, **kwargs):
    result = subprocess.run(cmd, **kwargs)
    raise SystemExit(result.returncode)


def py(script, args):
    return [sys.executable, str(ROOT / script)] + args


def sh(script, args):
    return ['bash', str(ROOT / script)] + args


def init_project(project, title):
    project = Path(project)
    project.mkdir(parents=True, exist_ok=True)
    shutil.copytree(TEMPLATE_DIR, project, dirs_exist_ok=True)
    (project / 'chapters').mkdir(parents=True, exist_ok=True)
    (project / 'reviews').mkdir(parents=True, exist_ok=True)

    for name in ['README-project.md', 'story_bible.md', 'book_rules.md', 'outline.md', 'current_state.md']:
        path = project / name
        if not path.exists():
            continue
        text = path.read_text(encoding='utf-8')
        path.write_text(text.replace('{{BOOK_TITLE}}', title), encoding='utf-8')

    print('Initialized novel project at: %s' % project)
    print('Title: %s' % title)


def main():
    parser = argparse.ArgumentParser(
        description='Unified CLI entrypoint for inkos-like-novel-os workflows.',
        epilog='Recommended local invocation: python3 scripts/inkos_cli.py <command> ...',
    )
    sub = parser.add_subparsers(dest='command')

    p = sub.add_parser('init', help='Initialize a novel project.')
    p.add_argument('project')
    p.add_argument('title')

    p = sub.add_parser('context', help='Build next-chapter context.')
    p.add_argument('--project', required=True)
    p.add_argument('--recent-chapters', type=int, default=3)
    p.add_argument('--max-chars-per-file', type=int, default=1800)
    p.add_argument('--json', action='store_true')

    p = sub.add_parser('write-next', help='Build a structured write-next packet for the next chapter.')
    p.add_argument('--project', required=True)
    p.add_argument('--chapter', type=int)
    p.add_argument('--recent-chapters', type=int, default=3)
    p.add_argument('--max-chars-per-file', type=int, default=1800)
    p.add_argument('--json', action='store_true')
    p.add_argument('--write-report', action='store_true')

    p = sub.add_parser('audit', help='Audit a chapter.')
    p.add_argument('--project', required=True)
    p.add_argument('--chapter-file', required=True)
    p.add_argument('--json', action='store_true')
    p.add_argument('--write-report', action='store_true')

    p = sub.add_parser('knowledge-check', help='Check chapter knowledge boundaries and POV leaks.')
    p.add_argument('--project', required=True)
    p.add_argument('--chapter-file', required=True)
    p.add_argument('--json', action='store_true')

    p = sub.add_parser('extract-state', help='Extract candidate state updates from a chapter draft.')
    p.add_argument('--project', required=True)
    p.add_argument('--chapter-file', required=True)
    p.add_argument('--json', action='store_true')

    p = sub.add_parser('hook-report', help='Summarize hook lifecycle status.')
    p.add_argument('--project', required=True)
    p.add_argument('--stale-after', type=int, default=5)
    p.add_argument('--json', action='store_true')

    p = sub.add_parser('state-update', help='Append story-state updates.')
    p.add_argument('--project', required=True)
    p.add_argument('--chapter', required=True)
    p.add_argument('--title', required=True)
    p.add_argument('--summary', required=True)
    p.add_argument('--state-change', action='append', default=[])
    p.add_argument('--hook-open', action='append', default=[])
    p.add_argument('--hook-advance', action='append', default=[])
    p.add_argument('--hook-close', action='append', default=[])
    p.add_argument('--relationship', action='append', default=[])
    p.add_argument('--emotion', action='append', default=[])
    p.add_argument('--json', action='store_true')
    p.add_argument('--write-report', action='store_true')

    p = sub.add_parser('revision-plan', help='Build a revision plan from an audit or chapter file.')
    p.add_argument('--project')
    p.add_argument('--chapter-file')
    p.add_argument('--audit-report')
    p.add_argument('--json', action='store_true')
    p.add_argument('--write-report', action='store_true')

    p = sub.add_parser('spot-fixes', help='Suggest low-risk spot fixes from an audit or chapter file.')
    p.add_argument('--project')
    p.add_argument('--chapter-file')
    p.add_argument('--audit-report')
    p.add_argument('--json', action='store_true')
    p.add_argument('--write-report', action='store_true')

    p = sub.add_parser('revise', help='Run knowledge-check, audit, revision-plan, and spot-fixes as one workflow.')
    p.add_argument('--project', required=True)
    p.add_argument('--chapter-file', required=True)
    p.add_argument('--skip-knowledge-check', action='store_true')
    p.add_argument('--json', action='store_true')
    p.add_argument('--write-report', action='store_true')

    p = sub.add_parser('snapshot', help='Create a versioned story-state snapshot.')
    p.add_argument('--project', required=True)
    p.add_argument('--label')
    p.add_argument('--chapter', type=int)
    p.add_argument('--notes')
    p.add_argument('--json', action='store_true')

    p = sub.add_parser('diff', help='Diff story-state snapshots or current state.')
    p.add_argument('--project', required=True)
    p.add_argument('--from', dest='from_ref', required=True)
    p.add_argument('--to', dest='to_ref', default='current')
    p.add_argument('--json', action='store_true')

    p = sub.add_parser('package', help='Package the skill into a .skill zip (and a versioned copy when VERSION exists).')
    p.add_argument('outdir', nargs='?', default='')
    p.add_argument('version_suffix', nargs='?', default='')

    sub.add_parser('smoke-test', help='Run smoke tests.')

    args = parser.parse_args()

    if args.command == 'init':
        init_project(args.project, args.title)
    elif args.command == 'context':
        if args.recent_chapters < 0:
            raise SystemExit('--recent-chapters must be >= 0')
        if args.max_chars_per_file < 0:
            raise SystemExit('--max-chars-per-file must be >= 0')
        cmd = py('build_next_chapter_context.py', ['--project', args.project, '--recent-chapters', str(args.recent_chapters), '--max-chars-per-file', str(args.max_chars_per_file)])
        if args.json:
            cmd.append('--json')
        run(cmd)
    elif args.command == 'write-next':
        if args.recent_chapters < 0:
            raise SystemExit('--recent-chapters must be >= 0')
        if args.max_chars_per_file < 0:
            raise SystemExit('--max-chars-per-file must be >= 0')
        cmd = py('build_write_next_packet.py', ['--project', args.project, '--recent-chapters', str(args.recent_chapters), '--max-chars-per-file', str(args.max_chars_per_file)])
        if args.chapter is not None:
            cmd.extend(['--chapter', str(args.chapter)])
        if args.json:
            cmd.append('--json')
        if args.write_report:
            cmd.append('--write-report')
        run(cmd)
    elif args.command == 'audit':
        cmd = py('audit_chapter.py', ['--project', args.project, '--chapter-file', args.chapter_file])
        if args.json:
            cmd.append('--json')
        if args.write_report:
            cmd.append('--write-report')
        run(cmd)
    elif args.command == 'knowledge-check':
        cmd = py('knowledge_check.py', ['--project', args.project, '--chapter-file', args.chapter_file])
        if args.json:
            cmd.append('--json')
        run(cmd)
    elif args.command == 'extract-state':
        cmd = py('extract_state.py', ['--project', args.project, '--chapter-file', args.chapter_file])
        if args.json:
            cmd.append('--json')
        run(cmd)
    elif args.command == 'hook-report':
        if args.stale_after < 0:
            raise SystemExit('--stale-after must be >= 0')
        cmd = py('hook_report.py', ['--project', args.project, '--stale-after', str(args.stale_after)])
        if args.json:
            cmd.append('--json')
        run(cmd)
    elif args.command == 'state-update':
        cmd = py('update_story_state.py', ['--project', args.project, '--chapter', str(args.chapter), '--title', args.title, '--summary', args.summary])
        for item in args.state_change:
            cmd.extend(['--state-change', item])
        for item in args.hook_open:
            cmd.extend(['--hook-open', item])
        for item in args.hook_advance:
            cmd.extend(['--hook-advance', item])
        for item in args.hook_close:
            cmd.extend(['--hook-close', item])
        for item in args.relationship:
            cmd.extend(['--relationship', item])
        for item in args.emotion:
            cmd.extend(['--emotion', item])
        if args.json:
            cmd.append('--json')
        if args.write_report:
            cmd.append('--write-report')
        run(cmd)
    elif args.command == 'revision-plan':
        cmd = py('build_revision_plan.py', [])
        if args.project:
            cmd.extend(['--project', args.project])
        if args.chapter_file:
            cmd.extend(['--chapter-file', args.chapter_file])
        if args.audit_report:
            cmd.extend(['--audit-report', args.audit_report])
        if args.json:
            cmd.append('--json')
        if args.write_report:
            cmd.append('--write-report')
        run(cmd)
    elif args.command == 'spot-fixes':
        cmd = py('suggest_spot_fixes.py', [])
        if args.project:
            cmd.extend(['--project', args.project])
        if args.chapter_file:
            cmd.extend(['--chapter-file', args.chapter_file])
        if args.audit_report:
            cmd.extend(['--audit-report', args.audit_report])
        if args.json:
            cmd.append('--json')
        if args.write_report:
            cmd.append('--write-report')
        run(cmd)
    elif args.command == 'revise':
        cmd = py('run_revision_cycle.py', ['--project', args.project, '--chapter-file', args.chapter_file])
        if args.skip_knowledge_check:
            cmd.append('--skip-knowledge-check')
        if args.json:
            cmd.append('--json')
        if args.write_report:
            cmd.append('--write-report')
        run(cmd)
    elif args.command == 'snapshot':
        cmd = py('snapshot_story_state.py', ['--project', args.project])
        if args.label:
            cmd.extend(['--label', args.label])
        if args.chapter is not None:
            cmd.extend(['--chapter', str(args.chapter)])
        if args.notes:
            cmd.extend(['--notes', args.notes])
        if args.json:
            cmd.append('--json')
        run(cmd)
    elif args.command == 'diff':
        cmd = py('diff_story_state.py', ['--project', args.project, '--from', args.from_ref, '--to', args.to_ref])
        if args.json:
            cmd.append('--json')
        run(cmd)
    elif args.command == 'package':
        cmd = py('package_skill.py', [])
        if args.outdir:
            cmd.append(args.outdir)
        if args.version_suffix:
            cmd.append(args.version_suffix)
        run(cmd)
    elif args.command == 'smoke-test':
        run(py('smoke_test.py', ['--invoked-by-cli']))
    else:
        parser.print_help()
        raise SystemExit(1)


if __name__ == '__main__':
    main()
