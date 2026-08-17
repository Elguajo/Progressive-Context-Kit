from pathlib import Path
import re

PHASE_RE = re.compile(r"^- \[(?P<marker>[ >x])\].*?`(?P<path>(?:docs|\.progressive)/phases/[^`]+\.md)`", re.M)

PREFIX_MAP = {
    'docs/project/': '.progressive/project/',
    'docs/phases/': '.progressive/phases/',
    'docs/decisions/': '.progressive/decisions/',
    'docs/system/': '.progressive/system/',
    'integrations/': '.progressive/integrations/',
    'templates/': '.progressive/templates/',
    'prompts/': '.progressive/prompts/',
    'tools/': '.progressive/tools/',
}

def read(p: Path):
    return p.read_text(encoding='utf-8') if p.is_file() else ''

def chars(p: Path):
    return len(read(p))

def is_runtime(root: Path) -> bool:
    return (root / '.progressive' / 'VERSION').is_file()

def resolve_path(root: Path, rel: str) -> Path:
    if is_runtime(root):
        for old, new in PREFIX_MAP.items():
            if rel.startswith(old):
                rel = new + rel[len(old):]
                break
    return root / rel

def project_file(root: Path, name: str) -> Path:
    return resolve_path(root, f'docs/project/{name}')

def template_file(root: Path, name: str) -> Path:
    return resolve_path(root, f'templates/{name}')

def integration_file(root: Path, name: str) -> Path:
    return resolve_path(root, f'integrations/{name}')

def current_phase(root: Path):
    road = read(project_file(root, 'ROADMAP.md'))
    for m in PHASE_RE.finditer(road):
        if m.group('marker') == '>':
            p = root / m.group('path')
            return p if p.is_file() else None
    return None
