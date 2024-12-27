#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

"""Doc"""

from __future__ import annotations

import enum
from datetime import datetime
from typing import Optional, TypeVar

from avin.core.range import Range
from avin.data._bar import _Bar

Chart = TypeVar("Chart")


class Bar(_Bar):
    class Type(enum.Flag):  # {{{
        UNDEFINE = 0
        BEAR = 1
        BULL = 2
        INSIDE = 4
        OVERFLOW = 8
        OUTSIDE = 16
        EXTREMUM = 32

    # }}}
    def __init__(  # {{{
        self,
        dt: datetime,
        open: float,
        high: float,
        low: float,
        close: float,
        vol: int,
        chart: Optional[Chart] = None,
    ):
        _Bar.__init__(self, dt, open, high, low, close, vol)
        self.__chart = chart
        self.__analyse()

    # }}}
    def __contains__(self, price: float) -> bool:  # {{{
        return self.low <= price <= self.high

    # }}}
    @property  # full  # {{{
    def full(self) -> Range:
        return Range(self.low, self.high, Range.Type.FULL, self)

    # }}}
    @property  # body  # {{{
    def body(self) -> Range:
        if self.open < self.close:
            return Range(self.open, self.close, Range.Type.BODY, self)
        else:
            return Range(self.close, self.open, Range.Type.BODY, self)

    # }}}
    @property  # lower  # {{{
    def lower(self) -> Range:
        # вот тут бы как нибудь мин прайс степ бы учесть..
        # а то значения open close - попадают и в тело и в тени.
        if self.isBull():
            return Range(self.low, self.open, Range.Type.LOWER, self)
        else:
            return Range(self.low, self.close, Range.Type.LOWER, self)

    # }}}
    @property  # upper  # {{{
    def upper(self) -> Range:
        if self.isBull():
            return Range(self.close, self.high, Range.Type.UPPER, self)
        else:
            return Range(self.open, self.high, Range.Type.UPPER, self)

    # }}}
    @property  # chart  # {{{
    def chart(self):
        return self.__chart

    # }}}
    def setChart(self, chart) -> None:  # {{{
        self.__chart = chart

    # }}}
    def addFlag(self, flag: Bar.Type) -> None:  # {{{
        assert isinstance(flag, Bar.Type)
        self.__flags |= flag

    # }}}
    def delFlag(self, flag: Bar.Type) -> None:  # {{{
        assert isinstance(flag, Bar.Type)
        self.__flags &= ~flag

    # }}}
    def isBull(self) -> bool:  # {{{
        return self.__flags & Bar.Type.BULL == Bar.Type.BULL

    # }}}
    def isBear(self) -> bool:  # {{{
        return self.__flags & Bar.Type.BEAR == Bar.Type.BEAR

    # }}}
    def isInside(self) -> bool:  # {{{
        return self.__flags & Bar.Type.INSIDE == Bar.Type.INSIDE

    # }}}
    def isOverflow(self) -> bool:  # {{{
        return self.__flags & Bar.Type.OVERFLOW == Bar.Type.OVERFLOW

    # }}}
    def isOutside(self) -> bool:  # {{{
        return self.__flags & Bar.Type.OUTSIDE == Bar.Type.OUTSIDE

    # }}}
    def isExtremum(self) -> bool:  # {{{
        return self.__flags & Bar.Type.EXTREMUM == Bar.Type.EXTREMUM

    # }}}
    @classmethod  # fromRecord# {{{
    def fromRecord(
        cls, record: asyncpg.Record, chart: Optional[Chart] = None
    ):
        bar = cls(
            record["dt"],
            record["open"],
            record["high"],
            record["low"],
            record["close"],
            record["volume"],
            chart,
        )
        return bar

    # }}}
    def __analyse(self):  # {{{
        if self.close - self.open > 0.0:
            self.__flags = Bar.Type.BULL
        elif self.close - self.open < 0.0:
            self.__flags = Bar.Type.BEAR
        else:
            self.__flags = Bar.Type.UNDEFINE

    # }}}


if __name__ == "__main__":
    ...
