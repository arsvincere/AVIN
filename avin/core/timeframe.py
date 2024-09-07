#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

from __future__ import annotations

from datetime import timedelta

from avin.data import DataType


class TimeFrame:  # {{{
    """doc# {{{
    Реализует таймфрейм.

    Обертка datetime.timedelta
    """

    # }}}
    ALL = []  # initializated below class

    def __init__(self, string):  # {{{
        period = {
            "1M": timedelta(minutes=1),
            "5M": timedelta(minutes=5),
            "10M": timedelta(minutes=10),
            "1H": timedelta(hours=1),
            "D": timedelta(days=1),
            "W": timedelta(weeks=1),
            "M": timedelta(days=30),
        }
        self.__period = period[string]

    # }}}
    def __str__(self):  # {{{
        periods = {
            timedelta(minutes=1): "1M",
            timedelta(minutes=5): "5M",
            timedelta(minutes=10): "10M",
            timedelta(hours=1): "1H",
            timedelta(days=1): "D",
            timedelta(weeks=1): "W",
            timedelta(days=30): "M",
        }
        return periods[self.__period]

    # }}}
    def __repr__(self):  # {{{
        periods = {
            timedelta(minutes=1): "1M",
            timedelta(minutes=5): "5M",
            timedelta(minutes=10): "10M",
            timedelta(hours=1): "1H",
            timedelta(days=1): "D",
            timedelta(weeks=1): "W",
            timedelta(days=30): "M",
        }
        s = periods[self.__period]
        return f"TimeFrame('{s}')"

    # }}}
    def __hash__(self):  # {{{
        return hash(str(self))

    # }}}
    def __eq__(self, other):  # operator ==  # {{{
        if isinstance(other, TimeFrame):
            return self.__period == other.__period
        elif isinstance(other, timedelta):
            return self.__period == other
        elif isinstance(other, str):
            other = TimeFrame(other)
            return self.__period == other.__period
        else:
            raise TimeFrameError(
                f"Недопустимое сравнение <TimeFrame> и {type(other)}"
            )

    # }}}
    def __lt__(self, other):  # operator <  # {{{
        if isinstance(other, TimeFrame):
            return self.__period < other.__period
        elif isinstance(other, timedelta):
            return self.__period < other
        elif isinstance(other, str):
            other = TimeFrame(other)
            return self.__period < other.__period
        else:
            raise TimeFrameError(
                f"Недопустимое сравнение <TimeFrame> и {type(other)}"
            )

    # }}}
    def __le__(self, other):  # operator <=  # {{{
        if isinstance(other, TimeFrame):
            return self.__period <= other.__period
        elif isinstance(other, timedelta):
            return self.__period <= other
        elif isinstance(other, str):
            other = TimeFrame(other)
            return self.__period <= other.__period
        else:
            raise TimeFrameError(
                f"Недопустимое сравнение <TimeFrame> и {type(other)}"
            )

    # }}}
    def __gt__(self, other):  # operator >  # {{{
        if isinstance(other, TimeFrame):
            return self.__period > other.__period
        elif isinstance(other, timedelta):
            return self.__period > other
        elif isinstance(other, str):
            other = TimeFrame(other)
            return self.__period > other.__period
        else:
            raise TimeFrameError(
                f"Недопустимое сравнение <TimeFrame> и {type(other)}"
            )

    # }}}
    def __ge__(self, other):  # operator >=  # {{{
        if isinstance(other, TimeFrame):
            return self.__period >= other.__period
        elif isinstance(other, timedelta):
            return self.__period >= other
        elif isinstance(other, str):
            other = TimeFrame(other)
            return self.__period >= other.__period
        else:
            raise TimeFrameError(
                f"Недопустимое сравнение <TimeFrame> и {type(other)}"
            )

    # }}}
    def __add__(self, other):  # operator +  # {{{
        if isinstance(other, timedelta):
            return other + self.__period
        if isinstance(other, datetime):
            return other + self.__period
        else:
            raise TimeFrameError(
                f"Недопустимое сложение <TimeFrame> и {type(other)}"
            )

    # }}}
    def __radd__(self, other):  # operator + #  {{{
        if isinstance(other, timedelta):
            return other + self.__period
        if isinstance(other, datetime):
            return other + self.__period
        else:
            raise TimeFrameError(
                f"Недопустимое сложение <TimeFrame> и {type(other)}"
            )

    # }}}
    def __mul__(self, other):  # operator *{{{
        if isinstance(other, int):
            return self.__period * other
        else:
            raise TimeFrameError(
                f"Недопустимое умножение <TimeFrame> и {type(other)}"
            )

    # }}}
    def __rmul__(self, other):  # operator *{{{
        if isinstance(other, int):
            return self.__period * other
        else:
            raise TimeFrameError(
                f"Недопустимое умножение <TimeFrame> и {type(other)}"
            )

    # }}}
    def minutes(self):  # {{{
        return int(self.__period.total_seconds() / 60)

    # }}}
    def toDataType(self):  # {{{
        periods = {
            timedelta(minutes=1): DataType.BAR_1M,
            timedelta(minutes=5): DataType.BAR_5M,
            timedelta(minutes=10): DataType.BAR_10M,
            timedelta(hours=1): DataType.BAR_1H,
            timedelta(days=1): DataType.BAR_D,
            timedelta(weeks=1): DataType.BAR_W,
            timedelta(days=30): DataType.BAR_M,
        }
        return periods[self.__period]

    # }}}
    def toTimeDelta(self):  # {{{
        return self.__period

    # }}}


# }}}

TimeFrame.ALL = [
    TimeFrame("1M"),
    TimeFrame("5M"),
    TimeFrame("10M"),
    TimeFrame("1H"),
    TimeFrame("D"),
    TimeFrame("W"),
    TimeFrame("M"),
]
