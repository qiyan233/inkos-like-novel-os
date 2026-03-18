#!/usr/bin/env python3
import argparse
import json
import re
from pathlib import Path

from inkos_common import (
    extract_markdown_section,
    iso_now,
    parse_chapter_number,
    read_text,
    require_existing_file,
    require_project_markers,
    split_sentences,
)

LEAK_PATTERNS = [
    ('knowledge-leak', re.compile(r'(早就知道|当然知道|已经知道真相|其实早已明白|他当然知道真相|她当然知道真相)')),
    ('premature-certainty', re.compile(r'(真相就是|幕后之人就是|答案已经摆在眼前|已经确认|毫无疑问)')),
    ('omniscient-leak', re.compile(r'(没人知道的是|他不知道的是|她不知道的是|与此同时另一边|此时远在)')),
]

BELIEF_NEGATION_TOKENS = ['不知道', '不知', '尚未得知', '未察觉', '并不清楚', '还不清楚', '蒙在鼓里']
BELIEF_SUSPICION_TOKENS = ['怀疑', '猜测', '觉得', '似乎', '隐约', '推测']
FACT_CONFIDENCE_TOKENS = ['真相', '幕后', '内情', '计划', '身份', '替换者', '伪造', '原物']


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


def knowledge_violations(chapter_text, beliefs):
    findings = []
    sentences = split_sentences(chapter_text)
    for sentence in sentences:
        for item in beliefs:
            statement = item['statement']
            if not any(token in statement for token in BELIEF_NEGATION_TOKENS):
                continue
            character = item['character']
            if character and character not in sentence:
                continue
            if not any(token in sentence for token in FACT_CONFIDENCE_TOKENS):
                continue
            if any(token in sentence for token in BELIEF_SUSPICION_TOKENS):
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
        for kind, pattern in LEAK_PATTERNS:
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


def build_report(project, chapter_file):
    project = require_project_markers(project)
    chapter_file = require_existing_file(chapter_file, 'Chapter file')
    chapter_text = read_text(chapter_file)
    beliefs = build_character_beliefs(project)
    violations = knowledge_violations(chapter_text, beliefs)
    chapter_num = parse_chapter_number(Path(chapter_file).stem) or parse_chapter_number(chapter_text) or None
    counts = {'critical': 0, 'major': 0, 'minor': 0, 'note': 0}
    for item in violations:
        counts[item['severity']] += 1
    ok = counts['critical'] == 0 and counts['major'] == 0
    return {
        'schema_version': 'inkos.knowledge-check.v1',
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
