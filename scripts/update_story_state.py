#!/usr/bin/env python3
import argparse
from pathlib import Path


def append_block(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        if path.stat().st_size > 0:
            f.write("\n")
        f.write(text.rstrip() + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="Append structured story-state updates.")
    parser.add_argument("--project", required=True)
    parser.add_argument("--chapter", required=True, type=int)
    parser.add_argument("--title", required=True)
    parser.add_argument("--summary", required=True)
    parser.add_argument("--state-change", action="append", default=[])
    parser.add_argument("--hook-open", action="append", default=[])
    parser.add_argument("--hook-advance", action="append", default=[])
    parser.add_argument("--hook-close", action="append", default=[])
    parser.add_argument("--relationship", action="append", default=[])
    parser.add_argument("--emotion", action="append", default=[])
    args = parser.parse_args()

    project = Path(args.project)
    summary_path = project / "chapter_summaries.md"
    hooks_path = project / "pending_hooks.md"
    matrix_path = project / "character_matrix.md"
    emotion_path = project / "emotional_arcs.md"

    chapter_block = [
        f"## Chapter {args.chapter} - {args.title}",
        f"- Summary: {args.summary}",
    ]

    if args.state_change:
        chapter_block.append("- State changes:")
        chapter_block.extend([f"  - {x}" for x in args.state_change])
    if args.hook_open:
        chapter_block.append("- Hooks opened:")
        chapter_block.extend([f"  - {x}" for x in args.hook_open])
    if args.hook_advance:
        chapter_block.append("- Hooks advanced:")
        chapter_block.extend([f"  - {x}" for x in args.hook_advance])
    if args.hook_close:
        chapter_block.append("- Hooks closed:")
        chapter_block.extend([f"  - {x}" for x in args.hook_close])
    if args.relationship:
        chapter_block.append("- Relationship changes:")
        chapter_block.extend([f"  - {x}" for x in args.relationship])
    if args.emotion:
        chapter_block.append("- Emotional arc changes:")
        chapter_block.extend([f"  - {x}" for x in args.emotion])

    append_block(summary_path, "\n".join(chapter_block))

    for hook in args.hook_open:
        append_block(hooks_path, f"- [OPEN] {hook} (opened: ch{args.chapter})")
    for hook in args.hook_advance:
        append_block(hooks_path, f"- [ADVANCED] {hook} (updated: ch{args.chapter})")
    for hook in args.hook_close:
        append_block(hooks_path, f"- [PAID OFF] {hook} (closed: ch{args.chapter})")
    for rel in args.relationship:
        append_block(matrix_path, f"- {rel} (updated: ch{args.chapter})")
    for emo in args.emotion:
        append_block(emotion_path, f"- {emo} (updated: ch{args.chapter})")

    print(f"Updated story state in {project}")


if __name__ == "__main__":
    main()
