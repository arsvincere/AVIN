#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

from __future__ import annotations

import enum


class Direction(enum.Enum):  # {{{
    UNDEFINE = 0
    BUY = 1
    SELL = 2

    @classmethod  # fromStr
    def fromStr(cls, string: str) -> Direction:
        directions = {
            "BUY": cls.BUY,
            "SELL": cls.SELL,
        }
        return directions[string]


# }}}
