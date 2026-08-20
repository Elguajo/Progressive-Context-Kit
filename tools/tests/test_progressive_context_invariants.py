import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
INIT = ROOT / 'tools/init_project.py'


class ProgressiveContextInvariantTests(unittest.TestCase):
    def run_init(self, target, *args):
        return subprocess.run(
            [sys.executable, str(INIT), str(target), *args],
            capture_output=True,
            text=True,
        )

    def test_completion_report_stays_cold_while_compact_bridge_is_compiled(self):
        with tempfile.TemporaryDirectory() as d:
            target = Path(d) / 'project'
            result = self.run_init(target, '--profile', 'standalone')
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

            phase0 = target / '.progressive/phases/00-complete.md'
            phase0.write_text(
                '# Phase 00 — Complete\n\n'
                '## Completion Record\n'
                'Status: COMPLETE\n'
                'Final report: ../completions/00-complete.md\n'
                'Outcome: BRIDGE_SENTINEL\n',
                encoding='utf-8',
            )
            phase1 = target / '.progressive/phases/01-active.md'
            phase1.write_text(
                '# Phase 01 — Active\n\n## Goal\nContinue safely.\n',
                encoding='utf-8',
            )
            report = target / '.progressive/completions/00-complete.md'
            report.write_text(
                '# Phase 00 Completion\n\nCOLD_REPORT_SENTINEL\n',
                encoding='utf-8',
            )
            roadmap = target / '.progressive/project/ROADMAP.md'
            roadmap.write_text(
                '# Roadmap\n\n'
                '- [x] Phase 00 — `.progressive/phases/00-complete.md`\n'
                '- [>] Phase 01 — `.progressive/phases/01-active.md`\n',
                encoding='utf-8',
            )

            compile_result = subprocess.run(
                [
                    sys.executable,
                    str(target / '.progressive/tools/context_compile.py'),
                    '--root',
                    str(target),
                ],
                capture_output=True,
                text=True,
            )
            self.assertEqual(compile_result.returncode, 0, compile_result.stdout + compile_result.stderr)
            self.assertIn('BRIDGE_SENTINEL', compile_result.stdout)
            self.assertNotIn('COLD_REPORT_SENTINEL', compile_result.stdout)

    def test_completion_layer_has_one_phase_report_template_and_no_task_report_template(self):
        self.assertTrue((ROOT / 'templates/PHASE_COMPLETION.template.md').is_file())
        self.assertFalse((ROOT / 'templates/TASK_COMPLETION.template.md').exists())
        handoff = (ROOT / 'docs/system/HANDOFF_PROTOCOL.md').read_text(encoding='utf-8')
        self.assertIn('docs/completions/<phase-name>.md', handoff)
        self.assertIn('Do not create one completion file per routine task', handoff)

    def test_phase_completion_record_remains_compact_bridge(self):
        phase_template = (ROOT / 'templates/PHASE.template.md').read_text(encoding='utf-8')
        record = phase_template.split('## Completion Record', 1)[1]
        self.assertIn('Keep this bridge compact', record)
        self.assertIn('Detailed durable phase history belongs in the phase completion report', record)

    def test_layer_ownership_keeps_current_truth_separate_from_history(self):
        ownership = (ROOT / 'docs/system/LAYER_OWNERSHIP.md').read_text(encoding='utf-8')
        self.assertIn('Brief → product outcome/users/scope/constraints/success.', ownership)
        self.assertIn('Architecture → current stack/system shape/trust boundaries/operational assumptions.', ownership)
        self.assertIn('ADR → one consequential decision rationale.', ownership)
        self.assertIn('read on demand, not normal warm-up', ownership)

    def test_next_session_remains_volatile_hot_navigation(self):
        template = (ROOT / 'templates/NEXT_SESSION.template.md').read_text(encoding='utf-8')
        self.assertIn('Volatile hot context. Overwrite this file on each meaningful handoff', template)
        self.assertIn('do not accumulate prior-session history', template)
        self.assertIn('completion reports, or chat history unless evidence requires it', template)

    def test_next_session_prompt_is_single_focus_until_current_gate_closes(self):
        template = (ROOT / 'templates/NEXT_SESSION.template.md').read_text(encoding='utf-8')
        handoff = (ROOT / 'docs/system/HANDOFF_PROTOCOL.md').read_text(encoding='utf-8')
        agent_skill = (ROOT / '.agents/skills/session-handoff/SKILL.md').read_text(encoding='utf-8')
        claude_skill = (ROOT / '.claude/skills/session-handoff/SKILL.md').read_text(encoding='utf-8')

        self.assertIn('<one unresolved execution target only>', template)
        self.assertIn('Do not name or describe later queued work here.', template)
        self.assertIn('do not bundle a second queued', template)
        self.assertIn('One handoff prompt = one unresolved execution target.', handoff)
        self.assertIn('finish current task → start next task', handoff)
        self.assertIn('must focus only on closing it', handoff)
        self.assertIn('Single-Focus Continuation', agent_skill)
        self.assertIn('Do not name or preload the next queued task/phase', agent_skill)
        self.assertEqual(agent_skill, claude_skill)

    def test_always_loaded_hard_budgets_remain_pinned_to_v25_values(self):
        # Raised from the v1.7.2 baseline (5000/8500/8600/9000) per the documented
        # Progressive-aware v2.5 migration (docs/migration/CODEX_CUSTOM_INSTRUCTIONS_V2_5.md),
        # which commits to a 5,500-char global adapter ceiling.
        audit = (ROOT / 'tools/audit.py').read_text(encoding='utf-8')
        expected = [
            "chars(g)>5500",
            "chars(gc)>5500",
            "chars(p)>3600",
            "chars(g)+chars(p)>9100",
            "chars(gc)+chars(p)>9100",
            "chars(s)>9300",
        ]
        for anchor in expected:
            self.assertIn(anchor, audit, anchor)

    def test_human_visual_explanations_remain_source_only(self):
        guide = (ROOT / 'docs/human/VISUAL_EXPLANATIONS.md').read_text(encoding='utf-8')
        self.assertIn(
            'Human explanatory assets are source-only documentation and must never be required for Runtime operation or packaged into Project Runtime.',
            guide,
        )
        human_guides = [
            'GLOSSARY.md',
            'GLOSSARY.ru.md',
            'HOW_PROGRESSIVE_CONTEXT_WORKS.md',
            'HOW_PROGRESSIVE_CONTEXT_WORKS.ru.md',
            'PROJECT_MEMORY_MODEL.md',
            'PROJECT_MEMORY_MODEL.ru.md',
            'UPDATING_RUNTIME.md',
            'UPDATING_RUNTIME.ru.md',
        ]
        for name in human_guides:
            self.assertTrue((ROOT / 'docs/human' / name).is_file(), name)
        visual_guides = [
            'progressive-context-overview.md',
            'session-context-flow.md',
            'project-memory-model.md',
            'user-onboarding.md',
            'phase-completion-lifecycle.md',
            'tool-routing.md',
            'source-runtime-release.md',
            'framework-update-safety.md',
        ]
        for name in visual_guides:
            self.assertTrue((ROOT / 'docs/visuals' / name).is_file(), name)
        layout = (ROOT / 'tools/runtime_layout.py').read_text(encoding='utf-8')
        self.assertNotIn("'docs/visuals/'", layout)
        for name in ['VISUAL_EXPLANATIONS.md', *human_guides]:
            self.assertNotIn(name, layout)

    def test_glossary_explains_framework_language_and_is_easy_to_find(self):
        glossary = (ROOT / 'docs/human/GLOSSARY.md').read_text(encoding='utf-8')
        glossary_ru = (ROOT / 'docs/human/GLOSSARY.ru.md').read_text(encoding='utf-8')
        readme = (ROOT / 'README.md').read_text(encoding='utf-8')
        readme_ru = (ROOT / 'README_RU.md').read_text(encoding='utf-8')
        getting_started = (ROOT / 'docs/human/GETTING_STARTED.md').read_text(encoding='utf-8')
        getting_started_ru = (ROOT / 'docs/human/GETTING_STARTED.ru.md').read_text(encoding='utf-8')
        visuals = (ROOT / 'docs/visuals/README.md').read_text(encoding='utf-8')

        for anchor in [
            '**PC**',
            '**FW**',
            '**DRS**',
            '**ADR**',
            'Default Read Set',
            'Phase Completion Report',
            'Single-Focus Continuation',
        ]:
            self.assertIn(anchor, glossary)
        self.assertIn('Глоссарий', glossary_ru)
        self.assertIn('GLOSSARY.md', readme)
        self.assertIn('GLOSSARY.ru.md', readme_ru)
        self.assertIn('GLOSSARY.md', getting_started)
        self.assertIn('GLOSSARY.ru.md', getting_started_ru)
        self.assertIn('../human/GLOSSARY.md', visuals)


if __name__ == '__main__':
    unittest.main()