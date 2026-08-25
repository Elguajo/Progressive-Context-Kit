import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

import tool_adapter_protocol
from runtime_layout import write_runtime


class ToolAdapterProtocolTests(unittest.TestCase):
    def test_source_registry_conforms(self):
        errors, warns = tool_adapter_protocol.validate(ROOT)
        self.assertEqual(errors, [])
        self.assertEqual(warns, [])

    def test_each_adapter_declares_route_boundaries_and_fallback(self):
        data = json.loads((ROOT / "integrations/TOOL_REGISTRY.json").read_text(encoding="utf-8"))
        self.assertEqual(data["schema"], 2)
        self.assertEqual(data["adapter_contract_version"], 1)
        for key, adapter in data["tools"].items():
            self.assertTrue(adapter["capability"], key)
            self.assertTrue(adapter["preferred_for"], key)
            self.assertTrue(adapter["avoid_when"], key)
            self.assertTrue(adapter["fallback"], key)
            self.assertIn("extra_approval_required_for", adapter)

    def test_missing_route_boundary_fails(self):
        data = json.loads((ROOT / "integrations/TOOL_REGISTRY.json").read_text(encoding="utf-8"))
        broken = copy.deepcopy(data)
        broken["tools"]["semble"].pop("avoid_when")
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            integrations = root / "integrations"
            integrations.mkdir(parents=True)
            (integrations / "TOOL_REGISTRY.json").write_text(json.dumps(broken), encoding="utf-8")
            (integrations / "TOOL_ADAPTER_PROTOCOL.md").write_text("protocol\n", encoding="utf-8")
            errors, _ = tool_adapter_protocol.validate(root)
        self.assertTrue(any("tools.semble missing fields: avoid_when" in error for error in errors))

    def test_invalid_profile_fails(self):
        data = json.loads((ROOT / "integrations/TOOL_REGISTRY.json").read_text(encoding="utf-8"))
        broken = copy.deepcopy(data)
        broken["tools"]["serena"]["profiles"] = ["always_on"]
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            integrations = root / "integrations"
            integrations.mkdir(parents=True)
            (integrations / "TOOL_REGISTRY.json").write_text(json.dumps(broken), encoding="utf-8")
            (integrations / "TOOL_ADAPTER_PROTOCOL.md").write_text("protocol\n", encoding="utf-8")
            errors, _ = tool_adapter_protocol.validate(root)
        self.assertTrue(any("tools.serena.profiles contains unknown profile" in error for error in errors))

    def test_generated_runtime_carries_and_validates_adapter_contract(self):
        with tempfile.TemporaryDirectory() as d:
            runtime = Path(d) / "runtime"
            write_runtime(ROOT, runtime)
            self.assertTrue((runtime / ".progressive/integrations/TOOL_ADAPTER_PROTOCOL.md").is_file())
            self.assertTrue((runtime / ".progressive/tools/tool_adapter_protocol.py").is_file())
            project_integrations = runtime / "integrations"
            project_integrations.mkdir()
            (project_integrations / "app-provider.txt").write_text("project-owned\n", encoding="utf-8")
            errors, warns = tool_adapter_protocol.validate(runtime)
            self.assertEqual(errors, [])
            self.assertEqual(warns, [])

    def test_runtime_registry_corruption_is_detected(self):
        with tempfile.TemporaryDirectory() as d:
            runtime = Path(d) / "runtime"
            write_runtime(ROOT, runtime)
            registry = runtime / ".progressive/integrations/TOOL_REGISTRY.json"
            data = json.loads(registry.read_text(encoding="utf-8"))
            data["tools"]["rtk"]["fallback"] = ""
            registry.write_text(json.dumps(data), encoding="utf-8")
            errors, _ = tool_adapter_protocol.validate(runtime)
            self.assertTrue(any("tools.rtk.fallback must be a non-empty string" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
