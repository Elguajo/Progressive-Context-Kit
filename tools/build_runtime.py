#!/usr/bin/env python3
from pathlib import Path
import argparse, shutil, zipfile
from runtime_layout import write_runtime

def framework_version(root):
    return (root / 'VERSION').read_text(encoding='utf-8').strip()

def main():
    ap = argparse.ArgumentParser(description='Build the minimal Project Runtime release.')
    ap.add_argument('--profile', choices=['standalone','personal'], default='standalone')
    ap.add_argument('--agent', choices=['codex','claude','both'], default='both')
    args = ap.parse_args()
    root = Path(__file__).resolve().parents[1]
    version = framework_version(root)
    dist = root / 'dist'
    dist.mkdir(exist_ok=True)
    suffix = '' if args.profile == 'standalone' else '-Personal'
    name = f'Progressive-Context-Project-Runtime{suffix}-v{version}'
    stage = dist / name
    if stage.exists(): shutil.rmtree(stage)
    write_runtime(root, stage, profile=args.profile, agent=args.agent)
    zip_path = dist / f'{name}.zip'
    if zip_path.exists(): zip_path.unlink()
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        for p in sorted(stage.rglob('*')):
            rel = p.relative_to(stage.parent).as_posix()
            if p.is_dir():
                if any(p.iterdir()):
                    continue
                info = zipfile.ZipInfo(rel.rstrip('/') + '/', date_time=(1980, 1, 1, 0, 0, 0))
                info.compress_type = zipfile.ZIP_STORED
                info.external_attr = 0o40755 << 16
                zf.writestr(info, b'')
                continue
            if not p.is_file():
                continue
            info = zipfile.ZipInfo(rel, date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            zf.writestr(info, p.read_bytes(), compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)
    print(zip_path)

if __name__ == '__main__':
    main()
