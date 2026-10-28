"""campus_model boundary guard: stdlib + campus.common only, no third party.

campus.model is the domain vocabulary of the campus namespace: pure
dataclass entities with no business logic. Its dependencies are exactly
the stdlib and campus.common (schema, errors, utils) — it imports no
other campus sibling and no third-party module whatsoever, not even
lazily: the OTP template rendering that used to drag flask in at call
time moved to campus.api.emailotp_templates (#970 phase 3 prep), so
flask/werkzeug are banned outright rather than lazy-only.

Checked with ast over the source files rather than by importing, so the
guard cannot itself be defeated by import-time side effects.
"""

import ast
import pathlib
import sys
import unittest

SRC = pathlib.Path(__file__).resolve().parents[2] / "src" / "campus" / "model"


def iter_module_trees():
    for path in sorted(SRC.rglob("*.py")):
        yield path, ast.parse(path.read_text(encoding="utf-8"))


def import_targets(node: ast.stmt):
    if isinstance(node, ast.Import):
        for alias in node.names:
            yield alias.name
    elif isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
        yield node.module


class TestModelBoundaries(unittest.TestCase):
    """AST checks over src/campus/model (see module docstring)."""

    def test_no_campus_sibling_imports(self):
        offenders = []
        for path, tree in iter_module_trees():
            for node in ast.walk(tree):
                for target in import_targets(node):
                    if target == "campus":
                        offenders.append(f"{path.relative_to(SRC)}: import campus")
                        continue
                    if not target.startswith("campus."):
                        continue
                    sibling = target[len("campus."):].split(".", 1)[0]
                    # campus.common is the kernel; campus.model is itself.
                    if sibling not in {"common", "model"}:
                        offenders.append(f"{path.relative_to(SRC)}: {target}")
        self.assertEqual(
            [],
            offenders,
            "campus.model must not import campus.* siblings other than campus.common",
        )

    def test_no_third_party_imports(self):
        """Test that no import target leaves the stdlib (even inside functions)."""
        offenders = []
        for path, tree in iter_module_trees():
            for node in ast.walk(tree):
                for target in import_targets(node):
                    top = target.split(".", 1)[0]
                    if top not in sys.stdlib_module_names and top != "campus":
                        offenders.append(f"{path.relative_to(SRC)}: {target}")
        self.assertEqual(
            [],
            offenders,
            "campus.model must import the stdlib and campus.* only — no third party",
        )


if __name__ == "__main__":
    unittest.main()
