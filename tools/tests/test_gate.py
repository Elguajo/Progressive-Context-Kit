import io
import subprocess
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

import gate
from runtime_layout import runtime_entries


class ProgressiveGateTests(unittest.TestCase):
    def test_default_gate_has_one_canonical_ordered_check_set(self):
        checks = gate.source_checks()
        self.assertEqual(
            [check.id for check in checks],
            [
                "profile-mirrors",
                "skill-mirrors",
                "behavior-contract",
                "framework-contract",
                "tool-adapter-protocol",
                "routing-integrity",
                "autoresearch-records",
                "duplication-audit",
                "source-audit",
                "context-report",
                "unit-tests",
            ],
        )
        self.assertEqual(checks[-1].args, ("-m", "unittest", "discover", "-s", "tools/tests", "-v"))

    def test_skip_unit_tests_removes_only_unit_test_check(self):
        full = gate.source_checks(True)
        reduced = gate.source_checks(False)
        self.assertEqual(len(full), len(reduced) + 1)
        self.assertEqual([check.id for check in reduced], [check.id for check in full[:-1]])

    def test_gate_is_fail_fast_and_names_failed_check(self):
        checks = (
            gate.Check("first", "First", ("tools/audit.py",)),
            gate.Check("second", "Second", ("tools/framework_contract.py",)),
            gate.Check("third", "Third", ("tools/routing_integrity.py",)),
        )
        results = [
            subprocess.CompletedProcess([], 0),
            subprocess.CompletedProcess([], 7),
        ]
        with (
            patch.object(gate, "source_checks", return_value=checks),
            patch.object(gate.subprocess, "run", side_effect=results) as runner,
            patch("sys.stdout", new_callable=io.StringIO) as output,
        ):
            code = gate.run_gate(ROOT)
        self.assertEqual(code, 7)
        self.assertEqual(runner.call_count, 2)
        self.assertIn("PROGRESSIVE GATE: FAIL (1/3 checks passed; failed: second)", output.getvalue())

    def test_ci_release_and_workflow_audit_delegate_to_gate(self):
        ci = (ROOT / ".github/workflows/audit.yml").read_text(encoding="utf-8")
        release = (ROOT / "tools/build_release.py").read_text(encoding="utf-8")
        skill = (ROOT / ".agents/skills/workflow-audit/SKILL.md").read_text(encoding="utf-8")
        self.assertIn("python3 tools/gate.py", ci)
        self.assertNotIn("python3 tools/behavior_contract.py", ci)
        self.assertIn('"tools/gate.py"', release)
        self.assertIn("python3 tools/gate.py", skill)

    def test_gate_infrastructure_stays_out_of_project_runtime(self):
        runtime_sources = {src.resolve() for src, _, _ in runtime_entries(ROOT, "standalone")}
        self.assertNotIn((ROOT / "tools/gate.py").resolve(), runtime_sources)
        self.assertNotIn((ROOT / "docs/contracts/PROGRESSIVE_GATE.md").resolve(), runtime_sources)


if __name__ == "__main__":
    unittest.main()
