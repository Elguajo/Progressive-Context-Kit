import json
import os
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from prepare_agent_benchmark import (
    BENCHMARK_ROOT,
    OPTIONAL_FRAMEWORK_TOOLS,
    fixture_digest,
    initialize_benchmark_project,
    load_experiment,
    materialize_fixture,
    prepare_pack,
    sha256_file,
)
from runtime_layout import runtime_entries


class AgentBenchmarkPackTests(unittest.TestCase):
    def test_default_fixture_hashes_match_preserved_historical_pilot(self):
        recorded = json.loads((ROOT/'docs/evals/agent/token-efficiency-2026-10-03/RUN_PLAN.json').read_text())
        hashes = {pair['task_id']: pair['fixture_snapshot'] for pair in recorded['pairs']}
        tasks = json.loads((BENCHMARK_ROOT/'TASKS.json').read_text())['tasks']
        for task in tasks:
            with self.subTest(task=task['id']), tempfile.TemporaryDirectory() as d:
                repo = Path(d)/'repo'
                materialize_fixture(task['fixture'], repo)
                self.assertEqual(fixture_digest(repo), hashes[task['id']])

    def test_controlled_fixtures_discover_real_tests_without_changing_legacy(self):
        tasks = json.loads((BENCHMARK_ROOT / 'TASKS.json').read_text())['tasks']
        for task in tasks:
            with self.subTest(task=task['id']), tempfile.TemporaryDirectory() as d:
                legacy, controlled = Path(d)/'legacy', Path(d)/'controlled'
                materialize_fixture(task['fixture'], legacy)
                materialize_fixture(task['fixture'], controlled, discoverable_tests=True)
                # The controlled patch changes only the discovery marker, not the task/code/tests.
                for path in legacy.rglob('*'):
                    if path.is_file():
                        self.assertEqual(path.read_bytes(), (controlled/path.relative_to(legacy)).read_bytes())
                if (controlled/'tests').is_dir():
                    self.assertTrue((controlled/'tests/__init__.py').is_file())
                    probe = subprocess.run(
                        [sys.executable, '-B', '-c',
                         "import unittest; print(unittest.TestLoader().discover('.').countTestCases())"],
                        cwd=controlled, capture_output=True, text=True,
                        env=dict(os.environ, PYTHONDONTWRITEBYTECODE='1'),
                    )
                    self.assertEqual(probe.returncode, 0, probe.stderr)
                    self.assertGreater(int(probe.stdout.strip()), 0)
                else:
                    self.assertFalse((controlled/'tests').exists())
                if task['id'] in ('recon-batch','keyhole-read','environment-probe','failure-pivot'):
                    self.assertFalse((legacy/'tests/__init__.py').exists())

    def test_controlled_pack_separates_neutral_workspaces_from_control_metadata(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            config = load_experiment(BENCHMARK_ROOT/'EXPERIMENT.json')
            config.update(experiment_id='controlled-test', harness_profile='controlled-v2')
            path = root/'config.json'; path.write_text(json.dumps(config))
            def runtime(repo, ref, agent, destination):
                (destination/'AGENTS.md').write_text('Local instructions\n')
                project = destination/'.progressive/project'; project.mkdir(parents=True)
                (project/'TOOLING_STATUS.json').write_text('{}\n')
                (project/'TOOLING_STATUS.md').write_text('Status: UNINITIALIZED\n')
            with patch('prepare_agent_benchmark.build_runtime_from_ref', side_effect=runtime):
                plan = prepare_pack(root/'control-pack', 1, {'environment-probe'},
                                    experiment_path=path, workspace_root=root/'local-tasks')
            self.assertEqual(plan['harness_profile'], 'controlled-v2')
            self.assertEqual(plan['workspace_root'], str((root/'local-tasks').resolve()))
            pair = plan['pairs'][0]
            self.assertTrue((root/'control-pack'/pair['prompt']).is_file())
            state = []
            for arm in ('baseline','candidate'):
                repo = (root/'control-pack'/pair['arms'][arm]['repo']).resolve()
                self.assertNotIn(root/'control-pack', repo.parents)
                self.assertNotRegex(str(repo), r'baseline|candidate|benchmark|experiment')
                self.assertFalse((repo/'RUN_PLAN.json').exists())
                self.assertTrue((repo/'tests/__init__.py').is_file())
                phase = repo/'.progressive/phases/00-current-task.md'
                self.assertTrue(phase.is_file())
                texts = '\n'.join(p.read_text() for p in (repo/'.progressive/project').glob('*')) + phase.read_text()
                self.assertNotRegex(texts.lower(), r'baseline|candidate|benchmark|experiment|environment-probe')
                history = subprocess.run(['git','log','-1','--format=%an %ae %s'], cwd=repo,
                                         capture_output=True, text=True, check=True).stdout
                self.assertNotRegex(history.lower(), r'baseline|candidate|benchmark|experiment')
                self.assertEqual(subprocess.run(['git','status','--porcelain'], cwd=repo,
                                               capture_output=True,text=True,check=True).stdout, '')
                state.append(texts)
            self.assertEqual(state[0], state[1])

    def test_invalid_workspace_does_not_replace_existing_control_pack(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d); output=root/'control-pack'; output.mkdir()
            sentinel=output/'keep'; sentinel.write_text('existing evidence')
            config=load_experiment(BENCHMARK_ROOT/'EXPERIMENT.json')
            config['harness_profile']='controlled-v2'
            path=root/'config.json'; path.write_text(json.dumps(config))
            existing=root/'existing';existing.mkdir()
            for workspace in (existing, output/'inside', ROOT/'dist/local-tasks', root/'baseline-jobs'):
                with self.subTest(workspace=workspace), self.assertRaises(ValueError):
                    prepare_pack(output,1,{'recon-batch'},experiment_path=path,workspace_root=workspace)
                self.assertEqual(sentinel.read_text(),'existing evidence')
            config['harness_profile']='historical'; path.write_text(json.dumps(config))
            with self.assertRaises(ValueError):
                prepare_pack(output,1,experiment_path=path,workspace_root=root/'local-tasks')
            self.assertEqual(sentinel.read_text(),'existing evidence')

    def test_unsafe_default_temporary_parent_preserves_existing_output(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d); output=root/'pack';output.mkdir()
            sentinel=output/'keep';sentinel.write_text('existing evidence')
            config=load_experiment(BENCHMARK_ROOT/'EXPERIMENT.json')
            config['harness_profile']='controlled-v2'
            path=root/'config.json';path.write_text(json.dumps(config))
            with patch('prepare_agent_benchmark.tempfile.gettempdir',return_value=str(ROOT/'dist')):
                with self.assertRaises(ValueError):
                    prepare_pack(output,1,experiment_path=path)
            self.assertEqual(sentinel.read_text(),'existing evidence')

    def test_custom_experiment_controls_refs_identity_and_provenance(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            config = json.loads((BENCHMARK_ROOT / 'EXPERIMENT.json').read_text())
            config.update(experiment_id='custom-efficiency', baseline_workflow_ref='a'*40,
                          candidate_workflow_ref='b'*40, agent_target='codex')
            path = root / 'experiment.json'
            path.write_text(json.dumps(config), encoding='utf-8')
            def runtime(repo, ref, agent, destination):
                (destination / 'AGENTS.md').write_text('Local fixture instructions\n')
            with patch('prepare_agent_benchmark.build_runtime_from_ref', side_effect=runtime) as builder, \
                 patch('prepare_agent_benchmark.init_clean_git_repo', return_value='c'*40):
                plan = prepare_pack(root / 'pack', 1, {'recon-batch'}, experiment_path=path)
            self.assertEqual(plan['experiment_id'],config['experiment_id'])
            self.assertEqual(plan['experiment_config'],config)
            self.assertEqual(plan['experiment_config_sha256'],sha256_file(path))
            self.assertEqual([call.args[1:3] for call in builder.call_args_list],
                             [('a'*40,'codex'),('b'*40,'codex')])
            pair=plan['pairs'][0]
            self.assertEqual(pair['arms']['candidate']['workflow_ref'],'b'*40)
            self.assertEqual(pair['task_sha256'],sha256_file(root/'pack'/pair['prompt']))
            self.assertEqual(pair['acceptance_sha256'],sha256_file(root/'pack'/pair['acceptance']))
            self.assertEqual(json.loads((root/'pack/RUN_PLAN.json').read_text()),plan)

    def test_default_experiment_still_selects_historical_refs(self):
        with tempfile.TemporaryDirectory() as d, \
             patch('prepare_agent_benchmark.build_runtime_from_ref') as builder, \
             patch('prepare_agent_benchmark.init_clean_git_repo',return_value='c'*40):
            plan=prepare_pack(Path(d)/'pack',1,{'recon-batch'})
        expected=load_experiment(BENCHMARK_ROOT/'EXPERIMENT.json')
        self.assertEqual(plan['experiment_id'],'execution-efficiency-v1')
        self.assertEqual([call.args[1] for call in builder.call_args_list],
                         [expected['baseline_workflow_ref'],expected['candidate_workflow_ref']])

    def test_invalid_experiment_preserves_existing_output(self):
        valid=load_experiment(BENCHMARK_ROOT/'EXPERIMENT.json')
        invalid=[None, {'schema':2}, dict(valid,baseline_workflow_ref='main'),
                 dict(valid,candidate_workflow_ref=valid['baseline_workflow_ref']),
                 dict(valid,experiment_id='../escape'),dict(valid,profile='personal'),
                 dict(valid,agent_target='other'),dict(valid,agent_target=[]),
                 dict(valid,default_repetitions=0),
                 dict(valid,default_repetitions=True),dict(valid,harness_profile='unknown')]
        for config in invalid:
            with self.subTest(config=config),tempfile.TemporaryDirectory() as d:
                root=Path(d); output=root/'pack'; output.mkdir()
                sentinel=output/'keep.txt'; sentinel.write_text('existing work')
                path=root/'experiment.json'; path.write_text(json.dumps(config))
                with self.assertRaises(ValueError):
                    prepare_pack(output,1,experiment_path=path)
                self.assertEqual(sentinel.read_text(),'existing work')

    def test_config_inside_disposable_output_retains_provenance(self):
        with tempfile.TemporaryDirectory() as d:
            output = Path(d) / 'pack'
            output.mkdir()
            path = output / 'experiment.json'
            config = load_experiment(BENCHMARK_ROOT / 'EXPERIMENT.json')
            path.write_text(json.dumps(config), encoding='utf-8')
            expected_hash = sha256_file(path)
            with patch('prepare_agent_benchmark.build_runtime_from_ref'), \
                 patch('prepare_agent_benchmark.init_clean_git_repo', return_value='c'*40):
                plan = prepare_pack(output, 1, {'recon-batch'}, experiment_path=path)
            self.assertEqual(plan['experiment_config'], config)
            self.assertEqual(plan['experiment_config_sha256'], expected_hash)

    def test_source_cannot_be_replaced_by_benchmark_output(self):
        for path in (ROOT,ROOT.parent):
            with self.subTest(path=path),self.assertRaises(ValueError):
                prepare_pack(path,1,{'recon-batch'})

    def test_experiment_pins_immutable_distinct_workflow_refs(self):
        experiment = json.loads((BENCHMARK_ROOT / "EXPERIMENT.json").read_text(encoding="utf-8"))
        baseline = experiment["baseline_workflow_ref"]
        candidate = experiment["candidate_workflow_ref"]
        self.assertRegex(baseline, r"^[0-9a-f]{40}$")
        self.assertRegex(candidate, r"^[0-9a-f]{40}$")
        self.assertNotEqual(baseline, candidate)
        self.assertEqual(experiment["profile"], "standalone")
        self.assertGreaterEqual(experiment["claim_repetitions_minimum"], 5)

    def test_task_set_covers_each_execution_efficiency_mechanism_once(self):
        data = json.loads((BENCHMARK_ROOT / "TASKS.json").read_text(encoding="utf-8"))
        tasks = data["tasks"]
        expected = {
            "batch-reconnaissance",
            "bounded-keyhole-reads",
            "single-pass-environment-probing",
            "convergent-validation",
            "repeated-failure-pivot",
            "bounded-polling",
        }
        self.assertEqual(len(tasks), 6)
        self.assertEqual({task["mechanism"] for task in tasks}, expected)
        self.assertEqual(len({task["id"] for task in tasks}), 6)
        for task in tasks:
            self.assertTrue(task["prompt"].strip())
            self.assertGreaterEqual(len(task["acceptance"]), 3)
            self.assertNotIn(task["mechanism"], task["prompt"])

    def test_all_raw_fixtures_materialize_deterministically_and_compile(self):
        tasks = json.loads((BENCHMARK_ROOT / "TASKS.json").read_text(encoding="utf-8"))["tasks"]
        for task in tasks:
            with self.subTest(task=task["id"]), tempfile.TemporaryDirectory() as a, tempfile.TemporaryDirectory() as b:
                first = Path(a) / "repo"
                second = Path(b) / "repo"
                materialize_fixture(task["fixture"], first)
                materialize_fixture(task["fixture"], second)
                self.assertEqual(fixture_digest(first), fixture_digest(second))
                self.assertFalse((first / "AGENTS.md").exists())
                self.assertFalse((first / "CLAUDE.md").exists())
                self.assertFalse((first / ".progressive").exists())
                for source in first.rglob("*.py"):
                    compile(source.read_text(encoding="utf-8"), str(source), "exec")

    def test_injected_runtime_seeds_are_replaced_with_active_identical_project_state(self):
        with tempfile.TemporaryDirectory() as d:
            repo = Path(d) / "repo"
            materialize_fixture("recon_batch", repo)
            project = repo / ".progressive/project"
            project.mkdir(parents=True)
            for name in ["PROJECT_BRIEF.md", "ARCHITECTURE.md", "ROADMAP.md", "NEXT_SESSION.md"]:
                (project / name).write_text("Status: UNINITIALIZED\n", encoding="utf-8")
            (project / "TOOLING_STATUS.json").write_text("{}\n", encoding="utf-8")
            (project / "TOOLING_STATUS.md").write_text("Status: UNINITIALIZED\n", encoding="utf-8")

            initialize_benchmark_project(repo, "recon-batch")

            for name in ["PROJECT_BRIEF.md", "ARCHITECTURE.md", "ROADMAP.md", "NEXT_SESSION.md"]:
                text = (project / name).read_text(encoding="utf-8")
                self.assertNotIn("UNINITIALIZED", text)
            self.assertIn("Status: ACTIVE", (project / "PROJECT_BRIEF.md").read_text(encoding="utf-8"))
            self.assertIn("[>] Phase 00", (project / "ROADMAP.md").read_text(encoding="utf-8"))
            self.assertTrue((repo / ".progressive/phases/00-benchmark-task.md").is_file())

            tooling = json.loads((project / "TOOLING_STATUS.json").read_text(encoding="utf-8"))
            self.assertEqual(tooling["profile"], "minimal")
            self.assertEqual(set(tooling["tools"]), set(OPTIONAL_FRAMEWORK_TOOLS))
            self.assertTrue(
                all(entry["status"] == "not_applicable" for entry in tooling["tools"].values())
            )
            tooling_md = (project / "TOOLING_STATUS.md").read_text(encoding="utf-8")
            self.assertIn("Profile: minimal", tooling_md)
            self.assertIn("repository-native tools only", tooling_md)

    def test_keyhole_fixture_is_materially_large_and_polling_fixture_is_long_running(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            keyhole = root / "keyhole"
            polling = root / "polling"
            materialize_fixture("keyhole_read", keyhole)
            materialize_fixture("polling_discipline", polling)
            lines = (keyhole / "src/catalog/data.py").read_text(encoding="utf-8").splitlines()
            self.assertGreater(len(lines), 1300)
            slow = (polling / "tools/slow_validation.py").read_text(encoding="utf-8")
            self.assertIn("time.sleep(35)", slow)

    def test_environment_fixture_exposes_groupable_prerequisites(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d) / "repo"
            materialize_fixture("environment_probe", root)
            text = (root / "ENVIRONMENT.md").read_text(encoding="utf-8")
            for anchor in ["python3 --version", "git --version", "schema_probe.py --version"]:
                self.assertIn(anchor, text)

    def test_benchmark_research_files_stay_out_of_project_runtime(self):
        runtime_sources = {src.resolve() for src, _, _ in runtime_entries(ROOT, "standalone")}
        benchmark_sources = {
            path.resolve()
            for path in (ROOT / "docs/evals/agent/benchmark").rglob("*")
            if path.is_file()
        }
        benchmark_sources.update(
            {
                (ROOT / "tools/prepare_agent_benchmark.py").resolve(),
                (ROOT / "tools/agent_benchmark_fixtures.py").resolve(),
            }
        )
        self.assertTrue(benchmark_sources.isdisjoint(runtime_sources))


if __name__ == "__main__":
    unittest.main()
