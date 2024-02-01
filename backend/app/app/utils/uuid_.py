# -*- coding: utf-8 -*-
r"""UUID draft version objects (universally unique identifiers).
This module provides the functions uuid6() and uuid7() for
generating version 6 and 7 UUIDs as specified in
https://github.com/uuid6/uuid6-ietf-draft.

Repo: https://github.com/oittaa/uuid6-python
"""

import uuid
from typing import Optional


class UUID_(uuid.UUID):
    """UUID draft version objects."""

    def __init__(
        self,
        hex_: Optional[str] = None,
        bytes_: Optional[bytes] = None,
        bytes_le: Optional[bytes] = None,
        fields: Optional[
            tuple[
                int,
                int,
                int,
                int,
                int,
                int,
            ]
        ] = None,
        int_: Optional[int] = None,
        version: Optional[int] = None,
        *,
        is_safe: uuid.SafeUUID = uuid.SafeUUID.unknown,
    ) -> None:
        if (
            int_ is None
            or [
                hex_,
                bytes_,
                bytes_le,
                fields,
            ].count(None)
            != 4
        ):
            super().__init__(
                hex=hex_,
                bytes=bytes_,
                bytes_le=bytes_le,
                fields=fields,
                int=int_,
                version=version,
                is_safe=is_safe,
            )
            return
        if version is not None:
            if not 6 <= version <= 7:
                raise ValueError("illegal version number")
            # Set the variant to RFC 4122.
            int_ &= ~(0xC000 << 48)
            int_ |= 0x8000 << 48
            # Set the version number.
            int_ &= ~(0xF000 << 64)
            int_ |= version << 76
        super().__init__(
            int=int_,
            is_safe=is_safe,
        )

    @property
    def subsec(
        self,
    ) -> int:
        return ((self.int >> 64) & 0x0FFF) << 8 | ((self.int >> 54) & 0xFF)

    @property
    def time(
        self,
    ) -> int:
        if self.version == 6:
            return (self.time_low << 28) | (self.time_mid << 12) | (self.time_hi_version & 0x0FFF)
        if self.version == 7:
            return (self.int >> 80) * 10**6 + self._subsec_decode(self.subsec)
        return super().time

    @staticmethod
    def _subsec_decode(
        value: int,
    ) -> int:
        return -(-value * 10**6 // 2**20)
