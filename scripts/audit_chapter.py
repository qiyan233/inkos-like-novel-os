#!/usr/bin/env python3
import argparse
import json
import re
from pathlib import Path

from inkos_common import extract_bullets, extract_keywords, iso_now, latest_sections, read_text, write_json

SEVERITY_ORDER = {'critical': 0, 'major': 1, 'minor': 2, 'note': 3}
TRANSITIONS = ['突然', '忽然', '仿佛', '竟然', '不禁', '猛地', '一时间', 'at that moment', 'suddenly', 'instantly', 'as if', 'unexpectedly']
REPORT_SPEAK = ['核心', '本质上', '某种意义上', '换句话说', '信息差', '底层逻辑', '情绪价值', '动机', 'strategy', 'framework']
CROWD_CLICHES = ['全场震惊', '所有人都', '全都愣住了', 'everyone gasped', 'the whole room fell silent']
TIME_JUMPS = ['次日', '第二天', '当夜', '当天晚上', '数日后', '三日后', '一周后', 'later that day', 'the next day', 'hours later']
TELLING_PHRASES = ['他感到', '她感到', '他意识到', '她意识到', 'he felt', 'she felt']
KNOWLEDGE_LEAPS = ['所有真相', '完整计划', '幕后之人就是', '答案已经摆在眼前', '真相大白']
PROTAGONIST_LOCK_BREAKS = ['突然心软', '轻易原谅', '毫无理由地退让', '无条件相信', '主动坦白一切']
STATE_TURN_MARKERS = ['决定', '确认', '发现', '明白', '知道', '拿到', '失去', '暴露', '受伤', '怀疑', 'betrayed', 'revealed', 'decided']


def add(findings, rule_id, severity, dimension, message, evidence=None, repair_targets=None):
    findings.append({
        'rule_id': rule_id,
        'severity': severity,
        'dimension': dimension,
        'message': message,
        'evidence': evidence or [],
        'repair_targets': repair_targets or [],
    })


def finding_counts(findings):
    counts = {'critical': 0, 'major': 0, 'minor': 0, 'note': 0}
    for item in findings:
        counts[item['severity']] += 1
    return counts


def chapter_metrics(chapter):
    paras = [p.strip() for p in re.split(r'\n\s*\n', chapter) if p.strip()]
    return {
        'char_count': len(chapter),
        'paragraph_count': len(paras),
        'dialogue_quote_count': chapter.count('“') + chapter.count('"'),
        'time_jump_markers': sum(chapter.count(x) for x in TIME_JUMPS),
    }


def open_hook_keywords(pending_hooks):
    keywords = []
    open_hooks = [x for x in extract_bullets(pending_hooks) if '[OPEN]' in x]
    for hook in open_hooks:
        hook = re.sub(r'\[[^\]]+\]\s*', '', hook)
        hook = re.sub(r'\([^\)]*\)', '', hook)
        keywords.extend(extract_keywords(hook, min_len=2, limit=6))
    return open_hooks, list(dict.fromkeys(keywords))


def build_report(project, chapter_file):
    project = Path(project)
    chapter_file = Path(chapter_file)
    chapter = read_text(chapter_file)
    current_state = read_text(project / 'current_state.md')
    book_rules = read_text(project / 'book_rules.md')
    pending_hooks = read_text(project / 'pending_hooks.md')
    chapter_summaries = read_text(project / 'chapter_summaries.md')
    outline = read_text(project / 'outline.md')

    findings = []
    fix_plan = []
    rules_evaluated = []

    if not chapter.strip():
        add(findings, 'AUD-000', 'critical', 'chapter-input', 'Chapter text is empty.', repair_targets=['Provide chapter text before auditing.'])
        counts = finding_counts(findings)
        return {
            'schema_version': 'inkos.audit-report.v1',
            'tool': 'audit_chapter',
            'generated_at': iso_now(),
            'project': str(project),
            'chapter': str(chapter_file),
            'overall': 'block',
            'summary': {'counts': counts, 'finding_count': 1, 'rules_evaluated': []},
            'source_files': [str(chapter_file)],
            'chapter_metrics': chapter_metrics(chapter),
            'findings': findings,
            'minimal_fix_plan': ['Provide chapter text before auditing.'],
        }

    rules_evaluated.append('AUD-101')
    for word in TRANSITIONS:
        count = chapter.count(word)
        if count >= 3:
            sev = 'major' if count >= 5 else 'minor'
            add(findings, 'AUD-101', sev, 'repetition-fatigue', "Transition word '%s' appears %s times." % (word, count), evidence=[word], repair_targets=["Reduce repeated transition word '%s'." % word])
            fix_plan.append("Reduce repeated transition word '%s'." % word)

    rules_evaluated.append('AUD-102')
    report_hits = [w for w in REPORT_SPEAK if w in chapter]
    if report_hits:
        sev = 'major' if len(report_hits) >= 3 else 'minor'
        add(findings, 'AUD-102', sev, 'report-speak', 'Abstract/report-like wording detected: %s.' % ', '.join(report_hits[:6]), evidence=report_hits[:6], repair_targets=['Replace abstract explanation with concrete action, sensory evidence, or dialogue.'])
        fix_plan.append('Replace abstract explanation with concrete action, sensory evidence, or dialogue.')

    rules_evaluated.append('AUD-103')
    crowd_hits = [w for w in CROWD_CLICHES if w in chapter]
    if crowd_hits:
        add(findings, 'AUD-103', 'minor', 'crowd-cliche', 'Generic crowd-response cliché detected: %s.' % ', '.join(crowd_hits), evidence=crowd_hits, repair_targets=['Replace generic crowd reaction with 1-2 specific character reactions.'])
        fix_plan.append('Replace generic crowd reaction with 1-2 specific character reactions.')

    rules_evaluated.append('AUD-104')
    paras = [p.strip() for p in re.split(r'\n\s*\n', chapter) if p.strip()]
    if len(paras) >= 4:
        lens = [len(p) for p in paras]
        avg = sum(lens) / float(len(lens))
        close = sum(1 for x in lens if abs(x - avg) <= 25)
        if close / float(len(lens)) >= 0.7:
            add(findings, 'AUD-104', 'minor', 'paragraph-monotony', 'Paragraph lengths are too uniform; rhythm may feel machine-made.', repair_targets=['Vary paragraph length and beat density.'])
            fix_plan.append('Vary paragraph length and beat density.')

    rules_evaluated.append('AUD-105')
    open_hooks, hook_keywords = open_hook_keywords(pending_hooks)
    if len(open_hooks) >= 8 and len(chapter) < 8000:
        add(findings, 'AUD-105', 'minor', 'hook-overload', 'There are %s open hooks; consider advancing at least one clearly.' % len(open_hooks), evidence=open_hooks[:5], repair_targets=['Advance or partially pay off at least one existing hook.'])
        fix_plan.append('Advance or partially pay off at least one existing hook.')

    rules_evaluated.append('AUD-106')
    if len(open_hooks) >= 3 and len(chapter) > 1200 and hook_keywords:
        if not any(keyword in chapter for keyword in hook_keywords[:12]):
            add(findings, 'AUD-106', 'minor', 'hook-advancement', 'Chapter does not appear to touch any currently open hook keywords.', evidence=hook_keywords[:8], repair_targets=['Check whether this chapter should advance, delay, or intentionally isolate current open hooks.'])
            fix_plan.append('Check whether this chapter should advance, delay, or intentionally isolate current open hooks.')

    rules_evaluated.append('AUD-107')
    outline_keywords = extract_keywords(outline, min_len=3, limit=40)
    if outline_keywords:
        hit = sum(1 for w in outline_keywords[:15] if w in chapter)
        if hit == 0 and len(chapter) > 1500:
            add(findings, 'AUD-107', 'major', 'outline-drift', 'Chapter appears weakly connected to the current outline keywords.', evidence=outline_keywords[:10], repair_targets=['Check whether the chapter still serves the planned arc or chapter function.'])
            fix_plan.append('Check whether the chapter still serves the planned arc or chapter function.')

    rules_evaluated.append('AUD-108')
    facts_section = current_state.split('## Character beliefs')[0]
    state_keywords = extract_keywords(facts_section, min_len=2, limit=20)
    if state_keywords:
        overlap = sum(1 for w in state_keywords if w in chapter)
        if overlap <= 1 and len(chapter) > 2000:
            add(findings, 'AUD-108', 'major', 'state-cohesion', 'Chapter barely references current authoritative state; risk of drift.', evidence=state_keywords[:10], repair_targets=['Re-check current_state.md and ensure the chapter reflects active facts, conflicts, and pressures.'])
            fix_plan.append('Re-check current_state.md and ensure the chapter reflects active facts, conflicts, and pressures.')

    rules_evaluated.append('AUD-109')
    constraint_lines = [x for x in extract_bullets(book_rules) if re.search(r'不能|不得|不要|禁止|avoid|never|must not|do not|constraint|prohibition', x, flags=re.I)]
    lock_breaks = [x for x in PROTAGONIST_LOCK_BREAKS if x in chapter]
    if constraint_lines and lock_breaks:
        add(findings, 'AUD-109', 'major', 'protagonist-lock', 'Potential protagonist lock break language found.', evidence=lock_breaks + constraint_lines[:3], repair_targets=['Re-check protagonist lock before keeping this turn in characterization.'])
        fix_plan.append('Re-check protagonist lock before keeping this turn in characterization.')

    rules_evaluated.append('AUD-110')
    recent = latest_sections(chapter_summaries, r'^##\s+Chapter\s+\d+.*$', 3)
    if ('不知道' in current_state or '不知' in current_state) and any(x in chapter for x in ['早就知道', '其实早已明白', '他当然知道真相']):
        add(findings, 'AUD-110', 'critical', 'information-boundary', 'Possible knowledge leak against current_state character-belief section.', repair_targets=['Verify who is allowed to know the revealed fact, then patch the leaking line.'])
        fix_plan.append('Verify who is allowed to know the revealed fact, then patch the leaking line.')
    elif recent and any(x in chapter for x in KNOWLEDGE_LEAPS):
        add(findings, 'AUD-110', 'minor', 'information-boundary', 'Check whether current POV earns this level of knowledge disclosure.', evidence=[x for x in KNOWLEDGE_LEAPS if x in chapter], repair_targets=['Check whether current POV has actually earned this reveal level.'])
        fix_plan.append('Check whether current POV has actually earned this reveal level.')

    rules_evaluated.append('AUD-111')
    jump_hits = [x for x in TIME_JUMPS if x in chapter]
    if len(jump_hits) >= 2 and len(chapter) < 2500:
        sev = 'major' if len(jump_hits) >= 3 else 'minor'
        add(findings, 'AUD-111', sev, 'timeline-continuity', 'Multiple time-jump markers appear in a compact chapter; verify timeline coherence.', evidence=jump_hits, repair_targets=['Check whether time progression is clear and earned between scene beats.'])
        fix_plan.append('Check whether time progression is clear and earned between scene beats.')

    rules_evaluated.append('AUD-112')
    quote_count = chapter.count('“') + chapter.count('"')
    if quote_count == 0 and len(chapter) > 1800:
        add(findings, 'AUD-112', 'note', 'dialogue-balance', 'Long chapter with no dialogue; verify that this is intentional.')

    rules_evaluated.append('AUD-113')
    telling_hits = [w for w in TELLING_PHRASES if w in chapter]
    if len(telling_hits) >= 3:
        add(findings, 'AUD-113', 'minor', 'telling-vs-dramatizing', 'Repeated emotional labeling found: %s.' % ', '.join(sorted(set(telling_hits))), evidence=sorted(set(telling_hits)), repair_targets=['Replace some direct emotion labels with action or sensory cues.'])
        fix_plan.append('Replace some direct emotion labels with action or sensory cues.')

    rules_evaluated.append('AUD-114')
    turn_hits = [w for w in STATE_TURN_MARKERS if w in chapter]
    if len(turn_hits) >= 4:
        add(findings, 'AUD-114', 'note', 'state-update-pressure', 'Chapter contains multiple state-turn markers; remember to update truth files after acceptance.', evidence=turn_hits[:8], repair_targets=['Prepare state updates for summaries, hooks, relationships, and emotional arcs.'])
        fix_plan.append('Prepare state updates for summaries, hooks, relationships, and emotional arcs.')

    findings.sort(key=lambda x: (SEVERITY_ORDER[x['severity']], x['rule_id']))
    dedup_fix_plan = []
    seen = set()
    for item in fix_plan:
        if item in seen:
            continue
        seen.add(item)
        dedup_fix_plan.append(item)
    if not dedup_fix_plan:
        dedup_fix_plan = ['No obvious high-severity issue found by heuristic audit. Do a human pass for subtle continuity and tone.']

    counts = finding_counts(findings)
    if counts['critical']:
        overall = 'block'
    elif counts['major']:
        overall = 'revise'
    else:
        overall = 'pass'

    return {
        'schema_version': 'inkos.audit-report.v1',
        'tool': 'audit_chapter',
        'generated_at': iso_now(),
        'project': str(project),
        'chapter': str(chapter_file),
        'overall': overall,
        'summary': {
            'counts': counts,
            'finding_count': len(findings),
            'rules_evaluated': rules_evaluated,
        },
        'source_files': [
            str(chapter_file),
            str(project / 'current_state.md'),
            str(project / 'book_rules.md'),
            str(project / 'pending_hooks.md'),
            str(project / 'chapter_summaries.md'),
            str(project / 'outline.md'),
        ],
        'chapter_metrics': chapter_metrics(chapter),
        'findings': findings,
        'minimal_fix_plan': dedup_fix_plan,
    }


def main():
    parser = argparse.ArgumentParser(description='Heuristic chapter auditor for inkos-like-novel-os projects.')
    parser.add_argument('--project', required=True)
    parser.add_argument('--chapter-file', required=True)
    parser.add_argument('--json', action='store_true', help='Output JSON instead of Markdown.')
    parser.add_argument('--write-report', action='store_true', help='Write report into project/reviews/.')
    args = parser.parse_args()

    report = build_report(args.project, args.chapter_file)

    if args.write_report:
        reviews = Path(args.project) / 'reviews'
        reviews.mkdir(parents=True, exist_ok=True)
        out = reviews / ('%s.audit.json' % Path(args.chapter_file).stem)
        report['report_path'] = str(out)
        write_json(out, report)

    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return

    print('# Chapter Audit')
    print()
    print('## Summary verdict')
    print('- overall: %s' % report['overall'])
    print()
    print('## Summary counts')
    for sev in ['critical', 'major', 'minor', 'note']:
        print('- %s: %s' % (sev, report['summary']['counts'][sev]))
    print()
    print('## Findings')
    grouped = {'critical': [], 'major': [], 'minor': [], 'note': []}
    for item in report['findings']:
        grouped[item['severity']].append(item)
    for sev in ['critical', 'major', 'minor', 'note']:
        print('### %s' % sev)
        if not grouped[sev]:
            print('- none')
        else:
            for item in grouped[sev]:
                print('- [%s/%s] %s' % (item['rule_id'], item['dimension'], item['message']))
        print()
    print('## Minimal fix plan')
    for item in report['minimal_fix_plan']:
        print('- %s' % item)


if __name__ == '__main__':
    main()
