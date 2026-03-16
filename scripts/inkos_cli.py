#!/usr/bin/env python3
import argparse
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent


def run(cmd):
    result = subprocess.run(cmd)
    raise SystemExit(result.returncode)


def py(script, args):
    return [sys.executable, str(ROOT / script)] + args


def sh(script, args):
    return ['bash', str(ROOT / script)] + args


def main():
    parser = argparse.ArgumentParser(description='Lightweight CLI for inkos-like-novel-os workflows.')
    sub = parser.add_subparsers(dest='command')

    p = sub.add_parser('init', help='Initialize a novel project.')
    p.add_argument('project')
    p.add_argument('title')

    p = sub.add_parser('context', help='Build next-chapter context.')
    p.add_argument('--project', required=True)
    p.add_argument('--recent-chapters', type=int, default=3)
    p.add_argument('--max-chars-per-file', type=int, default=1800)
    p.add_argument('--json', action='store_true')

    p = sub.add_parser('audit', help='Audit a chapter.')
    p.add_argument('--project', required=True)
    p.add_argument('--chapter-file', required=True)
    p.add_argument('--json', action='store_true')
    p.add_argument('--write-report', action='store_true')

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

    p = sub.add_parser('package', help='Package the skill into a .skill zip.')
    p.add_argument('outdir', nargs='?', default='')
    p.add_argument('version_suffix', nargs='?', default='')

    sub.add_parser('smoke-test', help='Run smoke tests.')

    args = parser.parse_args()

    if args.command == 'init':
        run(sh('init_novel_project.sh', [args.project, args.title]))
    elif args.command == 'context':
        cmd = py('build_next_chapter_context.py', ['--project', args.project, '--recent-chapters', str(args.recent_chapters), '--max-chars-per-file', str(args.max_chars_per_file)])
        if args.json:
            cmd.append('--json')
        run(cmd)
    elif args.command == 'audit':
        cmd = py('audit_chapter.py', ['--project', args.project, '--chapter-file', args.chapter_file])
        if args.json:
            cmd.append('--json')
        if args.write_report:
            cmd.append('--write-report')
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
    elif args.command == 'package':
        extra = []
        if args.outdir:
            extra.append(args.outdir)
        if args.version_suffix:
            extra.append(args.version_suffix)
        run(sh('package_skill.sh', extra))
    elif args.command == 'smoke-test':
        run(sh('smoke_test.sh', []))
    else:
        parser.print_help()
        raise SystemExit(1)


if __name__ == '__main__':
    main()
