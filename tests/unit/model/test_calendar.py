"""Unit tests for the CalendarDay model (the school calendar, TTv2)."""

import unittest

from campus.model import CalendarDay
from campus.model.calendar import DAY_CODE_VOCABULARY, FREE_CODE, TT_DAY_CODES


def make_day(**overrides) -> CalendarDay:
    fields = {
        "id": "2027-01-11",
        "j1_code": "Mon A",
        "j2_code": "Mon A",
        "term_week": "T1 W1",
    }
    fields.update(overrides)
    return CalendarDay(**fields)


class TestCalendarDayConstruction(unittest.TestCase):
    """Construction defaults and the date-as-identity convention."""

    def test_date_is_the_identity(self):
        day = make_day()
        self.assertEqual(day.id, "2027-01-11")

    def test_codes_default_to_unset(self):
        day = make_day(j1_code=None, j2_code=None, term_week=None)
        self.assertIsNone(day.j1_code)
        self.assertIsNone(day.j2_code)
        self.assertIsNone(day.term_week)

    def test_vocabulary_shape(self):
        # Ten TT days — the two-week Mon A..Fri B cycle — plus Free.
        self.assertEqual(len(TT_DAY_CODES), 10)
        self.assertEqual(FREE_CODE, "Free")
        self.assertEqual(DAY_CODE_VOCABULARY, TT_DAY_CODES + (FREE_CODE,))
        self.assertEqual(TT_DAY_CODES[0], "Mon A")
        self.assertEqual(TT_DAY_CODES[-1], "Fri B")


class TestCalendarDayStorageRoundTrip(unittest.TestCase):
    """Storage records carry plain strings; Optional fields coerce."""

    def test_from_storage_coerces_fields(self):
        record = {
            "id": "2027-03-22",
            "j1_code": "Mon B",
            "j2_code": "Free",
            "term_week": "T2 W1",
        }
        day = CalendarDay.from_storage(record)
        self.assertEqual(day.id, "2027-03-22")
        self.assertEqual(day.j1_code, "Mon B")
        self.assertEqual(day.j2_code, "Free")
        self.assertEqual(day.term_week, "T2 W1")

    def test_from_storage_falls_back_to_none_defaults(self):
        # Sparse records (a date seeded before its codes were decided)
        # deserialize with the field defaults.
        day = CalendarDay.from_storage({"id": "2027-06-01"})
        self.assertIsNone(day.j1_code)
        self.assertIsNone(day.j2_code)
        self.assertIsNone(day.term_week)
