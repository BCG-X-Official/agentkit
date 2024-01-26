# -*- coding: utf-8 -*-
"""UUID version 7 features a time-ordered value field derived from the."""

import secrets
import time

from app.utils.uuid_ import UUID_

_last_v7_timestamp = None


class UUID7(UUID_):
    """
    UUID version 7 features a time-ordered value field derived from the widely
    implemented and well known Unix Epoch timestamp source, the number of milliseconds
    seconds since midnight 1 Jan 1970 UTC, leap seconds excluded.

    As well as improved entropy characteristics over versions 1 or 6. Implementations
    SHOULD utilize UUID version 7 over UUID version 1 and 6 if possible.
    """


def uuid7() -> UUID7:
    """Requires separate function as UUID is immutable."""
    global _last_v7_timestamp  # pylint: disable=global-statement

    nanoseconds = time.time_ns()
    if _last_v7_timestamp is not None and nanoseconds <= _last_v7_timestamp:
        nanoseconds = _last_v7_timestamp + 1
    _last_v7_timestamp = nanoseconds
    (
        timestamp_ms,
        timestamp_ns,
    ) = divmod(
        nanoseconds,
        10**6,
    )
    subsec = subsec_encode(timestamp_ns)
    subsec_a = subsec >> 8
    subsec_b = subsec & 0xFF
    rand = secrets.randbits(54)
    uuid_int = (timestamp_ms & 0xFFFFFFFFFFFF) << 80
    uuid_int |= subsec_a << 64
    uuid_int |= subsec_b << 54
    uuid_int |= rand
    return UUID7(
        int_=uuid_int,
        version=7,
    )


def subsec_encode(
    value: int,
) -> int:
    return value * 2**20 // 10**6
