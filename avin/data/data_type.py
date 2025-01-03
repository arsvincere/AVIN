#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

from __future__ import annotations

import enum
from datetime import timedelta


class DataType(enum.Enum):
    """Enum for selet what data type to download."""

    BAR_1M = "1M"
    BAR_5M = "5M"
    BAR_10M = "10M"
    BAR_1H = "1H"
    BAR_D = "D"
    BAR_W = "W"
    BAR_M = "M"
    TIC = "tic"
    BOOK = "book"

    def __str__(self):  # {{{
        return self.value

    # }}}
    def __hash__(self):  # {{{
        return hash(self.name)

    # }}}
    def toTimeDelta(self):  # {{{
        periods = {
            "1M": timedelta(minutes=1),
            "5M": timedelta(minutes=5),
            "10M": timedelta(minutes=10),
            "1H": timedelta(hours=1),
            "D": timedelta(days=1),
            "W": timedelta(weeks=1),
            "M": timedelta(days=30),
        }
        return periods[self.value]

    # }}}
    @classmethod  # fromStr  #{{{
    def fromStr(cls, string_type: str):
        types = {
            "1M": DataType.BAR_1M,
            "5M": DataType.BAR_5M,
            "10M": DataType.BAR_10M,
            "1H": DataType.BAR_1H,
            "D": DataType.BAR_D,
            "W": DataType.BAR_W,
            "M": DataType.BAR_M,
            "BAR_1M": DataType.BAR_1M,
            "BAR_5M": DataType.BAR_5M,
            "BAR_10M": DataType.BAR_10M,
            "BAR_1H": DataType.BAR_1H,
            "BAR_D": DataType.BAR_D,
            "BAR_W": DataType.BAR_W,
            "BAR_M": DataType.BAR_M,
            "tic": DataType.TIC,
            "book": DataType.BOOK,
        }
        return types[string_type]

    # }}}
    @classmethod  # fromRecord  #{{{
    def fromRecord(cls, record: asyncpg.Record):
        type_name = record["data_type"]
        typ = cls.fromStr(type_name)
        return typ

    # }}}


if __name__ == "__main__":
    ...
