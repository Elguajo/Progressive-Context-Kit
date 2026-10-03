#!/usr/bin/env python3
from pathlib import Path
import argparse, difflib, hashlib, json, shutil, subprocess, sys, tempfile
from runtime_layout import INSTRUCTION_BASE_FILE, PROJECT_INSTRUCTIONS_SENTINEL, render_agent_profile, runtime_entries, transform_text, write_instruction_base

PROJECT_OWNED_PREFIXES = ('.progressive/project/', '.progressive/phases/', '.progressive/completions/', '.progressive/decisions/')
AGENT_SENTINEL=PROJECT_INSTRUCTIONS_SENTINEL
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


def known_profile_suffix(root,old,profile):
    """Match exact historical framework prefixes; never infer ownership from a title."""
    catalog=root/'tools/legacy_agent_profiles.json'
    if not catalog.is_file(): return None
    try:
        data=json.loads(catalog.read_text(encoding='utf-8'))
        if data.get('schema')!=1: raise ValueError('unsupported schema')
        entries=data['profiles'][profile]
        for entry in entries:
            length=entry['chars']
            if length<=0 or length>len(old): continue
            prefix=old[:length]
            if hashlib.sha256(prefix.encode('utf-8')).hexdigest()!=entry['sha256']: continue
            suffix=old[length:]
            # A known prefix must end at a line boundary, not halfway through a user edit.
            if suffix and not suffix.startswith('\n'): continue
            return suffix if suffix.strip() else ''
    except (KeyError,TypeError,ValueError) as exc:
        raise RuntimeError('invalid legacy agent profile catalog: '+str(exc)) from exc
    return None


def instruction_conflict(name,expected,actual):
    diff=''.join(difflib.unified_diff(
        (expected.rstrip()+'\n').splitlines(keepends=True),
        (actual.rstrip()+'\n').splitlines(keepends=True),
        fromfile=name+' (proposed standard prefix)',tofile=name+' (existing text)'))
    return RuntimeError(
        name+' is not a recognized Progressive framework prefix.\n'
        'Reconcile intentional local rules into the project-specific section before retrying.\n'
        'This diff compares the proposed standard with existing text; older framework differences may appear.\n'+diff)


def read_instruction_base(target,original=None):
    if original is not None:
        # Explicit original Runtime, not a guessed closest historical profile.
        bases={}
        for name,sentinel in (('AGENTS.md',AGENT_SENTINEL),('CLAUDE.md',CLAUDE_SENTINEL)):
            text=(original/name).read_text(encoding='utf-8')
            if sentinel in text:
                text,suffix=text.split(sentinel,1)
                if suffix.strip(): raise RuntimeError('--instruction-base must contain pristine instructions, without local suffixes')
            bases[name]=text.rstrip()+'\n'
        return bases
    path=target/'.progressive'/INSTRUCTION_BASE_FILE
    if not path.is_file(): return {}
    try:
        data=json.loads(path.read_text(encoding='utf-8'))
        installed=(target/'.progressive/PROFILE').read_text(encoding='utf-8').strip()
        if data['schema']!=1 or data['profile']!=installed: raise ValueError('schema/profile mismatch')
        bases=data['files']
        if not isinstance(bases,dict) or any(not isinstance(bases.get(name),str) or not bases[name].strip()
                                            for name in ('AGENTS.md','CLAUDE.md')):
            raise ValueError('missing instruction originals')
        return bases
    except (KeyError,TypeError,ValueError) as exc:
        raise RuntimeError('Invalid '+INSTRUCTION_BASE_FILE+': '+str(exc)) from exc


def merge_instruction_prefix(name,original,local,updated):
    """Conservatively merge independent line edits; never choose a side on overlap."""
    original=original.rstrip()+'\n'; local=local.rstrip()+'\n'; updated=updated.rstrip()+'\n'
    if local==original: return updated
    if updated==original or local==updated: return local
    base_lines=original.splitlines(keepends=True)
    def edits(text):
        lines=text.splitlines(keepends=True)
        result=[]
        for tag,a,b,c,d in difflib.SequenceMatcher(None,base_lines,lines,autojunk=False).get_opcodes():
            if tag=='equal': continue
            if tag=='replace' and b-a==d-c:
                # Separate adjacent one-to-one replacements so matching edits can be deduplicated.
                result.extend((a+i,a+i+1,[line]) for i,line in enumerate(lines[c:d]) if line!=base_lines[a+i])
            else: result.append((a,b,lines[c:d]))
        return result
    user_edits=edits(local); upstream_edits=edits(updated)
    for a,b,replacement in user_edits:
        for c,d,other in upstream_edits:
            if (a,b,replacement)==(c,d,other): continue
            overlap=max(a,c)<min(b,d)
            # Insertions touching a changed span have ambiguous ordering/intent.
            overlap=overlap or (a==b and c<=a<=d) or (c==d and a<=c<=b)
            if overlap:
                raise RuntimeError(name+' has overlapping local/framework edits; automatic merge stopped.\n'+
                                   str(instruction_conflict(name,updated,local)))
    combined=user_edits+[edit for edit in upstream_edits if edit not in user_edits]
    for start,end,replacement in sorted(combined,key=lambda edit:(edit[0],edit[1]),reverse=True):
        base_lines[start:end]=replacement
    return ''.join(base_lines)


def agents_merge_text(root,target,profile,adopt=False,bases=None):
    base=render_agent_profile(root,profile).rstrip()+'\n'
    dst=target/'AGENTS.md'
    if not dst.is_file(): return base+AGENT_SENTINEL
    old=dst.read_text(encoding='utf-8')
    marker=target/'.progressive/PROFILE'
    installed=marker.read_text(encoding='utf-8').strip() if marker.is_file() else profile
    if installed not in {'personal','standalone'}: installed=profile
    if AGENT_SENTINEL in old:
        prefix,suffix=old.split(AGENT_SENTINEL,1)
        if bases and 'AGENTS.md' in bases:
            base=merge_instruction_prefix('AGENTS.md',bases['AGENTS.md'],prefix,base)
            return base+AGENT_SENTINEL+suffix
        installed_base=render_agent_profile(root,installed).rstrip()
        if prefix.rstrip()!=installed_base and known_profile_suffix(root,prefix,installed)!='':
            raise instruction_conflict('AGENTS.md',base,prefix)
        return base+AGENT_SENTINEL+suffix
    if not adopt and bases and 'AGENTS.md' in bases:
        return merge_instruction_prefix('AGENTS.md',bases['AGENTS.md'],old,base)+AGENT_SENTINEL
    if old.rstrip()==base.rstrip(): return base+AGENT_SENTINEL
    suffix=known_profile_suffix(root,old,installed)
    if suffix is not None: return base+AGENT_SENTINEL+suffix
    if adopt: return base+AGENT_SENTINEL+old
    raise instruction_conflict('AGENTS.md',base,old)


def merge_agents(root,target,profile,backup=False):
    dst=target/'AGENTS.md'
    merged=agents_merge_text(root,target,profile,adopt=backup)
    if backup and dst.is_file():
        old=dst.read_text(encoding='utf-8')
        if AGENT_SENTINEL not in old and old.rstrip()!=render_agent_profile(root,profile).rstrip():
            bp=target/'.progressive/adoption-backup/AGENTS.before.md'; bp.parent.mkdir(parents=True,exist_ok=True); bp.write_text(old,encoding='utf-8')
    dst.write_text(merged,encoding='utf-8')


def claude_merge_text(root,target,adopt=False,bases=None):
    src=transform_text((root/'CLAUDE.md').read_text(encoding='utf-8')).rstrip()+'\n'; dst=target/'CLAUDE.md'
    if not dst.is_file(): return src
    old=dst.read_text(encoding='utf-8')
    if CLAUDE_SENTINEL in old:
        prefix,suffix=old.split(CLAUDE_SENTINEL,1)
        if bases and 'CLAUDE.md' in bases:
            src=merge_instruction_prefix('CLAUDE.md',bases['CLAUDE.md'],prefix,src)
        elif prefix.rstrip()!=src.rstrip(): raise instruction_conflict('CLAUDE.md',src,prefix)
        return src+CLAUDE_SENTINEL+suffix
    if not adopt and bases and 'CLAUDE.md' in bases:
        return merge_instruction_prefix('CLAUDE.md',bases['CLAUDE.md'],old,src)
    if old.rstrip()==src.rstrip(): return src
    if adopt: return src+CLAUDE_SENTINEL+old
    raise instruction_conflict('CLAUDE.md',src,old)


def merge_claude(root,target,adopt=False):
    dst=target/'CLAUDE.md'; merged=claude_merge_text(root,target,adopt)
    if adopt and dst.is_file():
        old=dst.read_text(encoding='utf-8')
        if CLAUDE_SENTINEL not in old and old.rstrip()!=transform_text((root/'CLAUDE.md').read_text(encoding='utf-8')).rstrip():
            bp=target/'.progressive/adoption-backup/CLAUDE.before.md'; bp.parent.mkdir(parents=True,exist_ok=True); bp.write_text(old,encoding='utf-8')
    dst.write_text(merged,encoding='utf-8')


def backup_update_instructions(target,plans):
    """Snapshot both entrypoints before replacement, preserving original bytes and earlier backups."""
    existing=[target/name for name in plans if (target/name).is_file()]
    if not any(path.read_bytes()!=plans[path.name].encode('utf-8') for path in existing): return None
    parent=target/'.progressive/update-backup'; parent.mkdir(parents=True,exist_ok=True)
    backup=Path(tempfile.mkdtemp(prefix='instructions-',dir=parent))
    for path in existing: shutil.copy2(path,backup/path.name)
    baseline=target/'.progressive'/INSTRUCTION_BASE_FILE
    if baseline.is_file(): shutil.copy2(baseline,backup/INSTRUCTION_BASE_FILE)
    return backup


def write_marker(root,target,profile,agent,state='ready'):
    m=target/'.progressive'; m.mkdir(parents=True,exist_ok=True)
    (m/'VERSION').write_text(framework_version(root)+'\n',encoding='utf-8')
    (m/'PROFILE').write_text(profile+'\n',encoding='utf-8')
    (m/'AGENT_TARGET').write_text(agent+'\n',encoding='utf-8')
    (m/'ADOPTION_STATE').write_text(state+'\n',encoding='utf-8')
    write_instruction_base(root,target,profile)
    (m/'phases').mkdir(exist_ok=True); (m/'completions').mkdir(exist_ok=True); (m/'decisions').mkdir(exist_ok=True)


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
    ap.add_argument('--instruction-base',type=Path,help='Original pristine Runtime directory for legacy three-way instruction merging')
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
    if a.instruction_base is not None and not a.update_framework:
        print('ERROR: --instruction-base requires --update-framework'); return 2
    marker=target/'.progressive/VERSION'
    if a.update_framework and not marker.is_file(): print('ERROR: --update-framework requires existing .progressive/VERSION marker'); return 2
    if a.adopt_existing and marker.is_file(): print('ERROR: already marked; use --update-framework'); return 2
    ops=collect_ops(root,target,a.profile,a.update_framework)
    if a.update_framework:
        # Fail before any write, including a successful-looking dry run on unsafe instructions.
        try:
            bases=read_instruction_base(target,a.instruction_base.expanduser().resolve() if a.instruction_base else None)
            instruction_plans={'AGENTS.md':agents_merge_text(root,target,a.profile,bases=bases),
                               'CLAUDE.md':claude_merge_text(root,target,bases=bases)}
        except (RuntimeError,OSError) as exc:
            print('ERROR:',exc)
            print('No files were changed.'); return 2

    if a.dry_run:
        mode='adopt' if a.adopt_existing else 'update' if a.update_framework else 'install'
        print(f'profile={a.profile} agent={agent} mode={mode} files={len(ops)+2}')
        print('MERGE',profile_agent(root,a.profile).relative_to(root),'-> AGENTS.md')
        print('MERGE CLAUDE.md -> CLAUDE.md')
        if a.update_framework:
            for name,text in instruction_plans.items():
                path=target/name; old=path.read_text(encoding='utf-8') if path.is_file() else ''
                print(''.join(difflib.unified_diff(old.splitlines(keepends=True),text.splitlines(keepends=True),
                                                 fromfile=name+' (existing)',tofile=name+' (merged)')),end='')
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
        if a.update_framework:
            backup=backup_update_instructions(target,instruction_plans)
            if backup: print('instruction backup:',backup)
            for name,text in instruction_plans.items():
                (target/name).write_text(text,encoding='utf-8')
        else:
            merge_agents(root,target,a.profile,backup=a.adopt_existing)
            merge_claude(root,target,adopt=a.adopt_existing)
    except (RuntimeError,OSError) as exc:
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
