#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

from __future__ import annotations


class Analytic:
    def highestHigh(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.highestHigh()")

        # using method getBars() instead of self.__bars
        # because its return only [0, head] bars
        bars = self.getBars()

        bar = max(bars, key=lambda x: x.high)
        return bar.high

    # }}}
    def lowestLow(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.lowestLow()")

        # using method getBars() instead of self.__bars
        # because its return only [0, head] bars
        bars = self.getBars()
        bar = min(bars, key=lambda x: x.low)
        return bar.low

    # }}}


class Extremum:  # {{{
    class Type(enum.Flag):  # {{{
        UNDEFINE = 0b00000000_00000000
        MIN = 0b00000000_00000010
        MAX = 0b00000000_00000100
        SHORTTERM = 0b00000000_00001000
        MIDTERM = 0b00000000_00011000
        LONGTERM = 0b00000000_00111000

    # }}}
    def __init__(self, TYPE, parent: Bar):  # {{{
        self.__parent = parent
        self.__parent.addFlag(Bar.Type.EXTREMUM)
        self.__flags = TYPE
        if TYPE & Extremum.Type.MAX:
            self.__price = parent.high
        elif TYPE & Extremum.Type.MIN:
            self.__price = parent.low

    # }}}
    def __str__(self):  # {{{
        s = f"{self.__parent.dt} {self.price}"
        s += " MAX" if self.isMax() else " MIN"
        s += " MIDTERM" if self.isMidterm() else ""
        s += " LONGTERM" if self.isLongterm() else ""
        return s

    # }}}
    def __lt__(self, other):  # operator <{{{
        assert isinstance(other, Extremum)
        return self.__price < other.__price

    # }}}
    def __le__(self, other):  # operator <={{{
        assert isinstance(other, Extremum)
        return self.__price <= other.__price

    # }}}
    def __gt__(self, other):  # operator >{{{
        assert isinstance(other, Extremum)
        return self.__price > other.__price

    # }}}
    def __ge__(self, other):  # operator >={{{
        assert isinstance(other, Extremum)
        return self.__price >= other.__price

    # }}}
    def __eq__(self, other):  # operator =={{{
        assert isinstance(other, Extremum)
        return self.__price == other.__price

    # }}}
    def __sub__(self, other):  # operator -{{{
        assert isinstance(other, Extremum)
        return self.__price - other.__price

    # }}}
    @property  # dt# {{{
    def dt(self):
        return self.__parent.dt

    # }}}
    @property  # price# {{{
    def price(self):
        return self.__price

    # }}}
    def parent(self) -> Bar:  # {{{
        return self.__parent

    # }}}
    def addFlag(self, flag):  # {{{
        assert isinstance(flag, Extremum.Type)
        self.__flags |= flag

    # }}}
    def isMin(self) -> bool:  # {{{
        return self.__flags & Extremum.Type.MIN == Extremum.Type.MIN

    # }}}
    def isMax(self) -> bool:  # {{{
        return self.__flags & Extremum.Type.MAX == Extremum.Type.MAX

    # }}}
    def isShortterm(self) -> bool:  # {{{
        r = self.__flags & Extremum.Type.SHORTTERM == Extremum.Type.SHORTTERM
        return r

    # }}}
    def isMidterm(self) -> bool:  # {{{
        return self.__flags & Extremum.Type.MIDTERM == Extremum.Type.MIDTERM

    # }}}
    def isLongterm(self) -> bool:  # {{{
        return self.__flags & Extremum.Type.LONGTERM == Extremum.Type.LONGTERM

    # }}}


# }}}
class ExtremumList:  # {{{
    """Const"""  # {{{

    name = "Extremum"

    # }}}
    def __init__(self, chart: Chart):  # {{{
        self.__parent = chart
        self.__shortterm = list()
        self.__midterm = list()
        self.__longterm = list()
        self.update()

    # }}}
    def __isOverflowOf(self, this, of) -> bool:  # {{{
        if this.high > of or this.low < of.low:
            return True
        else:
            return False

    # }}}
    def __isInsideOf(self, this, of) -> bool:  # {{{
        if this.high <= of.high and this.low >= of.low:
            return True
        else:
            return False

    # }}}
    def __isOutsideOf(self, this, of) -> bool:  # {{{
        if this.high >= of.high and this.low <= of.low:
            return True
        else:
            return False

    # }}}
    def __markInsideDays(self):  # {{{
        bars = self.__parent.getBars()
        i = 0
        previous = bars[i]
        previous.removeFlag(Bar.Type.INSIDE)
        i += 1
        while i < len(bars):
            current_bar = bars[i]
            if self.__isInsideOf(current_bar, previous):
                current_bar.addFlag(Bar.Type.INSIDE)
            else:
                current_bar.removeFlag(Bar.Type.INSIDE)
                previous = current_bar
            i += 1

    # }}}
    def __markOutsideDays(self):  # {{{
        bars = self.__parent.getBars()
        i = 0
        previous = bars[i]
        previous.removeFlag(Bar.Type.OUTSIDE)
        i += 1
        while i < len(bars):
            current_bar = bars[i]
            if self.__isOutsideOf(current_bar, previous):
                current_bar.addFlag(Bar.Type.OUTSIDE)
            else:
                current_bar.removeFlag(Bar.Type.OUTSIDE)
                previous = current_bar
            i += 1

    # }}}
    def __markOverflowDays(self):  # {{{
        bars = self.__parent.getBars()
        for bar in bars:
            if not bar.isInside() and not bar.isOutside():
                bar.addFlag(Bar.Type.OVERFLOW)

    # }}}
    def __skipInsideOutside(self):  # {{{
        without_inside_outside = list()
        bars = self.__parent.getBars()
        for bar in bars:
            if bar.isInside() or bar.isOutside():
                continue
            else:
                without_inside_outside.append(bar)
        return without_inside_outside

    # }}}
    def __popRepeatedExtr(self, elist):  # {{{
        if len(elist) < 2:
            return
        i = 0
        previous = elist[i]
        i += 1
        while i < len(elist):
            current = elist[i]
            if current.isMax() and previous.isMax():
                if current > previous:
                    elist.remove(previous)
                    previous = current
                    continue
                else:
                    elist.remove(current)
                    continue
            elif current.isMin() and previous.isMin():
                if current < previous:
                    elist.remove(previous)
                    previous = current
                    continue
                else:
                    elist.remove(current)
                    continue
            previous = current
            i += 1

    # }}}
    def __updateShorttem(self):  # {{{
        self.__shortterm.clear()
        bars = self.__skipInsideOutside()
        if len(bars) < 3:
            return
        i = 1
        count = len(bars) - 1
        while i < count:
            left = bars[i - 1]
            bar = bars[i]
            right = bars[i + 1]
            if left.high < bar.high > right.high:
                e = Extremum(Extremum.Type.MAX | Extremum.Type.SHORTTERM, bar)
                self.__shortterm.append(e)
            if left.low > bar.low < right.low:
                e = Extremum(Extremum.Type.MIN | Extremum.Type.SHORTTERM, bar)
                self.__shortterm.append(e)
            i += 1
        self.__popRepeatedExtr(self.__shortterm)

    # }}}
    def __updateMidterm(self):  # {{{
        self.__midterm.clear()
        short_extr = self.__shortterm
        if len(short_extr) < 5:
            return
        i = 2
        count = len(short_extr) - 2
        while i < count:
            left = short_extr[i - 2]
            e = short_extr[i]
            right = short_extr[i + 2]
            if (
                e.isMax()
                and left < e > right
                or e.isMin()
                and left > e < right
            ):
                e.addFlag(Extremum.Type.MIDTERM)
                self.__midterm.append(e)
            i += 1
        self.__popRepeatedExtr(self.__midterm)

    # }}}
    def __updateLongterm(self):  # {{{
        self.__longterm.clear()
        mid_extr = self.__midterm
        if len(mid_extr) < 5:
            return
        i = 2
        count = len(mid_extr) - 2
        while i < count:
            left = mid_extr[i - 2]
            e = mid_extr[i]
            right = mid_extr[i + 2]
            if (
                e.isMax()
                and (left < e > right)
                or e.isMin()
                and (left > e < right)
            ):
                e.addFlag(Extremum.Type.LONGTERM)
                self.__longterm.append(e)
            i += 1
        self.__popRepeatedExtr(self.__longterm)

    # }}}
    @property  # sterm{{{
    def sterm(self):
        return self.__shortterm

    # }}}
    @property  # mterm{{{
    def mterm(self):
        return self.__midterm

    # }}}
    @property  # lterm{{{
    def lterm(self):
        return self.__longterm

    # }}}
    def parent(self) -> Chart:  # {{{
        return self.__parent

    # }}}
    def update(self) -> None:  # {{{
        self.__markInsideDays()
        self.__markOutsideDays()
        self.__markOverflowDays()
        self.__updateShorttem()
        self.__updateMidterm()
        self.__updateLongterm()

    # }}}
    # def midDelta(self) -> float:{{{
    #     extr = self.__midterm
    #     if len(extr) >= 3:
    #         return extr[-1] - extr[-3]
    #     else:
    #         return None
    #
    # def midSpeed(self) -> bool:
    #     delta = self.midDelta()
    #     if delta is not None:
    #         percent = delta / self.__midterm[-1]
    #         tf = self.__parent.timeframe
    #         prev = self.__midterm[-3].dt
    #         cur = self.__midterm[-1].dt
    #         # TODO: через выходные перенос тогда будет искажено значение
    #         # надо наверное все таки пронумеровать бары
    #         bars_count = (cur - prev) / tf
    #         speed = percent / bars_count
    #         return speed
    #     else:
    #         return None
    #
    # def isMidTrendBull(self) -> bool:
    #     extr = self.__midterm
    #     if (len(extr) >= 4
    #         # Прошлый экстремум больше позапрошлого (бычий тренд)
    #         and extr[-1] > extr[-3]
    #         # Разница экстремумов больше __ %
    #         and abs(extr[-1] - extr[-3]) / chart.last.close * 100 > 3
    #         # Добавим что минимумы и максимумы идут по восходящей
    #         and extr[-2] > extr[-4]
    #         # Разница экстремумов больше __ %
    #         and abs(extr[-2] - extr[-4]) / chart.last.close * 100 > 3
    #         ):
    #         return True
    #     else:
    #         return False
    #
    # def isMidTrendBear(self) -> bool:
    #     extr = self.__midterm
    #     if (len(extr) >= 4
    #         # Прошлый экстремум меньше позапрошлого (медвежий тренд)
    #         and extr[-1] < extr[-3]
    #         # Разница экстремумов больше __ %
    #         and abs(extr[-1] - extr[-3]) / chart.last.close * 100 > 3
    #         # Добавим что и минимумы и максимумы идут по нисходящей
    #         and extr[-2] < extr[-4]
    #         # Разница экстремумов больше __ %
    #         and abs(extr[-2] - extr[-4]) / chart.last.close * 100 > 3
    #         ):
    #         return True
    #     else:
    #         return False
    #
    # }}}


# }}}
class Indicator:  # {{{
    @staticmethod  # BEAR_LEN# {{{
    def BEAR_LEN(chart):
        assert chart.last is not None
        i = -1
        while chart[i] is not None and chart[i].isBear():
            i -= 1
        return abs(i + 1)

    # }}}
    @staticmethod  # BULL_LEN# {{{
    def BULL_LEN(chart):
        assert chart.last is not None
        i = -1
        while chart[i] is not None and chart[i].isBull():
            i -= 1
        return abs(i + 1)

    # }}}
    @staticmethod  # SPEED# {{{
    def SPEED(chart, period):
        assert chart.last is not None
        if chart[-1] is None or chart[-period - 1] is None:
            return None
        first = chart[-period - 1].body.mid()
        last = chart[-1].body.mid()
        delta = last - first
        percent = delta / first * 100
        speed = percent / period
        return speed

    # }}}
    @staticmethod  # MA# {{{
    def MA(chart, period, parameter="close"):
        assert chart.last is not None
        total = 0
        for i in range(-1, -period - 1, -1):
            if chart[i] == None:
                return None
            total += chart[i].close
        return total / period

    # }}}


# }}}


if __name__ == "__main__":
    ...
