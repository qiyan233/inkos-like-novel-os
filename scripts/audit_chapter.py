#!/usr/bin/env python3
import argparse
import json
import re
from pathlib import Path

SEVERITY_ORDER = {"critical": 0, "major": 1, "minor": 2, "note": 3}
TRANSITIONS = ["突然", "忽然", "仿佛", "竟然", "不禁", "猛地", "一时间", "at that moment", "suddenly", "instantly", "as if", "unexpectedly"]
REPORT_SPEAK = ["核心", "本质上", "某种意义上", "换句话说", "信息差", "底层逻辑", "情绪价值", "动机", "strategy", "framework"]
CROWD_CLICHES = ["全场震惊", "所有人都", "全都愣住了", "everyone gasped", "the whole room fell silent"]


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def tail_chapter_summaries(text: str, count: int = 3) -> str:
    matches = list(re.finditer(r"^##\s+Chapter\s+\d+.*$", text, flags=re.M))
    if not matches:
        return text.strip()
    sections = []
    for i, m in enumerate(matches):
        start = m.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        sections.append(text[start:end].strip())
    return "\n\n".join(sections[-count:])


def add(findings, severity, dimension, message, evidence=None):
    findings.append({
        "severity": severity,
        "dimension": dimension,
        "message": message,
        "evidence": evidence,
    })


def extract_bullets(text: str):
    return [m.group(1).strip() for m in re.finditer(r"^-\s+(.+)$", text, flags=re.M)]


def audit(project: Path, chapter_path: Path):
    chapter = read_text(chapter_path)
    current_state = read_text(project / "current_state.md")
    book_rules = read_text(project / "book_rules.md")
    pending_hooks = read_text(project / "pending_hooks.md")
    character_matrix = read_text(project / "character_matrix.md")
    chapter_summaries = read_text(project / "chapter_summaries.md")
    outline = read_text(project / "outline.md")

    findings = []
    fix_plan = []
    lower = chapter.lower()

    if not chapter.strip():
        add(findings, "critical", "chapter-input", "Chapter text is empty.")
        return findings, ["Provide chapter text before auditing."], "block"

    # 1. Repetition / fatigue
    for word in TRANSITIONS:
        count = chapter.count(word)
        if count >= 3:
            sev = "major" if count >= 5 else "minor"
            add(findings, sev, "repetition-fatigue", f"Transition word '{word}' appears {count} times.")
            fix_plan.append(f"Reduce repeated transition word '{word}'.")

    # 2. Report-speak
    report_hits = [w for w in REPORT_SPEAK if w in chapter]
    if report_hits:
        sev = "major" if len(report_hits) >= 3 else "minor"
        add(findings, sev, "report-speak", f"Abstract/report-like wording detected: {', '.join(report_hits[:6])}.")
        fix_plan.append("Replace abstract explanation with concrete action, sensory evidence, or dialogue.")

    # 3. Generic crowd response
    crowd_hits = [w for w in CROWD_CLICHES if w in chapter]
    if crowd_hits:
        add(findings, "minor", "crowd-cliche", f"Generic crowd-response cliché detected: {', '.join(crowd_hits)}.")
        fix_plan.append("Replace generic crowd reaction with 1-2 specific character reactions.")

    # 4. Paragraph monotony
    paras = [p.strip() for p in re.split(r"\n\s*\n", chapter) if p.strip()]
    if len(paras) >= 4:
        lens = [len(p) for p in paras]
        avg = sum(lens) / len(lens)
        close = sum(1 for x in lens if abs(x - avg) <= 25)
        if close / len(lens) >= 0.7:
            add(findings, "minor", "paragraph-monotony", "Paragraph lengths are too uniform; rhythm may feel machine-made.")
            fix_plan.append("Vary paragraph length and beat density.")

    # 5. Hook management
    open_hooks = [x for x in extract_bullets(pending_hooks) if "[OPEN]" in x]
    if len(open_hooks) >= 8 and len(chapter) < 8000:
        add(findings, "minor", "hook-management", f"There are {len(open_hooks)} open hooks; consider advancing at least one clearly.")
        fix_plan.append("Advance or partially pay off at least one existing hook.")

    # 6. Outline drift (very heuristic)
    outline_keywords = [w for w in re.findall(r"[\u4e00-\u9fffA-Za-z]{3,}", outline)[:40] if len(w) >= 3]
    if outline_keywords:
        hit = sum(1 for w in outline_keywords[:15] if w in chapter)
        if hit == 0 and len(chapter) > 1500:
            add(findings, "major", "outline-drift", "Chapter appears weakly connected to the current outline keywords.")
            fix_plan.append("Check whether the chapter still serves the planned arc or chapter function.")

    # 7. Current-state mismatch heuristic
    facts_section = current_state.split("## Character beliefs")[0]
    state_keywords = [w for w in re.findall(r"[\u4e00-\u9fffA-Za-z]{2,}", facts_section) if len(w) >= 2]
    if state_keywords:
        overlap = sum(1 for w in state_keywords[:20] if w in chapter)
        if overlap <= 1 and len(chapter) > 2000:
            add(findings, "major", "state-cohesion", "Chapter barely references current authoritative state; risk of drift.")
            fix_plan.append("Re-check current_state.md and ensure the chapter reflects active facts, conflicts, and pressures.")

    # 8. Character consistency heuristic
    rule_lines = extract_bullets(book_rules)
    protagonist_constraints = [x for x in rule_lines if "personality" in x.lower() or "constraint" in x.lower() or "prohibition" in x.lower()]
    if protagonist_constraints and len(chapter) > 1200:
        if any(k in chapter for k in ["突然心软", "轻易原谅", "毫无理由地退让"]):
            add(findings, "major", "character-consistency", "Potential protagonist lock break: sudden softness/retreat language found.")
            fix_plan.append("Re-check protagonist lock before keeping this turn in characterization.")

    # 9. Information boundary leak heuristic
    recent = tail_chapter_summaries(chapter_summaries)
    matrix_words = [w for w in re.findall(r"[\u4e00-\u9fffA-Za-z]{2,}", character_matrix) if len(w) >= 2]
    if ("不知道" in current_state or "不知" in current_state) and any(x in chapter for x in ["早就知道", "其实早已明白", "他当然知道真相"]):
        add(findings, "critical", "information-boundary", "Possible knowledge leak against current_state character-belief section.")
        fix_plan.append("Verify who is allowed to know the revealed fact, then patch the leaking line.")
    elif recent and any(x in chapter for x in ["所有真相", "完整计划", "幕后之人就是"]):
        add(findings, "minor", "information-boundary", "Check whether current POV earns this level of knowledge disclosure.")

    # 10. Dialogue authenticity heuristic
    quote_count = chapter.count("“") + chapter.count('"')
    if quote_count == 0 and len(chapter) > 1800:
        add(findings, "note", "dialogue-balance", "Long chapter with no dialogue; verify that this is intentional.")

    # 11. Telling vs dramatizing heuristic
    telling_hits = [w for w in ["他感到", "她感到", "他意识到", "她意识到", "he felt", "she felt"] if w in chapter]
    if len(telling_hits) >= 3:
        add(findings, "minor", "telling-vs-dramatizing", f"Repeated emotional labeling found: {', '.join(sorted(set(telling_hits)))}.")
        fix_plan.append("Replace some direct emotion labels with action or sensory cues.")

    # overall verdict
    if any(f["severity"] == "critical" for f in findings):
        overall = "block"
    elif any(f["severity"] == "major" for f in findings):
        overall = "revise"
    else:
        overall = "pass"

    findings.sort(key=lambda x: SEVERITY_ORDER[x["severity"]])
    if not fix_plan:
        fix_plan = ["No obvious high-severity issue found by heuristic audit. Do a human pass for subtle continuity and tone."]

    return findings, list(dict.fromkeys(fix_plan)), overall


def main():
    parser = argparse.ArgumentParser(description="Heuristic chapter auditor for inkos-like-novel-os projects.")
    parser.add_argument("--project", required=True)
    parser.add_argument("--chapter-file", required=True)
    parser.add_argument("--json", action="store_true", help="Output JSON instead of Markdown.")
    parser.add_argument("--write-report", action="store_true", help="Write report into project/reviews/.")
    args = parser.parse_args()

    project = Path(args.project)
    chapter_file = Path(args.chapter_file)
    findings, fix_plan, overall = audit(project, chapter_file)

    report = {
        "overall": overall,
        "chapter": str(chapter_file),
        "findings": findings,
        "minimal_fix_plan": fix_plan,
    }

    if args.write_report:
        reviews = project / "reviews"
        reviews.mkdir(parents=True, exist_ok=True)
        out = reviews / f"{chapter_file.stem}.audit.json"
        out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return

    print("# Chapter Audit")
    print()
    print("## Summary verdict")
    print(f"- overall: {overall}")
    print()
    print("## Findings")
    grouped = {k: [] for k in ["critical", "major", "minor", "note"]}
    for item in findings:
        grouped[item["severity"]].append(item)
    for sev in ["critical", "major", "minor", "note"]:
        print(f"### {sev}")
        if not grouped[sev]:
            print("- none")
        else:
            for item in grouped[sev]:
                print(f"- [{item['dimension']}] {item['message']}")
        print()
    print("## Minimal fix plan")
    for item in fix_plan:
        print(f"- {item}")


if __name__ == "__main__":
    main()
