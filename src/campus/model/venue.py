"""campus.model.venue

Venue model for Campus.

Venues are managed with a deliberately fluid schema (campus#1099): each
venue is a document whose identifying facts live in freeform `metadata`
and whose freeform commentary lives in `notes` (markdown). Stable
metadata fields will be hoisted into model fields as they settle.
"""

import typing
from dataclasses import dataclass, field

from campus.common import schema
from campus.common.utils import uid

from .base import Model


@dataclass(eq=False, kw_only=True)
class Venue(Model):
    """A bookable campus venue, stored as a document.

    The venue schema is fluid: facts (name, type, capacity, location,
    ...) are kept in freeform `metadata` until they stabilise, and
    commentary is kept as markdown in `notes` (campus#1099).

    Fields:
      id (CampusID): Unique identifier for the venue.
      metadata (dict): Freeform venue facts; unstructured by design.
      notes (str | None): Freeform markdown notes; None = no notes.
      updated_at (DateTime | None): Last mutation stamp; set by the API
        resource layer (None until the venue's first update).
    """
    id: schema.CampusID = field(default_factory=(
        lambda: uid.generate_category_uid("venue", length=8)
    ))
    metadata: dict[str, typing.Any] = field(default_factory=dict)
    notes: str | None = None
    updated_at: schema.DateTime | None = None
