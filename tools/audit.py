#!/usr/bin/env python3
from pathlib import Path
import argparse, hashlib, json, re
from common import chars, current_phase, read
from sync_profiles import compose as compose_standalone, active_profile, root_matches_profile
from behavior_contract import validate as validate_behavior_contract
from framework_contract import validate as validate_framework_contract
from duplication_audit import validate as validate_duplication
from context_compile import completion_bridge, completion_record

EXPECTED_FALLBACK={'ROLE','TASK_CLASSIFICATION','REPOSITORY_GROUNDING','ENGINEERING_PRINCIPLES','DECISION_WORKFLOW','CODE_REVIEW_MODE','IMPLEMENTATION','VALIDATION_LOOP','SAFETY_AND_APPROVALS','DOCUMENTATION_UPDATE_APPROVAL','FINAL_REPORT','COMMUNICATION_STYLE'}
EXPECTED_SKILLS={'architecture-decision','code-review','documentation-governance','project-bootstrap','existing-project-adoption','tooling-bootstrap','project-doctor','security-sensitive-change','session-handoff','systematic-debugging','workflow-audit','implementation-execution'}
ALLOWED_SKILL_ACTIVATION={'automatic','explicit','both'}
EXPECTED_TOOLS={'semble','serena','rtk','superpowers','gstack','context7','github_spec_kit'}
# Mirrors the literal figures hardcoded in verify_profiles (kept literal there since a
# Behavior Contract anchor pins that exact substring); used here to check docs don't drift.
BUDGET_GLOBAL=5500; BUDGET_ROUTER=3600; BUDGET_COMBINED=9100; BUDGET_STANDALONE=9300
RELEASE_VERSION_DOCS=['README.md','README_RU.md','docs/human/GETTING_STARTED.md','docs/human/GETTING_STARTED.ru.md']
REQUIRED=[
'AGENTS.md','CLAUDE.md','global/AGENTS.codex.md','global/CLAUDE.md','profiles/personal/AGENTS.md','profiles/standalone/AGENTS.md',
'docs/system/LAYER_OWNERSHIP.md','docs/system/LINEAGE.md','docs/system/TOOL_ROUTING.md',
'integrations/TOOL_REGISTRY.json','integrations/PROFILES.md',
'docs/project/TOOLING_STATUS.json','docs/project/CONTEXT_MANIFEST.json',
'docs/migration/COVERAGE_MATRIX.json','docs/migration/BEHAVIOR_CONTRACT.json','docs/migration/BEHAVIOR_IDS.sha256','docs/migration/ORIGINAL_CUSTOM_INSTRUCTIONS.txt','docs/migration/ORIGINAL_CUSTOM_INSTRUCTIONS.sha256',
'docs/contracts/FRAMEWORK_CONTRACT.json','docs/contracts/FRAMEWORK_IDS.sha256','docs/contracts/SKILL_ACTIVATION.md',
'docs/evals/static/BEHAVIOR_SCENARIOS.json','docs/evals/static/FRAMEWORK_SCENARIOS.json','docs/evals/agent/MODEL_EVAL_PROTOCOL.md',
'templates/PHASE.template.md','templates/CONTEXT_MANIFEST.template.json',
'tools/context_report.py','tools/context_compile.py','tools/runtime_layout.py','tools/runtime_audit.py','tools/build_runtime.py','tools/build_release.py','tools/behavior_contract.py','tools/framework_contract.py','tools/duplication_audit.py','tools/sync_profiles.py','tools/sync_skills.py','tools/tooling_status.py','tools/tooling_bootstrap.py','tools/init_project.py']

def fail_if(c,errors,m):
    if c: errors.append(m)

def verify_archive_hash(root,errors):
    try:
        expected=(root/'docs/migration/ORIGINAL_CUSTOM_INSTRUCTIONS.sha256').read_text().split()[0].lower(); actual=hashlib.sha256((root/'docs/migration/ORIGINAL_CUSTOM_INSTRUCTIONS.txt').read_bytes()).hexdigest(); fail_if(actual!=expected,errors,'archived Custom Instructions SHA-256 mismatch')
    except Exception as exc: errors.append('cannot verify archived Custom Instructions hash: '+str(exc))

def verify_profiles(root,errors):
    g=root/'global/AGENTS.codex.md'; gc=root/'global/CLAUDE.md'; p=root/'profiles/personal/AGENTS.md'; s=root/'profiles/standalone/AGENTS.md'
    fail_if(chars(g)>5500,errors,'global/AGENTS.codex.md exceeds 5500-char hard budget')
    fail_if(chars(gc)>5500,errors,'global/CLAUDE.md exceeds 5500-char hard budget')
    fail_if(chars(p)>3600,errors,'personal repo router exceeds 3600-char hard budget')
    fail_if(chars(g)+chars(p)>9100,errors,'Personal Codex always-loaded layers exceed 9100 chars')
    fail_if(chars(gc)+chars(p)>9100,errors,'Personal Claude always-loaded layers exceed 9100 chars')
    fail_if(chars(s)>9300,errors,'Standalone AGENTS exceeds 9300-char hard budget')
    profile=active_profile(root); fail_if(not root_matches_profile(root,profile),errors,f'root AGENTS.md must contain active {profile} profile as canonical prefix')
    fail_if(s.read_text(encoding='utf-8')!=compose_standalone(root),errors,'profiles/standalone/AGENTS.md drifted from generated global+personal composition')
    claude=read(root/'CLAUDE.md')
    fail_if('@AGENTS.md' not in claude,errors,'CLAUDE.md must import active root @AGENTS.md')
    fail_if('@profiles/standalone/AGENTS.md' in claude,errors,'CLAUDE.md must not import Standalone directly; that duplicates universal behavior in Personal Claude')
    gct=read(gc)
    for anchor in ['Silently classify work before acting','Pasted code without a question is a review request','## Safety and approvals','## Completion']:
        fail_if(anchor not in gct,errors,'global/CLAUDE.md missing universal behavior anchor: '+anchor)

def verify_migration_coverage(root,errors,warns):
    archived=read(root/'docs/migration/ORIGINAL_CUSTOM_INSTRUCTIONS.txt'); parsed=set(re.findall(r'<([A-Z_]+)>',archived)) or EXPECTED_FALLBACK
    try: sections=json.loads(read(root/'docs/migration/COVERAGE_MATRIX.json')).get('sections',{})
    except Exception as exc: errors.append('invalid coverage matrix: '+str(exc)); return
    missing=parsed-set(sections); extra=set(sections)-parsed
    if missing: errors.append('uncovered original sections: '+', '.join(sorted(missing)))
    if extra: warns.append('unexpected coverage sections: '+', '.join(sorted(extra)))
    for name,targets in sections.items():
        if not isinstance(targets,list) or not targets: errors.append(f'{name} has no coverage target'); continue
        for rel in targets:
            if not (root/rel).is_file(): errors.append(f'{name} coverage target missing: {rel}')

def verify_skills(root,errors):
    src={p.parent.name:p for p in (root/'.agents/skills').glob('*/SKILL.md')}; dst={p.parent.name:p for p in (root/'.claude/skills').glob('*/SKILL.md')}
    if set(src)!=EXPECTED_SKILLS: errors.append('Codex Skill set mismatch: expected '+', '.join(sorted(EXPECTED_SKILLS)))
    if set(src)!=set(dst): errors.append('Codex/Claude Skill sets differ')
    for name in set(src)&set(dst):
        if src[name].read_bytes()!=dst[name].read_bytes(): errors.append('Skill mirror drift: '+name)
        text=read(src[name]); mn=re.search(r'^name:\s*(.+)$',text,re.M); md=re.search(r'^description:\s*(.+)$',text,re.M); ma=re.search(r'^activation:\s*(.+)$',text,re.M)
        if not mn or mn.group(1).strip()!=name: errors.append('Skill frontmatter name mismatch: '+name)
        if not md or not md.group(1).strip(): errors.append('Skill description missing: '+name)
        if not ma or not ma.group(1).strip():
            errors.append('Skill activation missing: '+name)
        elif ma.group(1).strip() not in ALLOWED_SKILL_ACTIVATION:
            errors.append('Skill activation invalid: '+name+'='+ma.group(1).strip())

def verify_tooling(root,errors):
    try:
        reg=json.loads(read(root/'integrations/TOOL_REGISTRY.json')); status=json.loads(read(root/'docs/project/TOOLING_STATUS.json'))
    except Exception as exc: errors.append('invalid tooling JSON: '+str(exc)); return
    tools=reg.get('tools',{})
    if set(tools)!=EXPECTED_TOOLS: errors.append('Tool Registry set mismatch')
    for key,t in tools.items():
        if not t.get('brand') or not t.get('capability'): errors.append(f'tool registry incomplete: {key}')
        if not str(t.get('official','')).startswith('https://'): errors.append(f'tool official source missing/invalid: {key}')
        if key not in status.get('tools',{}): errors.append(f'tooling status missing tool: {key}')
    profiles=read(root/'integrations/PROFILES.md')
    for brand in ['Semble','Serena','RTK','Superpowers','gstack','Context7','GitHub Spec Kit']:
        if brand not in profiles: errors.append('PROFILES missing preferred brand: '+brand)

def verify_token_budgets_doc(root,errors):
    doc=read(root/'docs/TOKEN_BUDGETS.md')
    for n in {BUDGET_GLOBAL,BUDGET_ROUTER,BUDGET_COMBINED,BUDGET_STANDALONE}:
        fail_if(f'{n:,} characters' not in doc,errors,f'docs/TOKEN_BUDGETS.md missing/stale {n:,}-char budget figure')

def verify_release_version_refs(root,errors):
    vfile=root/'VERSION'
    if not vfile.is_file(): return
    version=vfile.read_text(encoding='utf-8').strip()
    pat=re.compile(r'Progressive-Context-Project-Runtime-v(\d+\.\d+\.\d+)')
    for rel in RELEASE_VERSION_DOCS:
        for found in set(pat.findall(read(root/rel))):
            fail_if(found!=version,errors,f'{rel} references stale runtime v{found} (VERSION is {version})')

def verify_context_manifest(root,errors):
    try:
        data=json.loads(read(root/'docs/project/CONTEXT_MANIFEST.json'))
        if data.get('schema')!=1 or not isinstance(data.get('phases'),dict): errors.append('invalid CONTEXT_MANIFEST schema')
    except Exception as exc: errors.append('invalid CONTEXT_MANIFEST.json: '+str(exc))

def verify_project_state(root,errors,warns):
    road=read(root/'docs/project/ROADMAP.md'); markers=re.findall(r'^- \[([ >x])\].*?`(docs/phases/[^`]+\.md)`',road,re.M)
    if markers:
        active=[p for marker,p in markers if marker=='>']
        if len(active)>1: errors.append('Roadmap has more than one active phase')
        if not active and not all(marker=='x' for marker,_ in markers): errors.append('Initialized Roadmap must have exactly one active phase unless all phases are complete')
        for marker,rel in markers:
            p=root/rel
            # Completed and active phases must have detailed phase files. Planned future
            # phases may remain Roadmap-only until they become active.
            if marker in {'x','>'} and not p.is_file():
                errors.append('Roadmap phase file missing: '+rel)
                continue
            if marker=='x' and p.is_file() and not completion_record(p):
                warns.append('completed phase lacks durable Completion Record (legacy/migration gap): '+rel)
    phase=current_phase(root) or root/'templates/PHASE.template.md'
    project_chars=sum(chars(root/rel) for rel in ['docs/project/PROJECT_BRIEF.md','docs/project/ARCHITECTURE.md','docs/project/ROADMAP.md'])+chars(phase)
    if current_phase(root):
        _,record=completion_bridge(root,current_phase(root)); project_chars+=len(record)
    if project_chars>22000: warns.append(f'project default context exceeds 22000-char soft budget: {project_chars}')

def verify_adoption_state(root,errors,ignore_pending):
    p=root/'.progressive-context-spec-kit/ADOPTION_STATE'
    if p.is_file() and p.read_text(encoding='utf-8').strip()=='pending' and not ignore_pending: errors.append('existing-project adoption is pending; reconcile conflicts and run --finalize-adoption')

def verify_metadata(root,errors):
    marker=root/'.progressive-context-spec-kit'
    if marker.is_dir():
        fail_if(not (marker/'VERSION').is_file(),errors,'starter/project marker missing VERSION')
        fail_if(not (marker/'AGENT_TARGET').is_file(),errors,'starter/project marker missing AGENT_TARGET')
        if (marker/'AGENT_TARGET').is_file(): fail_if((marker/'AGENT_TARGET').read_text(encoding='utf-8').strip() not in {'codex','claude','both'},errors,'invalid AGENT_TARGET marker')
    else:
        for rel in ['VERSION','LICENSE']: fail_if(not (root/rel).is_file(),errors,'source framework metadata missing: '+rel)

def finish(errors,warns):
    for x in errors: print('ERROR:',x)
    for x in warns: print('WARN:',x)
    if errors: print(f'AUDIT: FAIL ({len(errors)} errors, {len(warns)} warnings)'); raise SystemExit(1)
    print(f'AUDIT: PASS (0 errors, {len(warns)} warnings)')

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--root',default='.'); ap.add_argument('--ignore-adoption-pending',action='store_true'); a=ap.parse_args(); root=Path(a.root).resolve(); errors=[]; warns=[]
    for rel in REQUIRED:
        if not (root/rel).is_file(): errors.append('missing '+rel)
    if errors: finish(errors,warns)
    verify_metadata(root,errors); verify_adoption_state(root,errors,a.ignore_adoption_pending); verify_archive_hash(root,errors); verify_profiles(root,errors); verify_migration_coverage(root,errors,warns)
    e,w=validate_behavior_contract(root); errors+=e; warns+=w
    e,w=validate_framework_contract(root); errors+=e; warns+=w
    errors+=validate_duplication(root)
    verify_skills(root,errors); verify_tooling(root,errors); verify_context_manifest(root,errors); verify_project_state(root,errors,warns)
    verify_token_budgets_doc(root,errors); verify_release_version_refs(root,errors); finish(errors,warns)
if __name__=='__main__': main()
