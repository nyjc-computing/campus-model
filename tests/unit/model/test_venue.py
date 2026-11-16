"""Unit tests for the Venue model (campus-model#9)."""

import unittest

from campus.common import schema
from campus.model import Venue


class TestVenue(unittest.TestCase):
    """Tests for Venue construction and storage round-trips."""

    def test_defaults(self):
        """A venue with no metadata or notes gets empty defaults."""
        venue = Venue()
        self.assertTrue(venue.id.startswith("uid-venue-"))
        self.assertEqual(venue.metadata, {})
        self.assertIsNone(venue.notes)
        self.assertIsNone(venue.updated_at)
        self.assertIsInstance(venue.created_at, schema.DateTime)

    def test_metadata_and_notes_round_trip(self):
        """to_storage/from_storage preserve metadata, notes, updated_at."""
        venue = Venue(
            metadata={"name": "B1-01", "capacity": 40},
            notes="Projector **broken** — book IT before use.",
        )
        record = venue.to_storage()
        self.assertEqual(record["metadata"]["name"], "B1-01")
        restored = Venue.from_storage(record)
        self.assertEqual(restored.metadata, {"name": "B1-01", "capacity": 40})
        self.assertEqual(
            restored.notes,
            "Projector **broken** — book IT before use.",
        )
        self.assertEqual(restored.id, venue.id)
        self.assertEqual(restored.created_at, venue.created_at)

    def test_from_storage_missing_optional_fields(self):
        """Records written before notes/updated_at deserialize with defaults."""
        venue = Venue.from_storage({
            "id": "venue_abcd1234",
            "created_at": "2026-11-16T00:00:00Z",
        })
        self.assertEqual(venue.metadata, {})
        self.assertIsNone(venue.notes)
        self.assertIsNone(venue.updated_at)

    def test_validate_update_rejects_unknown_field(self):
        """validate_update rejects fields that are not model fields."""
        with self.assertRaises(ValueError):
            Venue.validate_update({"venue_name": "B1-01"})


if __name__ == "__main__":
    unittest.main()
