#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

from __future__ import annotations

import enum


class Size(enum.Enum):
    BLACKSWAN_SMALL = -7
    ANOMAL_SMALL = -6
    EXTRA_SMALL = -5
    VERY_SMALL = -4
    SMALLEST = -3
    SMALLER = -2
    SMALL = -1
    NORMAL = 0
    BIG = 1
    BIGGER = 2
    BIGGEST = 3
    VERY_BIG = 4
    EXTRA_BIG = 5
    ANOMAL_BIG = 6
    BLACKSWAN_BIG = 7

    def __lt__(self, other):  # operator <  # {{{
        assert isinstance(other, Size)
        return self.value < other.value

    # }}}
    def __le__(self, other):  # operator <=  # {{{
        assert isinstance(other, Size)
        return self.value <= other.value

    # }}}
    def __gt__(self, other):  # operator >  # {{{
        assert isinstance(other, Size)
        return self.value > other.value

    # }}}
    def __ge__(self, other):  # operator >=  # {{{
        assert isinstance(other, Size)
        return self.value >= other.value

    # }}}

    @classmethod  # fromStr#{{{
    def fromStr(cls, string_size: str):
        sizes = {
            "BLACKSWAN_SMALL": Size.BLACKSWAN_SMALL,
            "ANOMAL_SMALL": Size.ANOMAL_SMALL,
            "EXTRA_SMALL": Size.EXTRA_SMALL,
            "VERY_SMALL": Size.VERY_SMALL,
            "SMALLEST": Size.SMALLEST,
            "SMALLER": Size.SMALLER,
            "SMALL": Size.SMALL,
            "NORMAL": Size.NORMAL,
            "BIG": Size.BIG,
            "BIGGER": Size.BIGGER,
            "BIGGEST": Size.BIGGEST,
            "VERY_BIG": Size.VERY_BIG,
            "EXTRA_BIG": Size.EXTRA_BIG,
            "ANOMAL_BIG": Size.ANOMAL_BIG,
            "BLACKSWAN_BIG": Size.BLACKSWAN_BIG,
        }
        return sizes[string_size]

    # }}}


class SimpleSize(enum.Enum):
    SMALLEST = -3
    SMALL = -1
    NORMAL = 0
    BIG = 1
    BIGGEST = 3

    def __eq__(self, other):  # operator ==  # {{{
        if isinstance(other, SimpleSize):
            return self.value == other.value

        assert isinstance(other, Size)
        match self:
            case SimpleSize.SMALLEST:
                eq = (
                    Size.BLACKSWAN_SMALL.value,
                    Size.ANOMAL_SMALL.value,
                    Size.EXTRA_SMALL.value,
                    Size.VERY_SMALL.value,
                    Size.SMALLEST.value,
                )
            case SimpleSize.SMALL:
                eq = (
                    Size.SMALLER.value,
                    Size.SMALL.value,
                )
            case SimpleSize.NORMAL:
                eq = (Size.NORMAL.value,)
            case SimpleSize.BIG:
                eq = (
                    Size.BIG.value,
                    Size.BIGGER.value,
                )
            case SimpleSize.BIGGEST:
                eq = (
                    Size.BIGGEST.value,
                    Size.VERY_BIG.value,
                    Size.EXTRA_BIG.value,
                    Size.ANOMAL_BIG.value,
                    Size.BLACKSWAN_BIG.value,
                )

        return other.value in eq

    # }}}
    def __hash__(self):  # {{{
        return hash(self.value)

    # }}}


if __name__ == "__main__":
    ...
