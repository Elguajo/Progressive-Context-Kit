"""Resolve phase-owned task prompts without loading historical prompt bodies."""
import re

from common import current_phase, project_file, read, safe_join

OPEN_STATUSES = {'READY', 'IN PROGRESS', 'BLOCKED'}
FRESHNESS = {'UNCHECKED', 'CURRENT', 'STALE'}


def structural_text(text):
    """Mask fenced content while preserving offsets for Markdown heading parsing."""
    lines = []
    fence = None
    for line in text.splitlines(keepends=True):
        match = re.match(r'^ {0,3}(`{3,}|~{3,})(.*)$', line.rstrip('\r\n'))
        if fence:
            if match and match[1][0] == fence[0] and len(match[1]) >= len(fence) and not match[2].strip():
                fence = None
            lines.append(''.join('\n' if c == '\n' else ' ' for c in line))
        elif match:
            fence = match[1]
            lines.append(''.join('\n' if c == '\n' else ' ' for c in line))
        else:
            lines.append(line)
    return ''.join(lines)


def section(text, title):
    masked = structural_text(text)
    headings = list(re.finditer(r'^## ([^\n]+)\n?', masked, re.M))
    matches = [(i, h) for i, h in enumerate(headings) if h[1].strip() == title]
    if len(matches) != 1:
        return None
    i, heading = matches[0]
    end = headings[i + 1].start() if i + 1 < len(headings) else len(text)
    return heading.start(), heading.end(), end


def phase_context(text):
    """Keep the current plan; prompt history is read only through an explicit pointer."""
    masked = structural_text(text)
    headings = list(re.finditer(r'^## ([^\n]+)\n?', masked, re.M))
    for i in range(len(headings) - 1, -1, -1):
        h = headings[i]
        if h[1].strip() == 'Task prompts':
            end = headings[i + 1].start() if i + 1 < len(headings) else len(text)
            text = text[:h.start()] + text[end:]
    return text


def prompt_records(text):
    span = section(text, 'Task prompts')
    if not span:
        return []
    body = text[span[1]:span[2]]
    headings = list(re.finditer(r'^### ([a-z0-9][a-z0-9-]*)\n', structural_text(body), re.M))
    records = []
    for i, heading in enumerate(headings):
        end = headings[i + 1].start() if i + 1 < len(headings) else len(body)
        record = body[heading.start():end].strip()
        # Metadata cannot be supplied by request/prompt/evidence text.
        subheading = re.search(r'^#### ', structural_text(record), re.M)
        metadata = record[:subheading.start()] if subheading else record
        fields = {}
        for name in ('Task', 'Status', 'Freshness'):
            values = re.findall(rf'^{name}: ([^\n]+)$', metadata, re.M)
            fields[name] = values[0].strip() if len(values) == 1 else ''
        records.append((heading[1], record, fields))
    return records


def prompt_source(phase):
    """One adjacent archive per phase; old inline records remain readable."""
    text = read(phase)
    archive = phase.with_name(phase.stem + '.prompts.md')
    if archive.is_file():
        if prompt_records(text):
            return archive, '', 'task prompts exist both inline and in the phase archive'
        if archive.resolve().parent != phase.resolve().parent:
            return archive, '', 'task prompt archive escapes owning phase directory'
        archive_text = read(archive)
        if not section(archive_text, 'Task prompts'):
            return archive, '', 'phase archive requires exactly one Task prompts section'
        return archive, archive_text, ''
    return phase, text, ''


def hot_prompt(record, checkpoint_limit=1200):
    """Render execution context without original request or accumulated evidence."""
    masked = structural_text(record)
    headings = list(re.finditer(r'^#### ([^\n]+)\n?', masked, re.M))
    metadata = record[:headings[0].start()] if headings else record
    parts = [line for line in metadata.splitlines()
             if line.startswith(('### ', 'Task: ', 'Status: ', 'Freshness: ', 'Supersedes: '))]
    for i, heading in enumerate(headings):
        name = heading[1].strip()
        if name not in {'Prompt', 'Freshness check', 'Current checkpoint'}:
            continue
        end = headings[i + 1].start() if i + 1 < len(headings) else len(record)
        body = record[heading.end():end].strip()
        if name != 'Prompt' and len(body) > checkpoint_limit:
            body = 'POINTER ONLY — read this section in the saved record before dependent execution; exceeds checkpoint limit.'
        parts.append(f'#### {name}\n{body}')
    return '\n\n'.join(parts)


def active_prompt(root):
    """Return (reference, record, error); absence is valid for legacy projects."""
    root = root.resolve()
    phase = current_phase(root)
    source, phase_text, source_error = prompt_source(phase) if phase else (None, '', '')
    if source_error:
        return '', '', source_error
    handoff = read(project_file(root, 'NEXT_SESSION.md'))
    span = section(handoff, 'Active task prompt')
    if not span:
        if re.search(r'^## Active task prompt\s*$', structural_text(handoff), re.M):
            return '', '', 'duplicate Active task prompt sections'
        if phase and prompt_records(phase_text):
            return '', '', 'phase has task prompts but NEXT_SESSION has no Active task prompt'
        return '', '', ''
    if section(handoff, 'NEXT SESSION PROMPT'):
        return '', '', 'NEXT_SESSION contains both an Active task prompt pointer and a legacy executable prompt'
    lines = handoff[span[1]:span[2]].strip().splitlines()
    ref = lines[0].strip().strip('`') if lines else ''
    if ref.startswith('<'):
        if phase and prompt_records(phase_text):
            return ref, '', 'Active task prompt is still a placeholder'
        return '', '', ''
    if ref == 'NONE':
        if phase and any(fields['Status'] in OPEN_STATUSES for _, _, fields in prompt_records(phase_text)):
            return ref, '', 'Active task prompt is NONE while an open task prompt exists'
        return ref, '', ''
    if not re.fullmatch(r'(?:docs|\.progressive)/phases/[^#\n]+\.md#[a-z0-9][a-z0-9-]*', ref):
        return ref, '', 'invalid Active task prompt reference (expected root-relative phase.md#id)'
    rel, identifier = ref.rsplit('#', 1)
    try:
        target = safe_join(root, rel)
    except ValueError as exc:
        return ref, '', str(exc)
    if not phase or target != source.resolve():
        return ref, '', 'Active task prompt does not belong to the Roadmap current phase'
    records = prompt_records(phase_text)
    ids = [identifier for identifier, _, _ in records]
    if len(ids) != len(set(ids)):
        return ref, '', 'duplicate task prompt IDs in current phase'
    matches = [(record, fields) for rid, record, fields in records if rid == identifier]
    if len(matches) != 1:
        return ref, '', 'Active task prompt ID not found in current phase'
    record, fields = matches[0]
    if not fields['Task'] or fields['Task'].startswith('<'):
        return ref, '', 'Active task prompt requires a concrete Task'
    if fields['Status'] not in OPEN_STATUSES:
        return ref, '', 'Active task prompt status is terminal or invalid: ' + fields['Status']
    if fields['Freshness'] not in FRESHNESS or fields['Freshness'] == 'STALE':
        return ref, '', 'Active task prompt freshness is stale or invalid: ' + fields['Freshness']
    masked = structural_text(record)
    prompt_headings = list(re.finditer(r'^#### Prompt\n', masked, re.M))
    if len(prompt_headings) != 1:
        return ref, '', 'Active task prompt requires exactly one Prompt body'
    prompt_heading = prompt_headings[0]
    rest = record[prompt_heading.end():]
    next_heading = re.search(r'^#### ', structural_text(rest), re.M)
    body = rest[:next_heading.start()] if next_heading else rest
    content = body.strip()
    fenced = re.fullmatch(r'(`{3,}|~{3,})[^\n]*\n(.*?)\n?\1\s*', content, re.S)
    if fenced:
        content = fenced[2].strip()
    if not content:
        return ref, '', 'Active task prompt has an empty Prompt body'
    if content.strip().startswith('<'):
        return ref, '', 'Active task prompt body is still a placeholder'
    return ref, record, ''
