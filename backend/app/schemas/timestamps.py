from datetime import UTC, datetime


def utc_z_timestamp(value: datetime | None) -> str | None:
    if value is None:
        return None
    # Normalize DB/provider datetimes for stable frontend rendering and API examples.
    if value.tzinfo is None:
        value = value.replace(tzinfo=UTC)
    return value.astimezone(UTC).isoformat().replace("+00:00", "Z")
