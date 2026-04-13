#!/usr/bin/env python3
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

from inkos_common import configure_stdio_utf8

ROOT = Path(__file__).resolve().parent.parent
CLI = ROOT / 'scripts' / 'inkos_cli.py'
PYTHON = sys.executable

configure_stdio_utf8()


def run_cli(*args, check=True, capture_output=True, text=True, cwd=None):
    env = dict(os.environ)
    env['PYTHONUTF8'] = '1'
    return subprocess.run(
        [PYTHON, str(CLI), *args],
        check=check,
        capture_output=capture_output,
        text=text,
        encoding='utf-8',
        errors='replace',
        cwd=cwd or str(ROOT),
        env=env,
    )


def run_script(script_name, *args):
    env = dict(os.environ)
    env['PYTHONUTF8'] = '1'
    return subprocess.run(
        [PYTHON, str(ROOT / 'scripts' / script_name), *args],
        check=True,
        capture_output=True,
        text=True,
        encoding='utf-8',
        errors='replace',
        cwd=str(ROOT),
        env=env,
    )


def assert_contains(path, needle):
    text = Path(path).read_text(encoding='utf-8')
    if needle not in text:
        raise AssertionError(f'{needle!r} not found in {path}')
    if '{{BOOK_TITLE}}' in text:
        raise AssertionError(f'placeholder not replaced in {path}')

def main():
    invoked_by_cli = '--invoked-by-cli' in sys.argv[1:]
    tmp = ROOT / '.smoke-work'
    shutil.rmtree(tmp, ignore_errors=True)
    tmp.mkdir(parents=True, exist_ok=True)
    try:
        project = tmp / 'demo-novel'

        print('===== cli init regression =====')
        init_result = run_cli('init', str(project), '测试长篇', check=False)
        if init_result.returncode != 0:
            raise SystemExit(init_result.stderr.strip() or init_result.stdout.strip() or 'cli init failed')
        for rel in ['README-project.md', 'story_bible.md', 'book_rules.md', 'outline.md', 'current_state.md']:
            if not (project / rel).exists():
                raise AssertionError(f'missing initialized file: {rel}')
        print('cli init ok')

        print('===== init title escaping regression =====')
        special_project = tmp / 'special-title-novel'
        special_title = 'A&B/测试'
        run_cli('init', str(special_project), special_title)
        for rel in ['README-project.md', 'story_bible.md', 'book_rules.md', 'outline.md', 'current_state.md']:
            assert_contains(special_project / rel, special_title)
        print('init title escaping ok')

        (project / 'current_state.md').write_text(
            """# Current State — 测试长篇

## Timeline position
- ch1 aftermath

## Major character states
- 林烬正在调查玉佩异常。

## Relationships
- 林烬对徐安保持表面合作。

## Open conflicts
- 玉佩是否被调包。

## Active resources / items
- 玉佩

## Facts
- 玉佩已经被人动过手脚。

## Character beliefs
- 林烬：不知道真正的替换者是谁。
- 徐安：不知道林烬已经开始怀疑自己。

## Immediate next pressure
- 林烬必须确认谁先碰过玉佩。
""",
            encoding='utf-8',
        )
        (project / 'character_knowledge.md').write_text(
            """# Character Knowledge

## 林烬
- knows: 玉佩有异常
- suspects: 徐安可能隐瞒线索
- does not know: 真正的替换者身份
- wrong beliefs: 暂无
""",
            encoding='utf-8',
        )
        (project / 'chapters' / 'ch01.md').write_text(
            """# Chapter 1

林烬推开旧库房的门时，先闻到一股潮木味，像是很多年前被封住的雨水。

桌上的玉佩安静地躺在布包里，颜色、纹路、缺口都和记忆里一样，可他摸上去时，指腹却迟疑了一瞬。

太新了。

不是表面的光，而是一种不该存在的完整感。真正跟了徐家十几年的东西，不会在边角处毫无磨痕。

“你在看什么？”徐安站在门边，语气平静。

林烬把玉佩收回掌心，没有立刻抬头：“我在想，谁有机会先碰到它。”

徐安没有接话。库房外风声掠过窗纸，像有人在暗处轻轻笑了一下。
""",
            encoding='utf-8',
        )

        print('===== build_next_chapter_context =====')
        run_script('build_next_chapter_context.py', '--project', str(project))
        print('context build ok')

        print('===== single chapter context regression =====')
        (project / 'outline.md').write_text(
            """# Outline — 测试长篇

## Chapter targets
- ch1: 第一章目标
- ch2: 第二章目标
- ch3: 第三章目标
- ch4: 第四章目标
- ch5: 第五章目标
""",
            encoding='utf-8',
        )
        context_data = json.loads(run_cli('context', '--project', str(project), '--chapter', '2', '--json').stdout)
        if context_data['target_chapter'] != 2:
            raise AssertionError('context target_chapter mismatch')
        if 'Draft exactly one chapter only: chapter 2.' not in context_data['single_chapter_contract']:
            raise AssertionError('context missing single-chapter contract')
        if 'ch2: 第二章目标' not in context_data['sections'].get('outline.md', ''):
            raise AssertionError('context missing target outline excerpt')
        if 'ch4: 第四章目标' in context_data['sections'].get('outline.md', ''):
            raise AssertionError('context leaked too many chapter targets')
        print('single chapter context ok')

        print('===== audit_chapter =====')
        run_script('audit_chapter.py', '--project', str(project), '--chapter-file', str(project / 'chapters' / 'ch01.md'), '--json')
        print('chapter audit ok')

        print('===== update_story_state =====')
        state_update = run_script(
            'update_story_state.py',
            '--project',
            str(project),
            '--chapter',
            '1',
            '--title',
            '第一章',
            '--summary',
            '林烬察觉玉佩疑似被调包，并开始怀疑有人提前动过手脚。',
            '--state-change',
            '林烬确认手中的玉佩手感异常，怀疑其并非原物。',
            '--hook-open',
            '是谁在林烬之前碰过玉佩',
            '--relationship',
            '林烬 -> 徐安：出现试探与怀疑',
            '--emotion',
            '林烬：警觉上升',
            '--json',
        )
        state_data = json.loads(state_update.stdout)
        for expected in ['chapter_summaries.md', 'current_state.md', 'pending_hooks.md', 'character_matrix.md', 'emotional_arcs.md']:
            if not any(path.endswith(expected) for path in state_data['updated_files']):
                raise AssertionError(f'missing updated file: {expected}')
        current_state_text = (project / 'current_state.md').read_text(encoding='utf-8')
        if 'chapter: 1' not in current_state_text:
            raise AssertionError('current_state missing latest accepted update chapter marker')
        if 'summary: 林烬察觉玉佩疑似被调包，并开始怀疑有人提前动过手脚。' not in current_state_text:
            raise AssertionError('current_state missing synced summary')
        if '林烬确认手中的玉佩手感异常，怀疑其并非原物。' not in current_state_text:
            raise AssertionError('current_state missing synced state change')
        print('story state update ok')

        print('===== write-next entrypoint =====')
        write_next = run_cli('write-next', '--project', str(project), '--json', check=False)
        if write_next.returncode != 0:
            raise SystemExit(write_next.stderr.strip() or write_next.stdout.strip() or 'cli write-next failed')
        write_next_data = json.loads(write_next.stdout)
        if write_next_data['schema_version'] != 'inkos.write-next.v1':
            raise AssertionError('write-next schema mismatch')
        if write_next_data['chapter'] != 2:
            raise AssertionError(f'write-next chapter mismatch: {write_next_data["chapter"]}')
        if not write_next_data['chapter_function']['primary_goal']:
            raise AssertionError('write-next missing primary goal')
        if not write_next_data['suggested_scene_beats']:
            raise AssertionError('write-next missing scene beats')
        if not write_next_data['chapter_file_hint'].endswith('ch02.md'):
            raise AssertionError('write-next missing chapter file hint')
        if 'Primary goal' not in write_next_data['plan_template']:
            raise AssertionError('write-next missing plan template')
        if not any('只输出第 2 章正文。' == item for item in write_next_data['single_chapter_contract']):
            raise AssertionError('write-next missing single chapter contract')
        write_next_report = run_cli('write-next', '--project', str(project), '--json', '--write-report', check=False)
        if write_next_report.returncode != 0:
            raise SystemExit(write_next_report.stderr.strip() or write_next_report.stdout.strip() or 'cli write-next write-report failed')
        write_next_report_data = json.loads(write_next_report.stdout)
        if not write_next_report_data.get('report_path'):
            raise AssertionError('write-next missing report path')
        if not Path(write_next_report_data['report_path']).exists():
            raise AssertionError('write-next report file missing on disk')
        print('write-next entrypoint ok')

        print('===== revise entrypoint =====')
        revise = run_cli('revise', '--project', str(project), '--chapter-file', str(project / 'chapters' / 'ch01.md'), '--json', check=False)
        if revise.returncode != 0:
            raise SystemExit(revise.stderr.strip() or revise.stdout.strip() or 'cli revise failed')
        revise_data = json.loads(revise.stdout)
        if revise_data['schema_version'] != 'inkos.revision-cycle.v1':
            raise AssertionError('revise schema mismatch')
        if revise_data['summary']['knowledge_check_run'] is not True:
            raise AssertionError('revise should run knowledge check by default')
        if 'audit' not in revise_data or 'revision_plan' not in revise_data or 'spot_fixes' not in revise_data:
            raise AssertionError('revise output missing workflow sections')
        if 'hook_pressure' not in revise_data:
            raise AssertionError('revise missing hook pressure')
        if 'stale_hook_count' not in revise_data['summary']:
            raise AssertionError('revise missing stale hook count')
        print('revise entrypoint ok')

        print('===== package entrypoint =====')
        dist = tmp / 'dist'
        package = run_cli('package', str(dist), 'test-build', check=False)
        if package.returncode != 0:
            raise SystemExit(package.stderr.strip() or package.stdout.strip() or 'cli package failed')
        expected = dist / 'inkos-like-novel-os.skill'
        expected_versioned = dist / 'inkos-like-novel-os-vtest-build.skill'
        if not expected.exists() or not expected_versioned.exists():
            raise AssertionError('package outputs missing')
        print('package entrypoint ok')

        print('===== smoke-test entrypoint =====')
        if invoked_by_cli:
            print('smoke-test entrypoint self-check skipped')
        else:
            smoke = run_cli('smoke-test', check=False)
            if smoke.returncode != 0:
                raise SystemExit(smoke.stderr.strip() or smoke.stdout.strip() or 'cli smoke-test failed')
            if 'Smoke test passed.' not in smoke.stdout:
                raise AssertionError('smoke-test did not report success')
        print('smoke-test entrypoint ok')

        print()
        print('Smoke test passed.')
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == '__main__':
    main()
