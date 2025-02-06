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
    BLACKSWAN_SMALL = 0
    GREATEST_SMALL = 1
    ANOMAL_SMALL = 3
    EXTRA_SMALL = 5
    VERY_SMALL = 10
    SMALLEST = 20
    SMALLER = 30
    SMALL = 40
    NORMAL = 60
    BIG = 70
    BIGGER = 80
    BIGGEST = 90
    VERY_BIG = 95
    EXTRA_BIG = 97
    ANOMAL_BIG = 99
    GREATEST_BIG = 100
    BLACKSWAN_BIG = 100500

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

    def toSimpleSize(self) -> SimpleSize:  # {{{
        for ssize in SimpleSize:
            if self == ssize:
                return ssize

    # }}}

    @classmethod  # fromStr#{{{
    def fromStr(cls, string_size: str):
        sizes = {
            "BLACKSWAN_SMALL": Size.BLACKSWAN_SMALL,
            "GREATEST_SMALL": Size.GREATEST_SMALL,
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
            "GREATEST_BIG": Size.GREATEST_BIG,
            "BLACKSWAN_BIG": Size.BLACKSWAN_BIG,
        }
        return sizes[string_size]

    # }}}


class SimpleSize(enum.Enum):
    XXS = 0
    XS = 20
    S = 40
    M = 60
    L = 80
    XL = 100
    XXL = 100500

    def __eq__(self, other):  # operator ==  # {{{
        if isinstance(other, SimpleSize):
            return self.value == other.value

        assert isinstance(other, Size)
        match self:
            case SimpleSize.XXS:
                eq = (Size.BLACKSWAN_SMALL.value,)
            case SimpleSize.XS:
                eq = (
                    Size.GREATEST_SMALL.value,
                    Size.ANOMAL_SMALL.value,
                    Size.EXTRA_SMALL.value,
                    Size.VERY_SMALL.value,
                )
            case SimpleSize.S:
                eq = (
                    Size.SMALLEST.value,
                    Size.SMALLER.value,
                )
            case SimpleSize.M:
                eq = (
                    Size.SMALL.value,
                    Size.NORMAL.value,
                    Size.BIG.value,
                )
            case SimpleSize.L:
                eq = (
                    Size.BIGGER.value,
                    Size.BIGGEST.value,
                )
            case SimpleSize.XL:
                eq = (
                    Size.VERY_BIG.value,
                    Size.EXTRA_BIG.value,
                    Size.ANOMAL_BIG.value,
                    Size.GREATEST_BIG.value,
                )
            case SimpleSize.XXL:
                eq = (Size.BLACKSWAN_BIG.value,)

        return other.value in eq

    # }}}
    def __hash__(self):  # {{{
        return hash(self.value)

    # }}}


if __name__ == "__main__":
    ...
