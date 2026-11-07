"""Unit tests for Timetable models."""

import unittest

from campus.common import schema
from campus.common.errors import ValidationError
from campus.model import LessonGroup, Timetable, TimetableEntry, TimetableMetadata


class TestTimetableMetadata(unittest.TestCase):
    """Tests for TimetableMetadata construction and validation."""

    def test_valid_metadata(self):
        """Constructing TimetableMetadata with a valid filename succeeds."""
        meta = TimetableMetadata(
            filename="2026.xml",
            start_date="2026-01-01T00:00:00Z",
            end_date="2026-12-31T00:00:00Z"
        )
        self.assertEqual(meta.filename, "2026.xml")

    def test_empty_filename_rejected(self):
        """Empty filename raises ValidationError with a filename field error.

        Regression test for #600: timetable.new() used to accept and
        store a timetable with an empty filename.
        """
        with self.assertRaises(ValidationError) as ctx:
            TimetableMetadata(
                filename="",
                start_date="2026-01-01T00:00:00Z",
                end_date="2026-12-31T00:00:00Z"
            )
        self.assertEqual(ctx.exception.status_code, 422)
        self.assertEqual(ctx.exception.error_code, "VALIDATION_FAILED")
        fields = [e["field"] for e in ctx.exception.field_errors]
        self.assertIn("filename", fields)


class TestTimetable(unittest.TestCase):
    """Tests for the Timetable API model."""

    def test_timetable_inherits_filename_validation(self):
        """Timetable rejects an empty filename like its metadata base."""
        with self.assertRaises(ValidationError):
            Timetable(
                filename=schema.String(""),
                start_date="2026-01-01T00:00:00Z",
                end_date="2026-12-31T00:00:00Z",
                entries=[]
            )

    def test_timetable_valid(self):
        """Timetable with a valid filename and entries constructs."""
        tt = Timetable(
            filename="2026.xml",
            start_date="2026-01-01T00:00:00Z",
            end_date="2026-12-31T00:00:00Z",
            entries=[]
        )
        self.assertEqual(tt.filename, "2026.xml")
        self.assertEqual(tt.entries, [])


class TestLessonGroup(unittest.TestCase):
    """Tests for LessonGroup construction and documented identity semantics."""

    def test_construction_defaults(self):
        """LessonGroup mints a category uid and keeps label/timetable_id."""
        lg = LessonGroup(timetable_id="uid-timetable-1", label="2527-COM")
        self.assertTrue(str(lg.id))  # fresh identity minted
        self.assertEqual(lg.label, "2527-COM")
        self.assertEqual(lg.timetable_id, "uid-timetable-1")


class TestTimetableEntryLabelPersistence(unittest.TestCase):
    """TimetableEntry.label is persisted (campus-model#5).

    Entries are self-describing per version: the label rides
    to_storage() so historical allocations keep rendering labels after
    the LessonGroup row is reused (by label match) for a newer
    allocation. Legacy records created before persistence lack the
    field entirely and deserialize to the None default.
    """

    def _make_entry(self, **overrides) -> TimetableEntry:
        defaults = {
            "timetable_id": "uid-timetable-1",
            "lessongroup_id": "uid-lesson-group-1",
            "venue": "5-64",
            "weekday": "Mon A",
            "timeslot": "0800",
            "label": "2527-COM",
        }
        defaults.update(overrides)
        return TimetableEntry(**defaults)

    def test_to_storage_carries_label(self):
        """to_storage() persists the label instead of dropping it."""
        entry = self._make_entry()
        self.assertEqual(entry.to_storage()["label"], "2527-COM")

    def test_label_defaults_to_none(self):
        """A label-less entry stores None."""
        entry = self._make_entry(label=None)
        self.assertIsNone(entry.to_storage()["label"])

    def test_from_storage_reads_persisted_label(self):
        """A stored label round-trips back as a plain str coerced to type."""
        entry = TimetableEntry.from_storage(self._make_entry().to_storage())
        self.assertEqual(entry.label, "2527-COM")

    def test_from_storage_tolerates_missing_label(self):
        """Legacy records (pre-persistence) deserialize with label None."""
        record = self._make_entry(label=None).to_storage()
        del record["label"]
        entry = TimetableEntry.from_storage(record)
        self.assertIsNone(entry.label)


if __name__ == '__main__':
    unittest.main()
