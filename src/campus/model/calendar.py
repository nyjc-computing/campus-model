"""campus.model.calendar

The school-calendar model: one row per calendar date, saying which TT
day each cohort runs — or that the date is Free (v1's NSD).

This carries the v1 calendar row forward with the fields the v2 model
does not need dropped: the version in force is campus.api's
effective-dated pointer trail's job now (per-date stamping was v1's
import), and venue occupancy was booking-era data. What survives is
the committee-editable core — the per-cohort day-code pair — plus the
term-week label the year's seed writes for display (in v1 nothing
wrote those labels; the seed is what fixes that open question).

The day-code vocabulary is the timetable cycle: ten TT days (the
two-week Mon A..Fri B cycle the Untis exports name) plus the explicit
"Free" code. campus.api validates calendar writes against
DAY_CODE_VOCABULARY; the day-code pair is what timetable grids,
the Manage Calendar editor, and any future booking validator all read.
"""

from dataclasses import dataclass

from campus.common import schema

from .base import Model

# The timetable cycle: ten TT days — week A and week B of the two-week
# cycle, named as the Untis exports name them. "Free" marks a
# no-school day (public holiday, off-in-lieu, scheduled school
# holiday): no lessons run, but the date stays a row so the committee
# can see it on the month grid and edit it.
TT_DAY_CODES: tuple[str, ...] = (
    "Mon A",
    "Tue A",
    "Wed A",
    "Thu A",
    "Fri A",
    "Mon B",
    "Tue B",
    "Wed B",
    "Thu B",
    "Fri B",
)
FREE_CODE = "Free"

DAY_CODE_VOCABULARY: tuple[str, ...] = TT_DAY_CODES + (FREE_CODE,)


@dataclass(eq=False, kw_only=True)
class CalendarDay(Model):
    """One school-calendar row, keyed by its own date.

    `id` carries the calendar date in ISO form (`YYYY-MM-DD`) — the
    date IS the identity, so rows are addressed by date everywhere
    (the month grid, the day editor, the year seed) and there is
    exactly one row per date. campus.api's write path validates the
    format and the code vocabulary.

    Fields:
      j1_code (String | None): JC1's TT day code for the date, from
        DAY_CODE_VOCABULARY; None leaves the field unset (the day
        editor's "select schedule"), which behaves as a day with no
        lessons.
      j2_code (String | None): JC2's TT day code, same rules.
      term_week (String | None): the seeded term-week label (e.g.
        "T1 W2"), display data for grids and reports; no resolution
        logic reads it.
    """

    id: schema.CampusID
    j1_code: schema.String | None = None
    j2_code: schema.String | None = None
    term_week: schema.String | None = None
