#!/usr/bin/env python3
import argparse
import json
import re
from pathlib import Path

from novelops_common import (
    extract_markdown_section,
    iso_now,
    parse_chapter_number,
    read_text,
    require_existing_file,
    require_project_markers,
    split_sentences,
)
from novelops_config import config_file_path, load_project_config, resolve_disabled, resolve_keyword_table

DEFAULT_LEAK_PATTERNS = [
    ('knowledge-leak', r'(早就知道|当然知道|已经知道真相|其实早已明白|他当然知道真相|她当然知道真相)'),
    ('premature-certainty', r'(真相就是|幕后之人就是|答案已经摆在眼前|已经确认|毫无疑问)'),
    ('omniscient-leak', r'(没人知道的是|他不知道的是|她不知道的是|与此同时另一边|此时远在)'),
]

LEAK_PATTERNS = [(kind, re.compile(pattern)) for kind, pattern in DEFAULT_LEAK_PATTERNS]

BELIEF_NEGATION_TOKENS = ['不知道', '不知', '尚未得知', '未察觉', '并不清楚', '还不清楚', '蒙在鼓里']
BELIEF_SUSPICION_TOKENS = ['怀疑', '猜测', '觉得', '似乎', '隐约', '推测']
FACT_CONFIDENCE_TOKENS = ['真相', '幕后', '内情', '计划', '身份', '替换者', '伪造', '原物']

DEFAULT_KEYWORD_TABLES = {
    'BELIEF_NEGATION_TOKENS': BELIEF_NEGATION_TOKENS,
    'BELIEF_SUSPICION_TOKENS': BELIEF_SUSPICION_TOKENS,
    'FACT_CONFIDENCE_TOKENS': FACT_CONFIDENCE_TOKENS,
}

VALID_LEAK_KINDS = ('knowledge-leak', 'premature-certainty', 'omniscient-leak')
VALID_KNOWLEDGE_SECTION_KEYS = ('keywords', 'leak_patterns', 'kinds_disabled')
VALID_LEAK_PATTERN_MODES = ('extend', 'replace', 'disable')


def resolve_knowledge_config(project, config=None):
    """解析项目配置的 knowledge 节，返回 (token 表, 已编译泄漏模式, 禁用 kind 集合, summary.config 块)。"""
    if config is None:
        config = load_project_config(project)
    kcfg = config.get('knowledge') or {}
    for key in kcfg:
        if key not in VALID_KNOWLEDGE_SECTION_KEYS:
            raise SystemExit(
                'novelops.config.json knowledge section has unknown key %r (known: %s)'
                % (key, ', '.join(VALID_KNOWLEDGE_SECTION_KEYS)))
    kw_specs = kcfg.get('keywords') or {}
    for name in kw_specs:
        if name not in DEFAULT_KEYWORD_TABLES:
            raise SystemExit(
                'novelops.config.json knowledge.keywords has unknown table %r (known: %s)'
                % (name, ', '.join(sorted(DEFAULT_KEYWORD_TABLES))))
    tables = {}
    tables_overridden = {}
    for name, default in DEFAULT_KEYWORD_TABLES.items():
        merged, source = resolve_keyword_table(name, default, kw_specs.get(name))
        tables[name] = merged
        if source != 'default':
            tables_overridden[name] = source

    spec = kcfg.get('leak_patterns')
    patterns_source = 'default'
    if spec is None:
        raw_patterns = list(DEFAULT_LEAK_PATTERNS)
    else:
        if not isinstance(spec, dict):
            raise SystemExit('novelops.config.json knowledge.leak_patterns must be an object with "mode"/"items"')
        mode = spec.get('mode', 'extend')
        if mode not in VALID_LEAK_PATTERN_MODES:
            raise SystemExit(
                'novelops.config.json knowledge.leak_patterns has unknown mode %r (expected one of %s)'
                % (mode, '/'.join(VALID_LEAK_PATTERN_MODES)))
        items = []
        for item in spec.get('items', []):
            if not isinstance(item, dict) or 'kind' not in item or 'pattern' not in item:
                raise SystemExit(
                    'novelops.config.json knowledge.leak_patterns items must be objects with "kind" and "pattern"')
            if item['kind'] not in VALID_LEAK_KINDS:
                raise SystemExit(
                    'novelops.config.json knowledge.leak_patterns has unknown kind %r (known: %s)'
                    % (item['kind'], ', '.join(VALID_LEAK_KINDS)))
            items.append((item['kind'], item['pattern']))
        if mode == 'disable':
            raw_patterns = []
        elif mode == 'replace':
            raw_patterns = items
        else:
            raw_patterns = list(DEFAULT_LEAK_PATTERNS) + items
        patterns_source = mode

    compiled = []
    for kind, pattern in raw_patterns:
        try:
            compiled.append((kind, re.compile(pattern)))
        except re.error as exc:
            raise SystemExit(
                'Invalid regex in novelops.config.json knowledge.leak_patterns: %r (%s)' % (pattern, exc))

    disabled_kinds = resolve_disabled(set(VALID_LEAK_KINDS), kcfg.get('kinds_disabled'), 'knowledge.kinds_disabled')
    compiled = [(kind, pattern) for kind, pattern in compiled if kind not in disabled_kinds]

    config_summary = {
        'config_file': config_file_path(project),
        'keyword_tables_overridden': tables_overridden,
        'leak_patterns_source': patterns_source,
        'kinds_disabled': sorted(disabled_kinds),
    }
    return tables, compiled, disabled_kinds, config_summary


def build_character_beliefs(project):
    text = read_text(project / 'current_state.md')
    belief_text = extract_markdown_section(text, 'Character beliefs')
    beliefs = []
    for line in belief_text.splitlines():
        line = line.strip()
        if not line.startswith('- '):
            continue
        raw = line[2:].strip()
        character = raw.split('：', 1)[0].split(':', 1)[0].strip()
        beliefs.append({'character': character, 'statement': raw})
    return beliefs


def knowledge_violations(chapter_text, beliefs, tables=None, leak_patterns=None, disabled_kinds=None):
    tables = tables if tables is not None else DEFAULT_KEYWORD_TABLES
    leak_patterns = leak_patterns if leak_patterns is not None else LEAK_PATTERNS
    disabled_kinds = disabled_kinds or set()
    negation_tokens = tables['BELIEF_NEGATION_TOKENS']
    suspicion_tokens = tables['BELIEF_SUSPICION_TOKENS']
    confidence_tokens = tables['FACT_CONFIDENCE_TOKENS']
    findings = []
    sentences = split_sentences(chapter_text)
    if 'knowledge-leak' in disabled_kinds:
        belief_candidates = []
    else:
        belief_candidates = beliefs
    for sentence in sentences:
        for item in belief_candidates:
            statement = item['statement']
            if not any(token in statement for token in negation_tokens):
                continue
            character = item['character']
            if character and character not in sentence:
                continue
            if not any(token in sentence for token in confidence_tokens):
                continue
            if any(token in sentence for token in suspicion_tokens):
                continue
            findings.append({
                'severity': 'major',
                'type': 'knowledge-leak',
                'character': character,
                'fact': statement,
                'evidence': sentence,
                'reason': 'Current state marks this character as not yet knowing the relevant fact.',
                'suggested_fix': 'Downgrade certainty to suspicion, inference, or incomplete evidence.',
            })
            break

    for sentence in sentences:
        for kind, pattern in leak_patterns:
            if pattern.search(sentence):
                findings.append({
                    'severity': 'minor' if kind != 'omniscient-leak' else 'major',
                    'type': kind,
                    'character': None,
                    'fact': None,
                    'evidence': sentence,
                    'reason': 'Sentence suggests knowledge or narration scope that may exceed current POV constraints.',
                    'suggested_fix': 'Anchor the line in observable evidence or a named character perspective.',
                })
                break
    return findings


def build_report(project, chapter_file, config=None):
    project = require_project_markers(project)
    tables, leak_patterns, disabled_kinds, config_summary = resolve_knowledge_config(project, config)
    chapter_file = require_existing_file(chapter_file, 'Chapter file')
    chapter_text = read_text(chapter_file)
    beliefs = build_character_beliefs(project)
    violations = knowledge_violations(chapter_text, beliefs, tables, leak_patterns, disabled_kinds)
    chapter_num = parse_chapter_number(Path(chapter_file).stem) or parse_chapter_number(chapter_text) or None
    counts = {'critical': 0, 'major': 0, 'minor': 0, 'note': 0}
    for item in violations:
        counts[item['severity']] += 1
    ok = counts['critical'] == 0 and counts['major'] == 0
    return {
        'schema_version': 'novelops.knowledge-check.v1',
        'tool': 'knowledge_check',
        'generated_at': iso_now(),
        'project': str(project),
        'chapter': chapter_num,
        'chapter_file': str(chapter_file),
        'ok': ok,
        'summary': {
            'violation_count': len(violations),
            'counts': counts,
            'beliefs_loaded': len(beliefs),
            'config': config_summary,
        },
        'source_files': [
            str(chapter_file),
            str(project / 'current_state.md'),
            str(project / 'character_matrix.md'),
            str(project / 'chapter_summaries.md'),
        ],
        'violations': violations,
    }


def print_markdown(report):
    print('# Knowledge Check')
    print()
    print('- ok: %s' % ('yes' if report['ok'] else 'no'))
    print('- violations: %s' % report['summary']['violation_count'])
    print()
    print('## Violations')
    if not report['violations']:
        print('- none')
        return
    for item in report['violations']:
        print('- [%s/%s] %s' % (item['severity'], item['type'], item['reason']))
        print('  - evidence: %s' % item['evidence'])
        if item.get('character'):
            print('  - character: %s' % item['character'])
        if item.get('fact'):
            print('  - fact: %s' % item['fact'])
        print('  - suggested_fix: %s' % item['suggested_fix'])


def main():
    parser = argparse.ArgumentParser(description='Check chapter text for character knowledge-boundary and POV leaks.')
    parser.add_argument('--project', required=True)
    parser.add_argument('--chapter-file', required=True)
    parser.add_argument('--json', action='store_true')
    args = parser.parse_args()

    report = build_report(args.project, args.chapter_file)

    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print_markdown(report)


if __name__ == '__main__':
    main()
