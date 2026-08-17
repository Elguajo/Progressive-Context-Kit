#!/usr/bin/env python3
from pathlib import Path
import argparse,shutil,sys

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--root',default='.'); ap.add_argument('--apply',action='store_true'); a=ap.parse_args(); root=Path(a.root).resolve()
    src=root/'.agents/skills'; dst=root/'.claude/skills'; bad=[]
    for f in sorted(src.glob('*/SKILL.md')):
        target=dst/f.parent.name/'SKILL.md'
        if not target.is_file() or target.read_bytes()!=f.read_bytes(): bad.append((f,target))
    extra={p.parent.name for p in dst.glob('*/SKILL.md')}-{p.parent.name for p in src.glob('*/SKILL.md')}
    if a.apply:
        for s,t in bad: t.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(s,t)
        for name in extra: shutil.rmtree(dst/name)
        print(f'synchronized {len(bad)} changed/missing; removed {len(extra)} extra'); return
    if bad or extra:
        print('skill mirror drift detected');
        for s,t in bad: print('DRIFT',s.relative_to(root),'->',t.relative_to(root))
        for n in sorted(extra): print('EXTRA',n)
        sys.exit(1)
    print('skill mirrors: PASS')
if __name__=='__main__': main()
