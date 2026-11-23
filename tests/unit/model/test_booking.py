"""Unit tests for the VenueBooking model (campus#1217)."""

import unittest

from campus.common import schema
from campus.model import VenueBooking


class TestVenueBooking(unittest.TestCase):
    """Tests for VenueBooking construction and storage round-trips."""

    def _booking(self, **overrides) -> VenueBooking:
        fields = {
            "user_id": schema.UserID("teacher@campus.test"),
            "venue_id": schema.CampusID("uid-venue-abcd1234"),
            "description": "CCA training",
            "start_time": schema.Time("1600"),
            "end_time": schema.Time("1800"),
            "date": schema.Date("2026-11-24"),
        }
        fields.update(overrides)
        return VenueBooking(**fields)

    def test_status_defaults_to_pending(self):
        """A new booking is pending; the id carries the booking prefix."""
        booking = self._booking()
        self.assertEqual(booking.status, "pending")
        self.assertTrue(booking.id.startswith("uid-booking-"))
        self.assertIsInstance(booking.created_at, schema.DateTime)

    def test_round_trip_preserves_status(self):
        """to_storage/from_storage preserve every field including status."""
        booking = self._booking()
        record = booking.to_storage()
        restored = VenueBooking.from_storage(record)
        self.assertEqual(restored.status, "pending")
        self.assertEqual(restored.venue_id, booking.venue_id)
        self.assertEqual(restored.date, booking.date)
        self.assertEqual(restored.start_time, booking.start_time)

    def test_from_storage_missing_status_reads_pending(self):
        """Records written before the status column deserialize as pending."""
        restored = VenueBooking.from_storage({
            "id": "uid-booking-abcd1234",
            "created_at": "2026-11-23T00:00:00Z",
            "user_id": "teacher@campus.test",
            "venue_id": "uid-venue-abcd1234",
            "description": "CCA training",
            "start_time": "1600",
            "end_time": "1800",
            "date": "2026-11-24",
        })
        self.assertEqual(restored.status, "pending")

    def test_validate_update_accepts_status_and_rejects_unknown(self):
        """status is a model field; unknown fields stay rejected."""
        VenueBooking.validate_update({"status": "approved"})
        with self.assertRaises(ValueError):
            VenueBooking.validate_update({"decision": "approved"})


if __name__ == "__main__":
    unittest.main()
