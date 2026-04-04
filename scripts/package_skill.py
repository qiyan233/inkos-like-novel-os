#!/usr/bin/env python3
import argparse
import shutil
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SKILL_NAME = 'inkos-like-novel-os'
DEFAULT_OUTDIR = ROOT.parent.parent / 'dist'
IGNORE_NAMES = {
    '.git',
    '.smoke-work',
    '.package-work',
    'node_modules',
}
IGNORE_FILE_SUFFIXES = {
    '.pyc',
}
IGNORE_FILE_NAMES = {
    '.DS_Store',
}


def normalize_tag(tag):
    tag = (tag or '').replace('\r', '').replace('\n', '').strip()
    if tag and not tag.startswith('v'):
        tag = 'v' + tag
    return tag


def default_version_suffix():
    version_file = ROOT / 'VERSION'
    if not version_file.exists():
        return ''
    return normalize_tag(version_file.read_text(encoding='utf-8'))


def should_skip(path):
    name = path.name
    if name in IGNORE_NAMES:
        return True
    if name.startswith('inkos-smoke-'):
        return True
    if name.startswith('inkos-package-'):
        return True
    if path.is_dir() and name == '__pycache__':
        return True
    if path.is_file() and (path.suffix in IGNORE_FILE_SUFFIXES or name in IGNORE_FILE_NAMES):
        return True
    return False


def copy_tree(src, dst):
    dst.mkdir(parents=True, exist_ok=True)
    for item in src.iterdir():
        if should_skip(item):
            continue
        target = dst / item.name
        if item.is_dir():
            copy_tree(item, target)
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(item, target)


def write_zip(stage_root, outfile):
    with zipfile.ZipFile(outfile, 'w', compression=zipfile.ZIP_DEFLATED) as zf:
        for path in sorted(stage_root.rglob('*')):
            if path.is_dir():
                continue
            arcname = path.relative_to(stage_root.parent)
            zf.write(path, arcname)


def package_skill(outdir='', version_suffix=''):
    outdir = Path(outdir) if outdir else DEFAULT_OUTDIR
    version_suffix = normalize_tag(version_suffix) if version_suffix else default_version_suffix()
    outdir.mkdir(parents=True, exist_ok=True)

    workdir = ROOT / '.package-work'
    shutil.rmtree(workdir, ignore_errors=True)
    workdir.mkdir(parents=True, exist_ok=True)
    try:
        stage_root = workdir / SKILL_NAME
        copy_tree(ROOT, stage_root)

        outfile = outdir / f'{SKILL_NAME}.skill'
        if outfile.exists():
            outfile.unlink()
        write_zip(stage_root, outfile)
        outputs = [str(outfile)]

        if version_suffix:
            versioned = outdir / f'{SKILL_NAME}-{version_suffix}.skill'
            if versioned.exists():
                versioned.unlink()
            shutil.copy2(outfile, versioned)
            outputs.append(str(versioned))
    finally:
        shutil.rmtree(workdir, ignore_errors=True)

    return outputs


def main():
    parser = argparse.ArgumentParser(description='Package the skill into a .skill zip.')
    parser.add_argument('outdir', nargs='?', default='')
    parser.add_argument('version_suffix', nargs='?', default='')
    args = parser.parse_args()

    for output in package_skill(args.outdir, args.version_suffix):
        print(output)


if __name__ == '__main__':
    main()
