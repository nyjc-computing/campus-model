"""Unit tests for the HostedApp model (campus-classroom#81)."""

import unittest

from campus.model import HostedApp


def make_app(**overrides) -> HostedApp:
    fields = {
        "slug": "quest-dom",
        "name": "Quest DOM",
        "content_hash": "a" * 64,
        "size": 1234,
        "content_type": "text/html",
    }
    fields.update(overrides)
    return HostedApp(**fields)


class TestHostedAppConstruction(unittest.TestCase):
    """Construction defaults and validation."""

    def test_valid_app_gets_defaults(self):
        app = make_app()
        self.assertTrue(app.id.startswith("uid-hostedapp-"))
        self.assertEqual(app.slug, "quest-dom")
        self.assertEqual(app.status, "published")
        self.assertEqual(app.content_type, "text/html")
        self.assertIsNotNone(app.created_at)
        self.assertIsNotNone(app.updated_at)

    def test_name_defaults_to_none(self):
        app = make_app(name=None)
        self.assertIsNone(app.name)

    def test_content_hash_optional_before_first_publish(self):
        app = make_app(content_hash=None, size=None)
        self.assertIsNone(app.content_hash)
        self.assertIsNone(app.size)

    def test_invalid_slug_rejected(self):
        for slug in ("Quest DOM", "has space", "", "has/slash", "UPPER"):
            with self.assertRaises(ValueError, msg=slug):
                make_app(slug=slug)

    def test_invalid_content_hash_rejected(self):
        with self.assertRaises(ValueError):
            make_app(content_hash="not-a-hash")
        with self.assertRaises(ValueError):
            make_app(content_hash="a" * 63)

    def test_invalid_status_rejected(self):
        with self.assertRaises(ValueError):
            make_app(status="approved")
        app = make_app(status="pending")
        self.assertEqual(app.status, "pending")


class TestHostedAppResource(unittest.TestCase):
    """Resource and storage round-trips."""

    def test_resource_round_trip(self):
        app = make_app()
        resource = app.to_resource()
        self.assertEqual(resource["slug"], "quest-dom")
        self.assertEqual(resource["content_hash"], "a" * 64)
        self.assertEqual(resource["status"], "published")
        rebuilt = HostedApp.from_resource(resource)
        self.assertEqual(rebuilt.slug, app.slug)
        self.assertEqual(rebuilt.name, app.name)
        self.assertEqual(rebuilt.content_hash, app.content_hash)
        self.assertEqual(rebuilt.status, app.status)

    def test_storage_round_trip(self):
        app = make_app()
        record = app.to_storage()
        self.assertIn("slug", record)
        self.assertIn("content_hash", record)
        rebuilt = HostedApp.from_storage(record)
        self.assertEqual(rebuilt.slug, app.slug)
        self.assertEqual(rebuilt.name, app.name)


if __name__ == "__main__":
    unittest.main()
