#!/usr/bin/env python3
from pathlib import Path
import argparse, json, shutil, subprocess, sys
from runtime_layout import render_agent_profile, runtime_entries, transform_text

PROJECT_OWNED_PREFIXES = ('.progressive/project/', '.progressive/phases/', '.progressive/decisions/')
AGENT_SENTINEL='\n\n<!-- PROJECT-SPECIFIC-INSTRUCTIONS -->\n\n'
CLAUDE_SENTINEL='\n\n<!-- PROJECT-SPECIFIC-CLAUDE-INSTRUCTIONS -->\n\n'


def is_project_owned(rel):
    return any(rel.startswith(p) for p in PROJECT_OWNED_PREFIXES)


def framework_version(root):
    p=root/'VERSION'
    return p.read_text(encoding='utf-8').strip() if p.is_file() else 'unknown'


def profile_agent(root, profile):
    return root/'profiles'/profile/'AGENTS.md'


def rendered(src: Path, transform: bool=True) -> str:
    text=src.read_text(encoding='utf-8')
    return transform_text(text) if transform else text


def collect_ops(root, target, profile, update):
    ops=[]
    for src, rel, transform in runtime_entries(root, profile):
        if rel.as_posix() in {'AGENTS.md','CLAUDE.md'}:
            continue
        if update and is_project_owned(rel.as_posix()):
            continue
        ops.append((src, target/rel, transform))
    return ops


def merge_agents(root,target,profile,backup=False):
    dst=target/'AGENTS.md'; base=render_agent_profile(root,profile).rstrip()+'\n'
    if not dst.is_file(): dst.write_text(base,encoding='utf-8'); return
    old=dst.read_text(encoding='utf-8')
    if AGENT_SENTINEL in old:
        _,suffix=old.split(AGENT_SENTINEL,1); dst.write_text(base+AGENT_SENTINEL+suffix,encoding='utf-8'); return
    if old.rstrip()==base.rstrip(): return
    if backup:
        bp=target/'.progressive/adoption-backup/AGENTS.before.md'; bp.parent.mkdir(parents=True,exist_ok=True); bp.write_text(old,encoding='utf-8')
        dst.write_text(base+AGENT_SENTINEL+old,encoding='utf-8')
    else:
        raise RuntimeError('AGENTS.md is not a recognized Progressive profile/preserved adoption form; reconcile it before --update-framework')


def merge_claude(root,target,adopt=False):
    src=transform_text((root/'CLAUDE.md').read_text(encoding='utf-8')).rstrip()+'\n'; dst=target/'CLAUDE.md'
    if not dst.is_file(): dst.write_text(src,encoding='utf-8'); return
    old=dst.read_text(encoding='utf-8')
    if CLAUDE_SENTINEL in old:
        _,suffix=old.split(CLAUDE_SENTINEL,1); dst.write_text(src+CLAUDE_SENTINEL+suffix,encoding='utf-8'); return
    if old.rstrip()==src.rstrip(): return
    if adopt:
        bp=target/'.progressive/adoption-backup/CLAUDE.before.md'; bp.parent.mkdir(parents=True,exist_ok=True); bp.write_text(old,encoding='utf-8')
        dst.write_text(src+CLAUDE_SENTINEL+old,encoding='utf-8')
    else:
        raise RuntimeError('CLAUDE.md is not a recognized Progressive form/preserved adoption form; reconcile it before --update-framework')


def write_marker(root,target,profile,agent,state='ready'):
    m=target/'.progressive'; m.mkdir(parents=True,exist_ok=True)
    (m/'VERSION').write_text(framework_version(root)+'\n',encoding='utf-8')
    (m/'PROFILE').write_text(profile+'\n',encoding='utf-8')
    (m/'AGENT_TARGET').write_text(agent+'\n',encoding='utf-8')
    (m/'ADOPTION_STATE').write_text(state+'\n',encoding='utf-8')
    (m/'phases').mkdir(exist_ok=True); (m/'decisions').mkdir(exist_ok=True)


def write_entry(src,dst,transform):
    dst.parent.mkdir(parents=True,exist_ok=True)
    if transform:
        dst.write_text(transform_text(src.read_text(encoding='utf-8')),encoding='utf-8')
    else:
        shutil.copy2(src,dst)


def finalize(target):
    marker=target/'.progressive'
    if not (marker/'VERSION').is_file(): print('ERROR: not a marked Progressive Context project'); return 2
    audit=target/'.progressive/tools/audit.py'
    if not audit.is_file(): print('ERROR: .progressive/tools/audit.py missing'); return 2
    r=subprocess.run([sys.executable,str(audit),'--root',str(target)],text=True)
    if r.returncode: print('ERROR: adoption cannot finalize until runtime audit passes'); return r.returncode
    (marker/'ADOPTION_STATE').write_text('ready\n',encoding='utf-8')
    c=marker/'ADOPTION_CONFLICTS.json'
    if c.exists(): c.unlink()
    print('adoption finalized:',target); return 0


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('target'); ap.add_argument('--profile',choices=['personal','standalone'],default=None); ap.add_argument('--agent',choices=['codex','claude','both'])
    ap.add_argument('--update-framework',action='store_true'); ap.add_argument('--adopt-existing',action='store_true'); ap.add_argument('--finalize-adoption',action='store_true'); ap.add_argument('--dry-run',action='store_true')
    a=ap.parse_args(); root=Path(__file__).resolve().parents[1]; target=Path(a.target).expanduser().resolve()
    existing_agent=target/'.progressive/AGENT_TARGET'
    agent=a.agent or (existing_agent.read_text(encoding='utf-8').strip() if existing_agent.is_file() else 'both')
    if agent not in {'codex','claude','both'}: agent='both'
    existing_profile=target/'.progressive/PROFILE'
    if a.profile is None:
        if a.update_framework and existing_profile.is_file():
            a.profile=existing_profile.read_text(encoding='utf-8').strip()
            if a.profile not in {'personal','standalone'}: a.profile='personal'
        else:
            a.profile='personal'
    if sum(bool(x) for x in [a.update_framework,a.adopt_existing,a.finalize_adoption])>1:
        print('ERROR: choose only one of --update-framework, --adopt-existing, --finalize-adoption'); return 2
    if a.finalize_adoption: return finalize(target)
    marker=target/'.progressive/VERSION'
    if a.update_framework and not marker.is_file(): print('ERROR: --update-framework requires existing .progressive/VERSION marker'); return 2
    if a.adopt_existing and marker.is_file(): print('ERROR: already marked; use --update-framework'); return 2
    ops=collect_ops(root,target,a.profile,a.update_framework)

    if a.dry_run:
        mode='adopt' if a.adopt_existing else 'update' if a.update_framework else 'install'
        print(f'profile={a.profile} agent={agent} mode={mode} files={len(ops)+2}')
        print('MERGE',profile_agent(root,a.profile).relative_to(root),'-> AGENTS.md')
        print('MERGE CLAUDE.md -> CLAUDE.md')
        for src,dst,_ in ops:
            action='COPY'
            if dst.exists(): action='PRESERVE/RECONCILE' if a.adopt_existing else 'UPDATE' if a.update_framework else 'CONFLICT'
            print(action,src.relative_to(root),'->',dst)
        return 0

    if not a.adopt_existing and not a.update_framework:
        conflicts=[]
        if target.exists():
            # An empty directory is fine; any existing content means use adoption mode.
            conflicts=list(target.iterdir())
        if conflicts:
            print('ERROR: initial install requires an empty directory. Use --adopt-existing for an existing repository.')
            for p in conflicts[:20]: print(' -',p)
            return 2

    target.mkdir(parents=True,exist_ok=True)
    conflicts=[]
    try:
        merge_agents(root,target,a.profile,backup=a.adopt_existing)
        merge_claude(root,target,adopt=a.adopt_existing)
    except RuntimeError as exc:
        print('ERROR:',exc); return 2

    for src,dst,transform in ops:
        if a.adopt_existing and dst.exists():
            try:
                same = dst.read_text(encoding='utf-8') == rendered(src,transform)
            except UnicodeDecodeError:
                same = dst.read_bytes() == src.read_bytes()
            if same: continue
            rel=dst.relative_to(target).as_posix()
            if is_project_owned(rel): continue
            bp=target/'.progressive/adoption-backup'/rel; bp.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(dst,bp)
            conflicts.append(rel); continue
        write_entry(src,dst,transform)

    state='pending' if conflicts else 'ready'; write_marker(root,target,a.profile,agent,state)
    if conflicts:
        cp=target/'.progressive/ADOPTION_CONFLICTS.json'; cp.write_text(json.dumps({'schema':1,'conflicts':conflicts,'instructions':'Reconcile each path, then run --finalize-adoption.'},indent=2)+'\n',encoding='utf-8')
        print('adoption installed with unresolved framework collisions:')
        for rel in conflicts: print(' -',rel)
        print('Resolve them, then run tools/init_project.py <target> --finalize-adoption from Framework Source.')
    else:
        print('installed:',target)
    if a.profile=='personal':
        if agent in {'codex','both'}: print('NOTE Codex Personal: install/review Framework Source global/AGENTS.codex.md as ~/.codex/AGENTS.md separately.')
        if agent in {'claude','both'}: print('NOTE Claude Personal: install/review Framework Source global/CLAUDE.md as ~/.claude/CLAUDE.md separately.')
        print('NOTE: the installer never modifies home-level agent settings automatically.')
    else:
        print('NOTE: Standalone Project Runtime needs no user-level global instruction file.')
    return 0
if __name__=='__main__': raise SystemExit(main())
