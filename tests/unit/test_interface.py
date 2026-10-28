"""campus_model public-interface closed-world guard and manifest check.

The public interface of campus.model is two-tier:

- The module tree is public by definition: importing submodules
  (``from campus.model.base import Model``, ``campus.model.constraints``)
  is a supported pattern — storage backends and downstream apps rely on
  it.
- Symbol re-exports are public if and only if they are listed in the
  containing package's ``__all__`` (the flat class surface:
  ``from campus.model import User``). Anything underscore-prefixed is
  private by convention.

Unlike campus.common, campus.model's ``__all__`` names classes rather
than submodules, so the tree-closure rule here is inverted: leaf
modules that declare their own ``__all__`` (audit, classroom, emailotp,
http) must only declare names the package also re-exports.

These tests keep ``__all__`` honest in both directions (declared names
must actually import; re-exported symbols must be declared), and verify
the checked-in interface manifest matches reality, so any interface
change is a deliberate, diffable commit that ships with a CHANGELOG
entry and the version bump the diff dictates (additive -> patch,
breaking -> minor).
"""

import ast
import importlib
import json
import pathlib
import unittest

import campus.model

SRC = pathlib.Path(campus.model.__file__).resolve().parent
MANIFEST = pathlib.Path(__file__).resolve().parents[1] / "interface_manifest.json"

# Package whose __init__ __all__ is contract ("" = campus.model itself).
PACKAGES = [""]

# Leaf modules that declare an __all__ of their own.
DECLARED_LEAVES = [
    "audit",
    "classroom",
    "emailotp",
    "http",
]


def _all_of(tree: ast.Module) -> list[str]:
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if getattr(target, "id", None) == "__all__":
                    return [e.value for e in node.value.elts if isinstance(e, ast.Constant)]
    raise AssertionError("no __all__ defined")


def _module_init(mod_path: pathlib.Path) -> ast.Module:
    return ast.parse(mod_path.read_text(encoding="utf-8"))


def _leaf_init(leaf: str) -> ast.Module:
    """AST of a declared leaf's __all__: emailotp is a package, the rest are modules."""
    pkg_dir = SRC / leaf
    if pkg_dir.is_dir():
        return _module_init(pkg_dir / "__init__.py")
    return _module_init(SRC / f"{leaf}.py")


def build_interface_manifest() -> dict[str, list[str]]:
    """The full declared-interface snapshot, as a JSON-ready dict."""
    manifest: dict[str, list[str]] = {}
    for pkg in PACKAGES:
        rel = "campus.model" + (f".{pkg}" if pkg else "")
        manifest[rel] = sorted(_all_of(_module_init(SRC / pkg if pkg else SRC / "__init__.py")))
    for leaf in DECLARED_LEAVES:
        mod = importlib.import_module(f"campus.model.{leaf}")
        manifest[f"campus.model.{leaf}"] = sorted(mod.__all__)
    return manifest


class TestPackageInterface(unittest.TestCase):
    """__all__ closure rules for the package."""

    def test_all_importable_and_no_underscores(self):
        for pkg in PACKAGES:
            with self.subTest(pkg=pkg or "campus.model"):
                module = importlib.import_module("campus.model" + (f".{pkg}" if pkg else ""))
                for name in module.__all__:
                    self.assertFalse(name.startswith("_"), name)
                    self.assertIsNotNone(getattr(module, name))

    def test_init_reexports_declared(self):
        """Every `from .x import Y` in the package __init__ must be declared."""
        for pkg in PACKAGES:
            with self.subTest(pkg=pkg or "campus.model"):
                pkg_path = SRC / pkg if pkg else SRC / "__init__.py"
                tree = _module_init(pkg_path)
                declared = set(_all_of(tree))
                for node in tree.body:
                    if isinstance(node, ast.ImportFrom) and node.level == 1:
                        for alias in node.names:
                            if alias.name != "*" and not alias.name.startswith("_"):
                                self.assertIn(alias.asname or alias.name, declared)


class TestLeafSurfaces(unittest.TestCase):
    """Leaf modules declaring __all__ must stay inside the package surface."""

    def test_leaf_declared_names_are_package_reexports(self):
        for leaf in DECLARED_LEAVES:
            with self.subTest(leaf=leaf):
                leaf_all = set(_all_of(_leaf_init(leaf)))
                package_all = set(_all_of(_module_init(SRC / "__init__.py")))
                self.assertEqual(
                    leaf_all & package_all,
                    leaf_all,
                    f"campus.model.{leaf}.__all__ declares names the package does not re-export",
                )


class TestInterfaceManifest(unittest.TestCase):
    """The checked-in manifest must match reality exactly (diff = deliberate)."""

    def test_manifest_matches_reality(self):
        committed = json.loads(MANIFEST.read_text(encoding="utf-8"))
        self.assertEqual(committed, build_interface_manifest())


if __name__ == "__main__":
    unittest.main()
