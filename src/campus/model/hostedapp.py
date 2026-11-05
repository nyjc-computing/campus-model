"""campus.model.hostedapp

HostedApp model definitions for Campus.

A HostedApp is a single-file HTML app published to Campus's app
hosting origin (campus-apphost; classroom#81): publishers upload via
campus.api /hostedapps, teachers reference apps by slug in document
questions (`data: {slug}`), and the serving origin serves the file's
current bytes.

Identity vs storage, deliberately decoupled:

- The **slug** is the app's stable hosting/reference address
  (user-chosen, immutable — references break if the address changes).
- The bytes are stored **content-addressed** under ``content_hash``
  (sha256) — an opaque key, so guessable addresses reveal no stable
  fetch path, and re-publishing new content under the same slug
  re-points the app at the new hash.
- The **name** is display-only (pickers/UI); renderers fall back to
  the slug when absent.
"""

import re
from dataclasses import dataclass, field

from campus.common import schema
from campus.common.utils import uid

from . import constraints
from .base import Model

SLUG_PATTERN = re.compile(r"^[a-z0-9._-]+$")
# Lowercase hex sha256 digest — the object-storage key and the
# integrity check at serve time.
CONTENT_HASH_PATTERN = re.compile(r"^[0-9a-f]{64}$")

# Approval gating (classroom#81): dev publishes immediately;
# prod deployments gate new uploads behind "pending" before serving.
STATUS_PENDING = "pending"
STATUS_PUBLISHED = "published"
STATUSES = frozenset({STATUS_PENDING, STATUS_PUBLISHED})


@dataclass(eq=False, kw_only=True)
class HostedApp(Model):
    """A single-file HTML app published to Campus app hosting.

    Published via campus.api /hostedapps (raw bytes + optional display
    name); content is stored content-addressed under ``content_hash``,
    so replacing an app's bytes under the same slug re-points it at the
    new hash and every referencing assignment serves the new version.
    """
    id: schema.CampusID = field(default_factory=(
        lambda: uid.generate_category_uid("hostedapp", length=8)
    ))
    # created_at inherited from Model
    # Immutable: the slug is referenced by published document questions;
    # renaming would silently break those references (delete + recreate
    # under a new slug instead).
    slug: str = field(metadata={
        "constraints": [constraints.UNIQUE],
        "mutable": False,
    })
    # Display name for pickers/UI; None renders as the slug.
    name: str | None = field(default=None, metadata={"mutable": True})
    # sha256 hex digest of the current bytes — object-storage key and
    # serve-time integrity check. None before the first content upload.
    content_hash: str | None = field(default=None, metadata={"mutable": True})
    size: int | None = field(default=None, metadata={"mutable": True})
    content_type: str = field(default="text/html", metadata={"mutable": True})
    status: str = field(default=STATUS_PUBLISHED, metadata={"mutable": True})
    uploaded_by_client_id: str | None = field(
        default=None, metadata={"mutable": False}
    )
    uploaded_by_user_id: str | None = field(
        default=None, metadata={"mutable": False}
    )
    updated_at: schema.DateTime = field(
        default_factory=schema.DateTime.utcnow,
        metadata={"mutable": True}
    )

    def __post_init__(self) -> None:
        """Validate the slug, content hash, and status."""
        if not SLUG_PATTERN.fullmatch(self.slug):
            raise ValueError(
                f"Invalid hosted app slug: {self.slug!r}. Slugs are the "
                f"app's address and must match {SLUG_PATTERN.pattern} "
                "(lowercase letters, digits, dots, dashes)."
            )
        if self.content_hash is not None \
                and not CONTENT_HASH_PATTERN.fullmatch(self.content_hash):
            raise ValueError(
                f"Invalid content hash: {self.content_hash!r}. Must be a "
                "64-character lowercase sha256 hex digest."
            )
        if self.status not in STATUSES:
            raise ValueError(
                f"Invalid status: {self.status!r}. "
                f"Valid statuses: {', '.join(sorted(STATUSES))}."
            )
