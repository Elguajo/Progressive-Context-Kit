from __future__ import annotations

import hashlib
from pathlib import Path
import textwrap


def write_file(root: Path, rel: str, content: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(textwrap.dedent(content).lstrip("\n"), encoding="utf-8")


def test_prelude() -> str:
    return (
        "import sys\n"
        "from pathlib import Path\n"
        "sys.path.insert(0, str(Path(__file__).resolve().parents[1] / \"src\"))\n\n"
    )


def write_test(root: Path, rel: str, body: str) -> None:
    write_file(root, rel, test_prelude() + textwrap.dedent(body).lstrip("\n"))


def build_recon_batch(root: Path) -> None:
    write_file(root, "pyproject.toml", """
        [project]
        name = "harbor-service"
        version = "2.4.1"
        requires-python = ">=3.11"
    """)
    write_file(root, "README.md", """
        # Harbor Service

        Commands are registered in `harbor.dispatcher`. Keep command implementations small and
        follow existing command modules. Run `python3 -m unittest discover -v` for validation.
    """)
    write_file(root, "src/harbor/__init__.py", "")
    write_file(root, "src/harbor/config.py", 'MODE = "safe"\n')
    write_file(root, "src/harbor/meta.py", """
        from pathlib import Path
        import tomllib

        def project_metadata():
            root = Path(__file__).resolve().parents[2]
            return tomllib.loads((root / "pyproject.toml").read_text(encoding="utf-8"))["project"]
    """)
    write_file(root, "src/harbor/commands/__init__.py", "")
    write_file(root, "src/harbor/commands/ping.py", """
        def run():
            return {"ok": True}
    """)
    write_file(root, "src/harbor/commands/info.py", """
        from harbor.config import MODE
        from harbor.meta import project_metadata

        def run():
            meta = project_metadata()
            return {"service": meta["name"], "mode": MODE}
    """)
    write_file(root, "src/harbor/dispatcher.py", """
        from harbor.commands import info, ping

        COMMANDS = {
            "ping": ping.run,
            "info": info.run,
        }

        def dispatch(name):
            return COMMANDS[name]()
    """)
    write_test(root, "tests/test_existing.py", """
        import unittest
        from harbor.dispatcher import dispatch

        class ExistingCommandTests(unittest.TestCase):
            def test_ping(self):
                self.assertEqual(dispatch("ping"), {"ok": True})

            def test_info(self):
                self.assertEqual(dispatch("info"), {"service": "harbor-service", "mode": "safe"})
    """)
    write_test(root, "tests/test_status.py", """
        import unittest
        from harbor.dispatcher import dispatch

        class StatusCommandTests(unittest.TestCase):
            def test_status_uses_canonical_metadata(self):
                self.assertEqual(
                    dispatch("status"),
                    {"service": "harbor-service", "version": "2.4.1", "mode": "safe"},
                )
    """)


def build_keyhole_read(root: Path) -> None:
    write_file(root, "pyproject.toml", """
        [project]
        name = "catalog-core"
        version = "1.0.0"
        requires-python = ">=3.11"
    """)
    write_file(root, "README.md", """
        # Catalog Core

        The catalog data module is generated in large sections. Avoid unrelated edits.
        Validation: `python3 -m unittest discover -v`.
    """)
    write_file(root, "src/catalog/__init__.py", "")
    lines = ["# Generated catalog constants. Do not reformat unrelated entries.\n"]
    for i in range(1, 1301):
        lines.append(f'ITEM_{i:04d} = "catalog-item-{i:04d}"\n')
    lines.extend([
        "\n",
        "def normalize_sku(value: str) -> str:\n",
        "    return value.strip().upper()\n",
        "\n",
        "def catalog_size() -> int:\n",
        "    return 1300\n",
    ])
    write_file(root, "src/catalog/data.py", "".join(lines))
    write_test(root, "tests/test_catalog.py", """
        import unittest
        from catalog.data import catalog_size, normalize_sku

        class CatalogTests(unittest.TestCase):
            def test_normalize_sku_collapses_whitespace(self):
                self.assertEqual(normalize_sku("  ab  12 cd "), "AB-12-CD")

            def test_existing_compact_sku(self):
                self.assertEqual(normalize_sku("ab-12"), "AB-12")

            def test_generated_catalog_is_intact(self):
                self.assertEqual(catalog_size(), 1300)
    """)


def build_environment_probe(root: Path) -> None:
    write_file(root, "pyproject.toml", """
        [project]
        name = "slug-service"
        version = "0.3.0"
        requires-python = ">=3.11"
    """)
    write_file(root, "README.md", """
        # Slug Service

        Read `ENVIRONMENT.md` before implementation. No third-party packages are required.
    """)
    write_file(root, "ENVIRONMENT.md", """
        # Local toolchain

        Required prerequisites are all knowable before the first execution step:
        - Python 3.11+ (`python3 --version`)
        - Git (`git --version`)
        - local schema helper (`python3 tools/schema_probe.py --version`)

        Normal validation: `python3 -m unittest discover -v`.
    """)
    write_file(root, "tools/schema_probe.py", """
        import sys

        if "--version" in sys.argv:
            print("schema-probe 1.2.0")
            raise SystemExit(0)
        print("usage: schema_probe.py --version", file=sys.stderr)
        raise SystemExit(2)
    """)
    write_file(root, "src/slug_service/__init__.py", "")
    write_file(root, "src/slug_service/render.py", """
        import re

        def render_slug(value: str) -> str:
            # TODO: complete punctuation/whitespace normalization.
            return value.strip().lower()
    """)
    write_test(root, "tests/test_render.py", """
        import unittest
        from slug_service.render import render_slug

        class RenderSlugTests(unittest.TestCase):
            def test_render_slug(self):
                self.assertEqual(
                    render_slug("  Hello, Progressive Context!  "),
                    "hello-progressive-context",
                )
    """)


def build_validation_convergence(root: Path) -> None:
    write_file(root, "pyproject.toml", """
        [project]
        name = "pricing-core"
        version = "1.1.0"
        requires-python = ">=3.11"
    """)
    write_file(root, "README.md", """
        # Pricing Core

        Focused and full unittest commands are the supported validation path. `tools/` also
        contains maintainer convenience wrappers; they are not additional release gates.
    """)
    write_file(root, "src/pricing/__init__.py", "")
    write_file(root, "src/pricing/core.py", """
        from decimal import Decimal, ROUND_HALF_UP

        CENT = Decimal("0.01")

        def tax_total(subtotal: Decimal, tax_percent: Decimal) -> Decimal:
            factor = Decimal("1") + (tax_percent / Decimal("100"))
            return (subtotal * factor).quantize(CENT, rounding=ROUND_HALF_UP)

        def net_total(subtotal: Decimal, discount_percent: Decimal) -> Decimal:
            raise NotImplementedError
    """)
    write_file(root, "tests/__init__.py", "")
    write_test(root, "tests/test_pricing.py", """
        import unittest
        from decimal import Decimal
        from pricing.core import net_total, tax_total

        class PricingTests(unittest.TestCase):
            def test_net_total(self):
                self.assertEqual(
                    net_total(Decimal("100.00"), Decimal("12.5")),
                    Decimal("87.50"),
                )

            def test_tax_total_regression(self):
                self.assertEqual(
                    tax_total(Decimal("100.00"), Decimal("5")),
                    Decimal("105.00"),
                )
    """)
    write_file(root, "tools/smoke.py", """
        import subprocess, sys
        raise SystemExit(subprocess.call([sys.executable, "-m", "unittest", "tests.test_pricing", "-v"]))
    """)
    write_file(root, "tools/deep_recheck.py", """
        import subprocess, sys
        raise SystemExit(subprocess.call([sys.executable, "-m", "unittest", "discover", "-v"]))
    """)


def build_failure_pivot(root: Path) -> None:
    write_file(root, "pyproject.toml", """
        [project]
        name = "checkout-core"
        version = "0.9.0"
        requires-python = ">=3.11"
    """)
    write_file(root, "README.md", """
        # Checkout Core

        Discount configuration is documented in `CONFIGURATION.md`.
        Validation: `python3 -m unittest discover -v`.
    """)
    write_file(root, "CONFIGURATION.md", """
        # Checkout configuration

        `discount` is a percentage string such as `10%`, `7.5%`, or `0%`.
    """)
    write_file(root, "src/checkout/__init__.py", "")
    write_file(root, "src/checkout/config.py", """
        from decimal import Decimal

        def parse_discount(value: str) -> Decimal:
            # Returns a fraction suitable for multiplication.
            return Decimal(value) / Decimal("100")
    """)
    write_file(root, "src/checkout/core.py", """
        from decimal import Decimal, InvalidOperation
        from checkout.config import parse_discount

        CENT = Decimal("0.01")

        def checkout_total(subtotal: Decimal, settings: dict[str, str]) -> Decimal:
            try:
                discount = parse_discount(settings.get("discount", "0%"))
            except (InvalidOperation, ValueError):
                # Existing fallback masks malformed documented configuration.
                discount = Decimal("0")
            return (subtotal * (Decimal("1") - discount)).quantize(CENT)
    """)
    write_test(root, "tests/test_checkout.py", """
        import unittest
        from decimal import Decimal
        from checkout.core import checkout_total

        class CheckoutIntegrationTests(unittest.TestCase):
            def test_documented_discount_format(self):
                self.assertEqual(
                    checkout_total(Decimal("100.00"), {"discount": "10%"}),
                    Decimal("90.00"),
                )

            def test_zero_discount(self):
                self.assertEqual(
                    checkout_total(Decimal("100.00"), {"discount": "0%"}),
                    Decimal("100.00"),
                )
    """)


def build_polling_discipline(root: Path) -> None:
    write_file(root, "pyproject.toml", """
        [project]
        name = "build-label"
        version = "1.8.0"
        requires-python = ">=3.11"
    """)
    write_file(root, "README.md", """
        # Build Label

        The task-specific prompt names the required validation command.
    """)
    write_file(root, "src/build_label/__init__.py", "")
    write_file(root, "src/build_label/core.py", """
        def build_label(name: str, version: str) -> str:
            return f"{name}:{version}"
    """)
    write_file(root, "tools/slow_validation.py", """
        import sys
        import time
        from pathlib import Path

        sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
        from build_label.core import build_label

        print("slow validation started", flush=True)
        time.sleep(35)
        actual = build_label("progressive", "1.8.0")
        if actual != "progressive@1.8.0":
            print(f"expected progressive@1.8.0, got {actual}", file=sys.stderr)
            raise SystemExit(1)
        print("slow validation passed", flush=True)
    """)


FIXTURE_BUILDERS = {
    "recon_batch": build_recon_batch,
    "keyhole_read": build_keyhole_read,
    "environment_probe": build_environment_probe,
    "validation_convergence": build_validation_convergence,
    "failure_pivot": build_failure_pivot,
    "polling_discipline": build_polling_discipline,
}


def materialize_fixture(fixture: str, destination: Path) -> None:
    if fixture not in FIXTURE_BUILDERS:
        raise ValueError(f"unknown fixture: {fixture}")
    destination.mkdir(parents=True, exist_ok=True)
    FIXTURE_BUILDERS[fixture](destination)


def fixture_digest(root: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted(p for p in root.rglob("*") if p.is_file() and ".git" not in p.parts):
        rel = path.relative_to(root).as_posix()
        digest.update(rel.encode("utf-8") + b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()
