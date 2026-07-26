#!/usr/bin/env python3
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

from novelops_common import configure_stdio_utf8, parse_chinese_numeral

ROOT = Path(__file__).resolve().parent.parent
CLI = ROOT / 'scripts' / 'novelops_cli.py'
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


def check_iso_now_format():
    env = dict(os.environ)
    env['PYTHONUTF8'] = '1'
    result = subprocess.run(
        [PYTHON, '-W', 'error::DeprecationWarning', '-c',
         'import sys; sys.path.insert(0, r"%s"); from novelops_common import iso_now; print(iso_now())'
         % str(ROOT / 'scripts')],
        capture_output=True,
        text=True,
        encoding='utf-8',
        errors='replace',
        env=env,
    )
    if result.returncode != 0:
        raise AssertionError('iso_now raised a warning/error: %s' % result.stderr.strip())
    stamp = result.stdout.strip()
    if not re.fullmatch(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z', stamp):
        raise AssertionError('iso_now format changed: %r' % stamp)


def main():
    invoked_by_cli = '--invoked-by-cli' in sys.argv[1:]
    tmp = ROOT / '.smoke-work'
    shutil.rmtree(tmp, ignore_errors=True)
    tmp.mkdir(parents=True, exist_ok=True)
    try:
        print('===== iso_now format regression =====')
        check_iso_now_format()
        print('iso_now format ok')

        project = tmp / 'demo-novel'

        print('===== cli init regression =====')
        init_result = run_cli('init', str(project), '测试长篇', check=False)
        if init_result.returncode != 0:
            raise SystemExit(init_result.stderr.strip() or init_result.stdout.strip() or 'cli init failed')
        for rel in ['README-project.md', 'story_bible.md', 'book_rules.md', 'outline.md', 'current_state.md']:
            if not (project / rel).exists():
                raise AssertionError(f'missing initialized file: {rel}')
        print('cli init ok')

        print('===== init non-empty directory safety regression =====')
        custom_state = project / 'current_state.md'
        custom_state.write_text('CUSTOM USER STATE SHOULD SURVIVE\n', encoding='utf-8')
        blocked_init = run_cli('init', str(project), '覆盖测试', check=False)
        if blocked_init.returncode == 0:
            raise AssertionError('init should fail for a non-empty directory without --force')
        blocked_message = (blocked_init.stderr + blocked_init.stdout).lower()
        if '--force' not in blocked_message:
            raise AssertionError('init safety error should mention --force')
        if custom_state.read_text(encoding='utf-8') != 'CUSTOM USER STATE SHOULD SURVIVE\n':
            raise AssertionError('init safety check allowed existing project content to change')

        empty_project = tmp / 'empty-init-novel'
        empty_project.mkdir()
        empty_init = run_cli('init', str(empty_project), '空目录项目', check=False)
        if empty_init.returncode != 0:
            raise SystemExit(empty_init.stderr.strip() or empty_init.stdout.strip() or 'cli init failed for empty directory')
        if not (empty_project / 'current_state.md').exists():
            raise AssertionError('init should allow an existing empty directory')

        force_init = run_cli('init', str(project), '强制覆盖测试', '--force', check=False)
        if force_init.returncode != 0:
            raise SystemExit(force_init.stderr.strip() or force_init.stdout.strip() or 'cli init --force failed')
        assert_contains(project / 'current_state.md', '强制覆盖测试')
        print('init non-empty directory safety ok')

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

        print('===== chapter_file contract regression =====')
        audit_contract = json.loads(
            run_cli('audit', '--project', str(project), '--chapter-file', str(project / 'chapters' / 'ch01.md'), '--json').stdout
        )
        if not audit_contract.get('chapter_file') or audit_contract['chapter_file'] != audit_contract['chapter']:
            raise AssertionError('audit report should carry chapter_file equal to chapter')
        for subcommand, report_key in (('revision-plan', 'revision plan'), ('spot-fixes', 'spot-fix suggestions')):
            contract_data = json.loads(
                run_cli(subcommand, '--project', str(project), '--chapter-file', str(project / 'chapters' / 'ch01.md'), '--json').stdout
            )
            if not contract_data.get('chapter_file'):
                raise AssertionError('%s output missing chapter_file' % report_key)
        print('chapter_file contract ok')

        print('===== project config engine =====')
        import novelops_config
        if novelops_config.load_project_config(tmp) != {}:
            raise AssertionError('load_project_config should return {} when no config file exists')
        merged, source = novelops_config.resolve_keyword_table(
            'T', ['a', 'b'], {'mode': 'extend', 'items': ['c', 'a']})
        if merged != ['a', 'b', 'c'] or source != 'extend':
            raise AssertionError('extend merge mismatch: %r / %r' % (merged, source))
        merged, source = novelops_config.resolve_keyword_table(
            'T', ['a', 'b'], {'mode': 'replace', 'items': ['x']})
        if merged != ['x'] or source != 'replace':
            raise AssertionError('replace merge mismatch: %r / %r' % (merged, source))
        merged, source = novelops_config.resolve_keyword_table('T', ['a'], {'mode': 'disable'})
        if merged != [] or source != 'disable':
            raise AssertionError('disable merge mismatch: %r / %r' % (merged, source))
        merged, source = novelops_config.resolve_keyword_table('T', ['a'], None)
        if merged != ['a'] or source != 'default':
            raise AssertionError('default merge mismatch: %r / %r' % (merged, source))
        bad_config_dir = tmp / 'bad-config-project'
        bad_config_dir.mkdir(exist_ok=True)
        (bad_config_dir / 'novelops.config.json').write_text('{broken', encoding='utf-8')
        try:
            novelops_config.load_project_config(bad_config_dir)
        except SystemExit as exc:
            if 'novelops.config.json' not in str(exc):
                raise AssertionError('bad config error should mention the file: %s' % exc)
        else:
            raise AssertionError('broken config JSON should raise SystemExit')
        template_config_path = project / 'novelops.config.json'
        if not template_config_path.exists():
            raise AssertionError('init should copy novelops.config.json from the template')
        template_config = json.loads(template_config_path.read_text(encoding='utf-8'))
        if template_config.get('audit') != {} or template_config.get('knowledge') != {}:
            raise AssertionError('template config should ship empty audit/knowledge sections')
        if template_config.get('llm', {}).get('base_url') != 'http://localhost:11434/v1':
            raise AssertionError('template config should default llm.base_url to local Ollama')
        print('project config engine ok')

        print('===== audit config engine =====')
        cfg_project = tmp / 'config-novel'
        cfg_init = run_cli('init', str(cfg_project), '配置测试', check=False)
        if cfg_init.returncode != 0:
            raise SystemExit(cfg_init.stderr.strip() or cfg_init.stdout.strip() or 'config project init failed')
        cfg_config_path = cfg_project / 'novelops.config.json'
        cfg_ch01 = cfg_project / 'chapters' / 'ch01.md'
        cfg_ch01.write_text(
            '# 第一章\n\n'
            '突然一声。突然又一声。突然第三声。突然第四声。突然第五声。\n\n'
            '这件事的核心在于本质上的动机差异。\n\n'
            '他感到不安。她感到紧张。他意识到自己已经疲惫。\n',
            encoding='utf-8',
        )

        def cfg_audit():
            return json.loads(
                run_cli('audit', '--project', str(cfg_project), '--chapter-file', str(cfg_ch01), '--json').stdout
            )

        with_template_cfg = cfg_audit()
        cfg_config_path.unlink()
        without_cfg = cfg_audit()
        if with_template_cfg['findings'] != without_cfg['findings']:
            raise AssertionError('empty audit config must not change findings')
        if with_template_cfg['summary']['rules_evaluated'] != without_cfg['summary']['rules_evaluated']:
            raise AssertionError('empty audit config must not change rules_evaluated')
        if with_template_cfg['summary']['counts'] != without_cfg['summary']['counts']:
            raise AssertionError('empty audit config must not change counts')
        if 'config' not in without_cfg['summary'] or without_cfg['summary']['config']['config_file'] is not None:
            raise AssertionError('audit summary should carry a config block with config_file None when unconfigured')
        aud101 = [f for f in without_cfg['findings'] if f['rule_id'] == 'AUD-101']
        if not aud101 or aud101[0]['severity'] != 'major' or aud101[0]['evidence'] != ['突然']:
            raise AssertionError('default AUD-101 behavior changed: %r' % aud101)
        if not any(f['rule_id'] == 'AUD-102' for f in without_cfg['findings']):
            raise AssertionError('default AUD-102 behavior changed')
        if not any(f['rule_id'] == 'AUD-113' for f in without_cfg['findings']):
            raise AssertionError('default AUD-113 behavior changed')

        cfg_config_path.write_text(json.dumps({
            'audit': {'keywords': {'TRANSITIONS': {'mode': 'extend', 'items': ['蓦然回身']}}}
        }, ensure_ascii=False), encoding='utf-8')
        cfg_ch01.write_text(
            '# 第一章\n\n蓦然回身一次。蓦然回身两次。蓦然回身三次。\n',
            encoding='utf-8',
        )
        extended = cfg_audit()
        if not any(f['rule_id'] == 'AUD-101' and f['evidence'] == ['蓦然回身'] for f in extended['findings']):
            raise AssertionError('extended TRANSITIONS keyword should trigger AUD-101')
        if extended['summary']['config']['keyword_tables_overridden'].get('TRANSITIONS') != 'extend':
            raise AssertionError('summary.config should record the extended table')

        cfg_config_path.write_text(json.dumps({
            'audit': {'keywords': {'TRANSITIONS': {'mode': 'replace', 'items': ['蓦然回身']}}}
        }, ensure_ascii=False), encoding='utf-8')
        cfg_ch01.write_text(
            '# 第一章\n\n突然一声。突然又一声。突然第三声。突然第四声。突然第五声。\n',
            encoding='utf-8',
        )
        replaced = cfg_audit()
        if any(f['rule_id'] == 'AUD-101' for f in replaced['findings']):
            raise AssertionError('replaced TRANSITIONS table should stop default word from triggering AUD-101')

        cfg_config_path.write_text(json.dumps({
            'audit': {'thresholds': {'AUD-113': {'min_hits': 1}}}
        }, ensure_ascii=False), encoding='utf-8')
        cfg_ch01.write_text('# 第一章\n\n他感到不安，但没有说出口。\n', encoding='utf-8')
        threshold_hit = cfg_audit()
        if not any(f['rule_id'] == 'AUD-113' for f in threshold_hit['findings']):
            raise AssertionError('lowered AUD-113 threshold should trigger on a single hit')
        if 'AUD-113' not in threshold_hit['summary']['config']['thresholds_overridden']:
            raise AssertionError('summary.config should record threshold override')

        cfg_config_path.write_text(json.dumps({
            'audit': {'rules_disabled': ['AUD-113']}
        }, ensure_ascii=False), encoding='utf-8')
        cfg_ch01.write_text(
            '# 第一章\n\n他感到不安。她感到紧张。他意识到自己已经疲惫。\n', encoding='utf-8')
        disabled_report = cfg_audit()
        if any(f['rule_id'] == 'AUD-113' for f in disabled_report['findings']):
            raise AssertionError('disabled AUD-113 should not produce findings')
        if 'AUD-113' in disabled_report['summary']['rules_evaluated']:
            raise AssertionError('disabled AUD-113 should not be in rules_evaluated')
        if disabled_report['summary']['config']['rules_disabled'] != ['AUD-113']:
            raise AssertionError('summary.config should record disabled rules')

        for bad_audit_cfg in (
            {'audit': {'keywords': {'NOT_A_TABLE': {'mode': 'extend', 'items': ['x']}}}},
            {'audit': {'thresholds': {'AUD-999': {'min_hits': 1}}}},
            {'audit': {'rules_disabled': ['AUD-999']}},
        ):
            cfg_config_path.write_text(json.dumps(bad_audit_cfg, ensure_ascii=False), encoding='utf-8')
            bad_run = run_cli('audit', '--project', str(cfg_project), '--chapter-file', str(cfg_ch01), '--json', check=False)
            if bad_run.returncode == 0:
                raise AssertionError('invalid audit config should fail: %r' % bad_audit_cfg)
            if 'Traceback' in (bad_run.stderr or ''):
                raise AssertionError('invalid audit config should not raise a traceback: %s' % bad_run.stderr.strip())
        cfg_config_path.write_text(json.dumps({'audit': {}, 'knowledge': {}}, ensure_ascii=False), encoding='utf-8')
        print('audit config engine ok')

        print('===== knowledge config engine =====')
        kn_ch = cfg_project / 'chapters' / 'kn01.md'
        kn_ch.write_text('# 章节\n\n林烬早就知道真相。\n\n没人知道的是，账册已被换过。\n', encoding='utf-8')

        def cfg_knowledge():
            return json.loads(
                run_cli('knowledge-check', '--project', str(cfg_project), '--chapter-file', str(kn_ch), '--json').stdout
            )

        kn_with_cfg = cfg_knowledge()
        cfg_config_path.unlink()
        kn_no_cfg = cfg_knowledge()
        if kn_with_cfg['violations'] != kn_no_cfg['violations'] or kn_with_cfg['ok'] != kn_no_cfg['ok']:
            raise AssertionError('empty knowledge config must not change violations')
        if 'config' not in kn_no_cfg['summary'] or kn_no_cfg['summary']['config']['config_file'] is not None:
            raise AssertionError('knowledge summary should carry a config block with config_file None when unconfigured')
        if not any(v['type'] == 'knowledge-leak' for v in kn_no_cfg['violations']):
            raise AssertionError('default knowledge-leak pattern behavior changed')
        if not any(v['type'] == 'omniscient-leak' and v['severity'] == 'major' for v in kn_no_cfg['violations']):
            raise AssertionError('default omniscient-leak behavior changed')
        if kn_no_cfg['ok'] is not False:
            raise AssertionError('major omniscient-leak should make ok False')

        cfg_config_path.write_text(json.dumps({
            'knowledge': {'kinds_disabled': ['omniscient-leak']}
        }, ensure_ascii=False), encoding='utf-8')
        kn_disabled = cfg_knowledge()
        if any(v['type'] == 'omniscient-leak' for v in kn_disabled['violations']):
            raise AssertionError('disabled omniscient-leak should not produce violations')
        if kn_disabled['ok'] is not True:
            raise AssertionError('with omniscient-leak disabled the remaining minor leak should leave ok True')
        if kn_disabled['summary']['config']['kinds_disabled'] != ['omniscient-leak']:
            raise AssertionError('knowledge summary.config should record kinds_disabled')

        cfg_config_path.write_text(json.dumps({
            'knowledge': {'leak_patterns': {'mode': 'extend', 'items': [{'kind': 'knowledge-leak', 'pattern': '早已看穿'}]}}
        }, ensure_ascii=False), encoding='utf-8')
        kn_ch.write_text('# 章节\n\n他早已看穿一切。\n', encoding='utf-8')
        kn_extended = cfg_knowledge()
        if not any(v['type'] == 'knowledge-leak' and '早已看穿' in v['evidence'] for v in kn_extended['violations']):
            raise AssertionError('extended leak pattern should trigger a violation')

        (cfg_project / 'current_state.md').write_text(
            '# Current State\n\n## Character beliefs\n- 林烬：并不清楚玉佩的真相\n', encoding='utf-8')
        kn_ch.write_text('# 章节\n\n林烬看出了真相的全部内情。\n', encoding='utf-8')
        cfg_config_path.unlink()
        kn_belief = cfg_knowledge()
        if not any(v.get('character') == '林烬' for v in kn_belief['violations']):
            raise AssertionError('belief-based knowledge leak should trigger by default')
        cfg_config_path.write_text(json.dumps({
            'knowledge': {'keywords': {'BELIEF_SUSPICION_TOKENS': {'mode': 'extend', 'items': ['看出']}}}
        }, ensure_ascii=False), encoding='utf-8')
        kn_exempted = cfg_knowledge()
        if any(v.get('character') == '林烬' for v in kn_exempted['violations']):
            raise AssertionError('extended suspicion token should exempt the belief-based violation')

        for bad_kn_cfg in (
            {'knowledge': {'kinds_disabled': ['not-a-kind']}},
            {'knowledge': {'leak_patterns': {'mode': 'extend', 'items': [{'kind': 'knowledge-leak', 'pattern': '('}]}}},
            {'knowledge': {'keywords': {'NOT_A_TABLE': {'mode': 'extend', 'items': ['x']}}}},
        ):
            cfg_config_path.write_text(json.dumps(bad_kn_cfg, ensure_ascii=False), encoding='utf-8')
            bad_kn_run = run_cli('knowledge-check', '--project', str(cfg_project), '--chapter-file', str(kn_ch), '--json', check=False)
            if bad_kn_run.returncode == 0:
                raise AssertionError('invalid knowledge config should fail: %r' % bad_kn_cfg)
            if 'Traceback' in (bad_kn_run.stderr or ''):
                raise AssertionError('invalid knowledge config should not raise a traceback: %s' % bad_kn_run.stderr.strip())
        cfg_config_path.write_text(json.dumps({'audit': {}, 'knowledge': {}}, ensure_ascii=False), encoding='utf-8')
        print('knowledge config engine ok')

        print('===== llm client offline paths =====')
        import llm_client
        if llm_client.strip_think_blocks('<think>推理过程</think>\n正文段落。') != '正文段落。':
            raise AssertionError('strip_think_blocks should remove closed think blocks')
        if llm_client.strip_think_blocks('残留推理</think>\n正文段落。') != '正文段落。':
            raise AssertionError('strip_think_blocks should recover from a dangling closing tag')
        try:
            llm_client.strip_think_blocks('<think>未闭合的推理与正文混在一起')
        except SystemExit as exc:
            if 'max_tokens' not in str(exc):
                raise AssertionError('unclosed think block error should mention max_tokens: %s' % exc)
        else:
            raise AssertionError('unclosed think block should raise SystemExit')
        default_llm_cfg = llm_client.resolve_llm_config({})
        if default_llm_cfg['base_url'] != 'http://localhost:11434/v1' or default_llm_cfg['temperature'] != 0.6:
            raise AssertionError('default llm config should target local Ollama with Hermes sampling defaults')
        overridden_llm_cfg = llm_client.resolve_llm_config({}, {'model': 'custom-model'})
        if overridden_llm_cfg['model'] != 'custom-model' or overridden_llm_cfg['top_p'] != 0.95:
            raise AssertionError('llm config overrides should only touch given keys')
        try:
            llm_client.resolve_llm_config({'llm': {'no_such_key': 1}})
        except SystemExit:
            pass
        else:
            raise AssertionError('unknown llm config key should raise SystemExit')
        payload = llm_client.build_chat_payload(
            [{'role': 'system', 'content': 's'}, {'role': 'user', 'content': 'u'}], default_llm_cfg)
        if payload['stream'] is not False or payload['temperature'] != 0.6 or payload['top_p'] != 0.95:
            raise AssertionError('chat payload should carry Hermes sampling defaults and stream=False')
        if payload['model'] != default_llm_cfg['model'] or len(payload['messages']) != 2:
            raise AssertionError('chat payload should carry model and messages')
        mock_file = tmp / 'mock-response.json'
        mock_file.write_text(json.dumps(
            {'choices': [{'message': {'content': '来自 OpenAI 格式的正文'}}]}, ensure_ascii=False), encoding='utf-8')
        if llm_client.load_mock_responses(mock_file) != ['来自 OpenAI 格式的正文']:
            raise AssertionError('load_mock_responses should unwrap an OpenAI response object')
        mock_file.write_text(json.dumps(['第一段', '第二段'], ensure_ascii=False), encoding='utf-8')
        if llm_client.load_mock_responses(mock_file) != ['第一段', '第二段']:
            raise AssertionError('load_mock_responses should accept a JSON array')
        mock_file.write_text('纯文本 mock 正文', encoding='utf-8')
        if llm_client.load_mock_responses(mock_file) != ['纯文本 mock 正文']:
            raise AssertionError('load_mock_responses should fall back to raw text')
        mock_chat = llm_client.chat(
            [{'role': 'user', 'content': 'u'}], default_llm_cfg, mock_content='<think>t</think>\nmock 正文')
        if mock_chat['content'] != 'mock 正文' or mock_chat['transport'] != 'mock':
            raise AssertionError('mock chat should strip think and mark transport=mock')
        print('llm client offline paths ok')

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
        write_next = run_cli('write-next', '--project', str(project), '--chapter', '2', '--json', check=False)
        if write_next.returncode != 0:
            raise SystemExit(write_next.stderr.strip() or write_next.stdout.strip() or 'cli write-next failed')
        write_next_data = json.loads(write_next.stdout)
        if write_next_data['schema_version'] != 'novelops.write-next.v1':
            raise AssertionError('write-next schema mismatch')
        if write_next_data['chapter'] != 2:
            raise AssertionError(f'write-next chapter mismatch: {write_next_data["chapter"]}')
        if write_next_data['context_packet']['target_chapter'] != 2:
            raise AssertionError('write-next context target_chapter mismatch')
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
        write_next_report = run_cli('write-next', '--project', str(project), '--chapter', '2', '--json', '--write-report', check=False)
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
        if revise_data['schema_version'] != 'novelops.revision-cycle.v1':
            raise AssertionError('revise schema mismatch')
        if revise_data['summary']['knowledge_check_run'] is not True:
            raise AssertionError('revise should run knowledge check by default')
        if 'audit' not in revise_data or 'revision_plan' not in revise_data or 'spot_fixes' not in revise_data:
            raise AssertionError('revise output missing workflow sections')
        if 'hook_pressure' not in revise_data:
            raise AssertionError('revise missing hook pressure')
        if 'stale_hook_count' not in revise_data['summary']:
            raise AssertionError('revise missing stale hook count')
        if not revise_data.get('chapter_file') or not revise_data['audit'].get('chapter_file'):
            raise AssertionError('revise output missing chapter_file fields')
        print('revise entrypoint ok')

        print('===== write-report guard regression =====')
        audit_json = json.loads(
            run_cli('audit', '--project', str(project), '--chapter-file', str(project / 'chapters' / 'ch01.md'), '--json').stdout
        )
        partial_audit = dict(audit_json)
        partial_audit.pop('project', None)
        partial_audit_path = tmp / 'partial-audit.json'
        partial_audit_path.write_text(json.dumps(partial_audit, ensure_ascii=False, indent=2), encoding='utf-8')
        for subcommand in ('revision-plan', 'spot-fixes'):
            guarded = run_cli(subcommand, '--audit-report', str(partial_audit_path), '--write-report', check=False)
            if guarded.returncode == 0:
                raise AssertionError('%s --write-report should fail when the audit report lacks "project"' % subcommand)
            guarded_stderr = guarded.stderr or ''
            if '--write-report requires' not in guarded_stderr:
                raise AssertionError('%s guard error should mention --write-report requires, got: %s' % (subcommand, guarded_stderr.strip()))
            if 'Traceback' in guarded_stderr:
                raise AssertionError('%s guard should not raise a traceback:\n%s' % (subcommand, guarded_stderr.strip()))
        bare_audit = dict(partial_audit)
        bare_audit.pop('chapter', None)
        bare_audit.pop('chapter_file', None)
        bare_audit_path = tmp / 'bare-audit.json'
        bare_audit_path.write_text(json.dumps(bare_audit, ensure_ascii=False, indent=2), encoding='utf-8')
        bare_fixes = run_cli('spot-fixes', '--audit-report', str(bare_audit_path), '--json', check=False)
        if bare_fixes.returncode != 0:
            raise AssertionError('spot-fixes without --write-report should tolerate a report missing "chapter": %s' % (bare_fixes.stderr or '').strip())
        json.loads(bare_fixes.stdout)
        print('write-report guard ok')

        print('===== snapshot dir & legacy fallback regression =====')
        snap_manifest = json.loads(run_cli('snapshot', '--project', str(project), '--json').stdout)
        if '.novelops-state' not in snap_manifest['snapshot_dir']:
            raise AssertionError('snapshot should be written under .novelops-state, got: %s' % snap_manifest['snapshot_dir'])
        if not (project / '.novelops-state' / 'snapshots').exists():
            raise AssertionError('snapshot did not create .novelops-state/snapshots')
        if not (project / '.novelops-state' / 'index.jsonl').exists():
            raise AssertionError('snapshot did not append .novelops-state/index.jsonl')
        if (project / '.inkos-state').exists():
            raise AssertionError('snapshot should not create the legacy .inkos-state directory')
        legacy_project = tmp / 'legacy-snap-novel'
        legacy_init = run_cli('init', str(legacy_project), '旧快照项目', check=False)
        if legacy_init.returncode != 0:
            raise SystemExit(legacy_init.stderr.strip() or legacy_init.stdout.strip() or 'legacy project init failed')
        legacy_snapshot_dir = legacy_project / '.inkos-state' / 'snapshots' / '20200101T000000Z-ch001-legacy'
        legacy_snapshot_dir.mkdir(parents=True)
        shutil.copy2(str(legacy_project / 'current_state.md'), str(legacy_snapshot_dir / 'current_state.md'))
        with (legacy_project / 'current_state.md').open('a', encoding='utf-8') as f:
            f.write('\n- 旧快照回退测试：当前状态已推进。\n')
        legacy_diff = run_cli('diff', '--project', str(legacy_project), '--from', 'latest', '--to', 'current', '--json', check=False)
        if legacy_diff.returncode != 0:
            raise AssertionError('diff should read snapshots from the legacy .inkos-state directory: %s'
                                 % (legacy_diff.stderr or legacy_diff.stdout or '').strip())
        legacy_diff_data = json.loads(legacy_diff.stdout)
        if legacy_diff_data['from']['id'] != '20200101T000000Z-ch001-legacy':
            raise AssertionError('diff latest should resolve to the legacy snapshot, got: %s' % legacy_diff_data['from']['id'])
        if legacy_diff_data['summary']['changed_files'] < 1:
            raise AssertionError('legacy fallback diff should report changes')
        print('snapshot dir & legacy fallback ok')

        print('===== reverse-longdoc entrypoint =====')
        longdoc_source = tmp / 'longdoc-source.md'
        longdoc_workspace = tmp / 'reverse-project'
        longdoc_source.write_text(
            """# 示例长文档

第一章 初到旧宅
林烬第一次进旧宅时，就觉得走廊深处有人盯着自己。他怀疑这地方藏着旧事。

第二章 雨夜账册
雨夜里他翻到账册，确认其中有被改写过的痕迹，也知道徐安在隐瞒一部分线索。

第三章 回廊试探
他试探徐安，但没有直接摊牌，只是进一步怀疑玉佩在入库前就已经被动过。
""",
            encoding='utf-8',
        )
        reverse = run_cli(
            'reverse-longdoc',
            '--source',
            str(longdoc_source),
            '--workspace',
            str(longdoc_workspace),
            '--chapters-per-file',
            '2',
            '--json',
            check=False,
        )
        if reverse.returncode != 0:
            raise SystemExit(reverse.stderr.strip() or reverse.stdout.strip() or 'cli reverse-longdoc failed')
        reverse_data = json.loads(reverse.stdout)
        if reverse_data['schema_version'] != 'novelops.longdoc-reverse.v1':
            raise AssertionError('reverse-longdoc schema mismatch')
        if reverse_data['summary']['total_chapters'] != 3:
            raise AssertionError('reverse-longdoc total_chapters mismatch')
        index_path = Path(reverse_data['outputs']['index'])
        summary_json_path = Path(reverse_data['outputs']['summary_json'])
        summary_md_path = Path(reverse_data['outputs']['summary_md'])
        if not index_path.exists() or not summary_json_path.exists() or not summary_md_path.exists():
            raise AssertionError('reverse-longdoc missing output files')
        index_data = json.loads(index_path.read_text(encoding='utf-8'))
        if index_data['total_chapters'] != 3 or len(index_data['chunk_files']) != 2:
            raise AssertionError('reverse-longdoc index mismatch')
        summary_data = json.loads(summary_json_path.read_text(encoding='utf-8'))
        if len(summary_data['chapters']) != 3:
            raise AssertionError('reverse-longdoc summary chapter mismatch')
        if 'all_state_changes' not in summary_data['aggregated']:
            raise AssertionError('reverse-longdoc aggregated summary missing state changes')
        print('reverse-longdoc entrypoint ok')

        print('===== chinese chapter numbering regression =====')
        expected_numerals = {'一': 1, '十二': 12, '一百零三': 103, '两百': 200, '三千': 3000}
        for numeral, expected in expected_numerals.items():
            actual = parse_chinese_numeral(numeral)
            if actual != expected:
                raise AssertionError('parse_chinese_numeral(%r) = %r, expected %r' % (numeral, actual, expected))
        cn_source = tmp / 'cn-longdoc.md'
        cn_workspace = tmp / 'cn-reverse-project'
        cn_source.write_text(
            """第三章 回廊夜话
他在回廊里等到了徐安，两人围绕玉佩的来历彼此试探。

第十二章 账册缺页
他发现账册缺了关键一页，怀疑有人提前处理过记录。

第一百零三章 尘埃落定
真正的经手人终于浮出水面，旧案得以了结。
""",
            encoding='utf-8',
        )
        cn_reverse = run_cli(
            'reverse-longdoc',
            '--source',
            str(cn_source),
            '--workspace',
            str(cn_workspace),
            '--json',
            check=False,
        )
        if cn_reverse.returncode != 0:
            raise SystemExit(cn_reverse.stderr.strip() or cn_reverse.stdout.strip() or 'cn reverse-longdoc failed')
        cn_index = json.loads(Path(json.loads(cn_reverse.stdout)['outputs']['index']).read_text(encoding='utf-8'))
        cn_numbers = [row['chapter_num'] for row in cn_index['chapters']]
        if cn_numbers != [3, 12, 103]:
            raise AssertionError('chinese numeral chapter numbers mismatch: %r (expected [3, 12, 103])' % cn_numbers)
        print('chinese chapter numbering ok')

        print('===== package entrypoint =====')
        dist = tmp / 'dist'
        package = run_cli('package', str(dist), 'test-build', check=False)
        if package.returncode != 0:
            raise SystemExit(package.stderr.strip() or package.stdout.strip() or 'cli package failed')
        expected = dist / 'novelops-skill.skill'
        expected_versioned = dist / 'novelops-skill-vtest-build.skill'
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
