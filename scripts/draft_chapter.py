#!/usr/bin/env python3
"""LLM 章节写作执行器：把 write-next 工作包交给 Hermes 等 OpenAI 兼容模型生成单章草稿。

三种模式：
- dry-run：只组装并输出完整请求 payload，不联网、不写盘；
- mock：--mock-response / NOVELOPS_LLM_MOCK 提供响应文件，跳过网络但走完整校验与落盘链路；
- live：真实调用 llm.base_url（默认本地 Ollama）。
"""
import argparse
import json
import re
from pathlib import Path

from build_write_next_packet import build_packet
from llm_client import (
    build_chat_payload,
    chat,
    load_mock_responses,
    resolve_api_key,
    resolve_llm_config,
    resolve_mock_source,
)
from novelops_common import iso_now, parse_chinese_numeral, write_json
from novelops_config import load_project_config

LOOSE_HEADING_RE = re.compile(
    r'^\s{0,3}#{0,3}\s*(?:第\s*([0-9零一二两三四五六七八九十百千]+)\s*章|Chapter\s+(\d+))\b',
    re.M | re.I,
)


def find_chapter_headings(text):
    """返回文本中所有章节标题的 (行文本, 解析出的编号或 None)。"""
    headings = []
    for match in LOOSE_HEADING_RE.finditer(text):
        cn_num, en_num = match.group(1), match.group(2)
        number = None
        if en_num:
            number = int(en_num)
        elif cn_num:
            number = parse_chinese_numeral(cn_num)
        headings.append((match.group(0).strip(), number))
    return headings


def build_messages(packet):
    contract_lines = '\n'.join('- %s' % line for line in packet['single_chapter_contract'])
    constraints = packet['required_inputs'].get('constraints') or []
    constraint_lines = '\n'.join('- %s' % line for line in constraints) if constraints else '- （book_rules.md 未提供显式禁令）'
    system = (
        '你是长篇小说的章节写作执行器，唯一任务是写出目标章节的正文。\n\n'
        '必须严格遵守以下单章契约：\n%s\n\n'
        '必须遵守的书籍约束：\n%s\n\n'
        '输出格式要求：第一行输出章节标题 `## 第 %d 章 <可选标题>`，随后直接是正文段落；'
        '不要输出解释、前言、大纲、创作说明或除正文之外的任何附加内容。'
        % (contract_lines, constraint_lines, packet['chapter'])
    )
    function = packet['chapter_function']
    beats = packet.get('suggested_scene_beats') or []
    task_lines = [
        '## 本章写作任务',
        '- 主要目标：%s' % function.get('primary_goal', ''),
        '- 当前压力：%s' % ('；'.join(function.get('pressure') or []) or '（无显式压力项）'),
        '- 本章回报：%s' % (function.get('planned_payoff_or_partial_payoff') or '（按大纲推进）'),
    ]
    if beats:
        task_lines.append('- 建议场景节拍：')
        task_lines.extend('  - %s' % beat for beat in beats)
    user = (
        '%s\n\n---\n\n%s\n\n参考章计划模板（仅供构思，勿输出模板本身）：\n\n%s\n\n'
        '现在只写第 %d 章正文，写完立即停止。'
        % (packet['context_packet']['context'], '\n'.join(task_lines), packet['plan_template'], packet['chapter'])
    )
    return [
        {'role': 'system', 'content': system},
        {'role': 'user', 'content': user},
    ]


def validate_draft(text, chapter):
    """校验并规范化草稿：拒绝空响应与多章输出，缺标题时自动补齐。"""
    text = (text or '').strip()
    if not text:
        raise SystemExit('LLM returned an empty draft. 请重试，或检查模型与提示词配置。')
    headings = find_chapter_headings(text)
    warnings = []
    heading_added = False
    if len(headings) > 1:
        raise SystemExit(
            'LLM response contains %d chapter headings (%s); 违反单章契约，草稿已拒绝。'
            '请重试，或调小 llm.max_tokens 以降低模型越章概率。'
            % (len(headings), ' / '.join(h[0] for h in headings[:4])))
    if not headings:
        text = '## 第 %d 章\n\n%s' % (chapter, text)
        heading_added = True
    else:
        number = headings[0][1]
        if number is not None and number != chapter:
            warnings.append(
                'Draft heading declares chapter %s but the target is chapter %s; kept as-is.' % (number, chapter))
    normalized = text.replace('\r\n', '\n').replace('\r', '\n').rstrip() + '\n'
    return normalized, {
        'heading_count': len(headings),
        'heading_added': heading_added,
        'warnings': warnings,
    }


def build_draft(project, chapter=None, out=None, force=False, dry_run=False, mock_path=None,
                llm_overrides=None, recent_chapters=3, max_chars_per_file=1800):
    packet = build_packet(project, chapter=chapter, recent_chapters=recent_chapters,
                          max_chars_per_file=max_chars_per_file)
    target_chapter = packet['chapter']
    target_file = Path(out) if out else Path(packet['chapter_file_hint'])

    project_config = load_project_config(project)
    llm_config = resolve_llm_config(project_config, llm_overrides)
    api_key, api_key_source = resolve_api_key(llm_config)
    llm_info = {
        'provider': llm_config['provider'],
        'base_url': llm_config['base_url'],
        'model': llm_config['model'],
        'temperature': llm_config['temperature'],
        'top_p': llm_config['top_p'],
        'max_tokens': llm_config['max_tokens'],
        'api_key': None,
        'api_key_present': api_key is not None,
        'api_key_source': api_key_source,
    }

    messages = build_messages(packet)
    report = {
        'schema_version': 'novelops.draft.v1',
        'tool': 'draft_chapter',
        'generated_at': iso_now(),
        'project': packet['project'],
        'chapter': target_chapter,
        'chapter_file': str(target_file),
        'mode': 'dry-run',
        'llm': llm_info,
        'request': None,
        'response': None,
        'validation': None,
        'write': {'written': False, 'chapter_file': str(target_file), 'forced': bool(force)},
        'next_actions': [
            '对草稿依次跑 revise / knowledge-check / audit',
            '接受后跑 extract-state 与 state-update',
        ],
    }

    if dry_run:
        report['request'] = {'payload': build_chat_payload(messages, llm_config)}
        return report

    if target_file.exists() and not force:
        raise SystemExit('Draft target already exists: %s. Use --force to overwrite.' % target_file)

    mock_source = resolve_mock_source(mock_path)
    mock_content = load_mock_responses(mock_source)[0] if mock_source else None
    result = chat(messages, llm_config, mock_content=mock_content)

    normalized, validation = validate_draft(result['content'], target_chapter)

    report['mode'] = 'mock' if result['transport'] == 'mock' else 'live'
    report['request'] = {
        'message_count': len(messages),
        'system_chars': len(messages[0]['content']),
        'user_chars': len(messages[1]['content']),
    }
    report['response'] = {
        'raw_chars': len(result['raw_content'] or ''),
        'content_chars': len(normalized),
        'think_stripped': result['raw_content'] != result['content'],
        'usage': result['usage'],
        'model': result['model'],
    }
    report['validation'] = validation

    target_file.parent.mkdir(parents=True, exist_ok=True)
    target_file.write_text(normalized, encoding='utf-8')
    report['write'] = {'written': True, 'chapter_file': str(target_file), 'forced': bool(force)}
    return report


def print_markdown(report):
    print('# Draft Chapter')
    print()
    print('- mode: %s' % report['mode'])
    print('- chapter: %s' % report['chapter'])
    print('- chapter_file: %s' % report['chapter_file'])
    print('- written: %s' % ('yes' if report['write']['written'] else 'no'))
    if report.get('validation'):
        print('- heading_added: %s' % ('yes' if report['validation']['heading_added'] else 'no'))
        for warning in report['validation']['warnings']:
            print('- warning: %s' % warning)
    print()
    print('## Next actions')
    for item in report['next_actions']:
        print('- %s' % item)


def main():
    parser = argparse.ArgumentParser(description='Draft the next chapter with an OpenAI-compatible LLM (Hermes-first).')
    parser.add_argument('--project', required=True)
    parser.add_argument('--chapter', type=int)
    parser.add_argument('--out')
    parser.add_argument('--force', action='store_true')
    parser.add_argument('--dry-run', action='store_true', help='Print the chat payload without calling the LLM.')
    parser.add_argument('--mock-response', help='File whose content is used as the LLM response (offline).')
    parser.add_argument('--json', action='store_true')
    parser.add_argument('--write-report', action='store_true')
    parser.add_argument('--model')
    parser.add_argument('--base-url')
    parser.add_argument('--temperature', type=float)
    parser.add_argument('--top-p', type=float, dest='top_p')
    parser.add_argument('--max-tokens', type=int, dest='max_tokens')
    parser.add_argument('--timeout', type=int, dest='timeout_seconds')
    parser.add_argument('--recent-chapters', type=int, default=3)
    parser.add_argument('--max-chars-per-file', type=int, default=1800)
    args = parser.parse_args()

    llm_overrides = {
        'model': args.model,
        'base_url': args.base_url,
        'temperature': args.temperature,
        'top_p': args.top_p,
        'max_tokens': args.max_tokens,
        'timeout_seconds': args.timeout_seconds,
    }

    report = build_draft(
        args.project,
        chapter=args.chapter,
        out=args.out,
        force=args.force,
        dry_run=args.dry_run,
        mock_path=args.mock_response,
        llm_overrides=llm_overrides,
        recent_chapters=args.recent_chapters,
        max_chars_per_file=args.max_chars_per_file,
    )

    if args.write_report:
        reviews = Path(args.project) / 'reviews'
        out = reviews / ('ch%02d.draft.json' % report['chapter'])
        report['report_path'] = str(out)
        write_json(out, report)

    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print_markdown(report)


if __name__ == '__main__':
    main()
