#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

from __future__ import annotations

import enum


class DataSource(enum.Enum):
    MOEX = 1
    TINKOFF = 2

    @classmethod  # fromStr  # {{{
    def fromStr(cls, string) -> DataSource:
        sources = {
            "MOEX": DataSource.MOEX,
            "TINKOFF": DataSource.TINKOFF,
        }
        return sources[string]

    # }}}
    @classmethod  # fromRecord  # {{{
    def fromRecord(cls, record: asyncpg.Record) -> DataSource:
        string = record["source"]
        source = cls.fromStr(string)
        return source

    # }}}


if __name__ == "__main__":
    ...
