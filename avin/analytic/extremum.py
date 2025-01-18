#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

from __future__ import annotations

import enum

from avin.config import Usr
from avin.core import Bar, Chart
from avin.utils import logger


class Extremum:  # {{{
    class Type(enum.Flag):  # {{{
        UNDEFINE = 0b00000000
        MIN = 0b00000010
        MAX = 0b00000100
        SHORTTERM = 0b00001000
        MIDTERM = 0b00011000
        LONGTERM = 0b00111000

    # }}}
    def __init__(self, TYPE, bar: Bar):  # {{{
        self.__bar = bar  # сохраняем исходный бар
        self.__bar.addFlag(Bar.Type.EXTREMUM)  # вешаем бару флаг экстремум
        self.__flags = TYPE  # сохраняем флаги определяющие тип

        # определяем и сохраняем цену в зависимости от типа (MIN/MAX)
        if self.__flags & Extremum.Type.MAX:
            self.__price = bar.high
        elif self.__flags & Extremum.Type.MIN:
            self.__price = bar.low

    # }}}
    def __str__(self):  # {{{
        dt = Usr.localTime(self.__bar.dt)
        ticker = self.__bar.chart.instrument.ticker
        s = f"{ticker} {dt} {self.price}"
        s += " MAX" if self.isMax() else " MIN"
        s += " MIDTERM" if self.isMidterm() else ""
        s += " LONGTERM" if self.isLongterm() else ""
        return s

    # }}}
    def __lt__(self, other):  # operator <  # {{{
        assert isinstance(other, Extremum)

        # TODO: а с float ведь тоже можно делать сравнения...

        return self.__price < other.__price

    # }}}
    def __le__(self, other):  # operator <=  # {{{
        assert isinstance(other, Extremum)
        return self.__price <= other.__price

    # }}}
    def __gt__(self, other):  # operator >  # {{{
        assert isinstance(other, Extremum)
        return self.__price > other.__price

    # }}}
    def __ge__(self, other):  # operator >=  # {{{
        assert isinstance(other, Extremum)
        return self.__price >= other.__price

    # }}}
    def __eq__(self, other):  # operator ==  # {{{
        assert isinstance(other, Extremum)
        return self.__price == other.__price

    # }}}
    def __sub__(self, other):  # operator -  # {{{
        assert isinstance(other, Extremum)
        return self.__price - other.__price

    # }}}

    @property  # dt  # {{{
    def dt(self):
        return self.__bar.dt

    # }}}
    @property  # price  # {{{
    def price(self):
        return self.__price

    # }}}
    @property  # bar   # {{{
    def bar(self) -> Bar:
        return self.__bar

    # }}}
    @property  # type  # {{{
    def type(self):
        if self.isLongterm():
            return Extremum.Type.LONGTERM
        elif self.isMidterm():
            return Extremum.Type.MIDTERM
        elif self.isShortterm():
            return Extremum.Type.SHORTTERM
        else:
            assert False, "WTF???"

    # }}}

    def addFlag(self, flag: Extremum.Type) -> None:  # {{{
        assert isinstance(flag, Extremum.Type)
        self.__flags |= flag

    # }}}
    def delFlag(self, flag: Extremum.Type) -> None:  # {{{
        assert isinstance(flag, Extremum.Type)
        self.__flags &= ~flag

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
    def __init__(self, chart: Chart):  # {{{
        self.__chart = chart
        self.__shortterm = list()
        self.__midterm = list()
        self.__longterm = list()
        self.update()

    # }}}

    @property  # sterm  # {{{
    def sterm(self):
        return self.__shortterm

    # }}}
    @property  # mterm  # {{{
    def mterm(self):
        return self.__midterm

    # }}}
    @property  # lterm  # {{{
    def lterm(self):
        return self.__longterm

    # }}}
    @property  # chart  # {{{
    def chart(self) -> Chart:
        return self.__chart

    # }}}

    def sMax(self):  # {{{
        max_of_sterm = -1
        for extr in self.__shortterm:
            if extr.isMax():
                max_of_sterm = max(extr.price, max_of_sterm)

        if max_of_sterm == -1:
            return None

        return max_of_sterm

    # }}}

    def sTrend(self, n=0) -> Trend | None:  # {{{
        """
        Тренд 0 - это текущий незавершенный тренд
        Тренд 1 - это прошлый тренд
        Тренд 2 - это позапрошлый тренд и тд
        """
        assert n >= 0

        if n > (len(self.__shortterm) - 1):
            return None

        t = Extremum.Type
        if n == 0:
            e1 = self.__shortterm[-1]

            # TODO: тут нужно не просто last_bar брать как сейчас
            # а смотреть на самое экстримальное значение среди баров
            # от прошлого экстремума до последнего исторического бара
            # self.__chart.getBars(e1.bar, self.__chart.last)
            last_bar = self.__chart.last

            if e1.isMax():
                e2 = Extremum(t.MIN | t.SHORTTERM, last_bar)
            else:
                e2 = Extremum(t.MAX | t.SHORTTERM, last_bar)

            trend = Trend(e1, e2, Term.SHORTTERM)
            return trend

        # n >= 1
        e1 = self.__shortterm[-n - 1]
        e2 = self.__shortterm[-n]
        trend = Trend(e1, e2, Term.SHORTTERM)
        return trend

    # }}}
    def mTrend(self, n=0) -> Trend | None:  # {{{
        assert n >= 0

        if n > (len(self.__midterm) - 1):
            return None

        t = Extremum.Type
        if n == 0:
            e1 = self.__midterm[-1]

            last_bar = self.__chart.last
            if e1.isMax():
                e2 = Extremum(t.MIN | t.SHORTTERM, last_bar)
            else:
                e2 = Extremum(t.MAX | t.SHORTTERM, last_bar)

            trend = Trend(e1, e2, Term.MIDTERM)
            return trend

        # n >= 1
        e1 = self.__midterm[-n - 1]
        e2 = self.__midterm[-n]
        trend = Trend(e1, e2, Term.MIDTERM)
        return trend

    # }}}
    def lTrend(self, n=0) -> Trend | None:  # {{{
        assert n >= 0

        if n > (len(self.__longterm) - 1):
            return None

        t = Extremum.Type
        if n == 0:
            e1 = self.__longterm[-1]

            last_bar = self.__chart.last
            if e1.isMax():
                e2 = Extremum(t.MIN | t.SHORTTERM, last_bar)
            else:
                e2 = Extremum(t.MAX | t.SHORTTERM, last_bar)

            trend = Trend(e1, e2, Term.LONGTERM)
            return trend

        # n >= 1
        e1 = self.__longterm[-n - 1]
        e2 = self.__longterm[-n]
        trend = Trend(e1, e2, Term.LONGTERM)
        return trend

    # }}}
    def getAllSTrends(self) -> list[Trend]:  # {{{
        all_trends = list()

        n = 0
        trend = self.sTrend(n)
        while trend is not None:
            all_trends.append(trend)
            n += 1
            trend = self.sTrend(n)

        return all_trends

    # }}}
    def getAllMTrends(self) -> list[Trend]:  # {{{
        all_trends = list()

        n = 0
        trend = self.mTrend(n)
        while trend is not None:
            all_trends.append(trend)
            n += 1
            trend = self.mTrend(n)

        return all_trends

    # }}}
    def getAllLTrends(self) -> list[Trend]:  # {{{
        all_trends = list()

        n = 0
        trend = self.lTrend(n)
        while trend is not None:
            all_trends.append(trend)
            n += 1
            trend = self.lTrend(n)

        return all_trends

    # }}}

    def sVawe(self, n=0) -> Vawe | None:  # {{{
        assert n >= 0

        """
        Волна 0 состоит из тренда 1 и тренда 0
        Волна 1 состоит из тренда 2 и тренда 1
        Волна 2 состоит из тренда 3 и тренда 2
        """

        t1 = self.sTrend(n + 1)
        t2 = self.sTrend(n)
        if t1 is None:
            return None

        return Vawe(t1, t2)

    # }}}
    def mVawe(self, n=0) -> Vawe | None:  # {{{
        assert n >= 0

        """
        Волна 0 состоит из тренда 1 и тренда 0
        Волна 1 состоит из тренда 2 и тренда 1
        Волна 2 состоит из тренда 3 и тренда 2
        """

        t1 = self.mTrend(n + 1)
        t2 = self.mTrend(n)
        if t1 is None:
            return None

        return Vawe(t1, t2)

    # }}}
    def lVawe(self, n=0) -> Vawe | None:  # {{{
        assert n >= 0

        """
        Волна 0 состоит из тренда 1 и тренда 0
        Волна 1 состоит из тренда 2 и тренда 1
        Волна 2 состоит из тренда 3 и тренда 2
        """

        t1 = self.lTrend(n + 1)
        t2 = self.lTrend(n)
        if t1 is None:
            return None

        return Vawe(t1, t2)

    # }}}
    def getAllSVawes(self) -> list[Vawe]:  # {{{
        all_vawes = list()

        n = 0
        vawe = self.sVawe(n)
        while vawe is not None:
            all_vawes.append(vawe)
            n += 1
            vawe = self.sVawe(n)

        return all_vawes

    # }}}
    def getAllMVawes(self) -> list[Vawe]:  # {{{
        all_vawes = list()

        n = 0
        vawe = self.mVawe(n)
        while vawe is not None:
            all_vawes.append(vawe)
            n += 1
            vawe = self.mVawe(n)

        return all_vawes

    # }}}
    def getAllLVawes(self) -> list[Vawe]:  # {{{
        all_vawes = list()

        n = 0
        vawe = self.lVawe(n)
        while vawe is not None:
            all_vawes.append(vawe)
            n += 1
            vawe = self.lVawe(n)

        return all_vawes

    # }}}

    def sSupport(self, n=0) -> Level: ...
    def mSupport(self, n=0) -> Level: ...
    def lSupport(self, n=0) -> Level: ...

    def sResist(self, n=0) -> Level: ...
    def mResist(self, n=0) -> Level: ...
    def lResist(self, n=0) -> Level: ...

    def update(self) -> None:  # {{{
        self.__markInsideDays()
        self.__markOutsideDays()
        self.__markOverflowDays()
        self.__updateShorttem()
        self.__updateMidterm()
        self.__updateLongterm()

    # }}}

    @classmethod  # period  # {{{
    def period(cls, e1: Extremum, e2: Extremum) -> int:
        # assert e1.dt < e2.dt

        chart = e1.bar.chart
        index1 = chart.getIndex(e1.bar)
        index2 = chart.getIndex(e2.bar)
        period = index2 - index1

        if period == 0:
            return 1

        return period

    # }}}
    @classmethod  # deltaPrice  # {{{
    def deltaPrice(cls, e1: Extremum, e2: Extremum) -> float:
        # assert e1.dt < e2.dt

        delta = e2.price - e1.price

        return delta

    # }}}
    @classmethod  # deltaPercent  # {{{
    def deltaPercent(cls, e1: Extremum, e2: Extremum) -> float:
        # assert e1.dt < e2.dt

        delta = e2.price - e1.price
        percent = delta / e1.price * 100

        return round(percent, 2)

    # }}}
    @classmethod  # speedPrice  # {{{
    def speedPrice(cls, e1: Extremum, e2: Extremum) -> float:
        # assert e1.dt < e2.dt

        delta = e2.price - e1.price
        period = cls.period(e1, e2)
        speed = delta / period

        return round(speed, 2)

    # }}}
    @classmethod  # speedPercent  # {{{
    def speedPercent(cls, e1: Extremum, e2: Extremum) -> float:
        # assert e1.dt < e2.dt

        delta = e2.price - e1.price
        percent = delta / e1.price * 100
        period = cls.period(e1, e2)
        speed = percent / period

        return round(speed, 2)

    # }}}
    @classmethod  # volume  # {{{
    def volume(cls, e1: Extremum, e2: Extremum) -> int:
        # assert e1.dt < e2.dt

        chart = e1.bar.chart
        bars = chart.getBars(begin=e1.bar, end=e2.bar)

        # не учитываем объем первого экстремума, только объем баров движения
        # от первого экстремума до второго
        bars.pop(0)

        all_volume = 0
        for bar in bars:
            all_volume += bar.vol

        return all_volume

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
        bars = self.__chart.getBars()
        i = 0
        previous = bars[i]
        previous.delFlag(Bar.Type.INSIDE)
        i += 1

        while i < len(bars):
            current_bar = bars[i]
            if self.__isInsideOf(current_bar, previous):
                current_bar.addFlag(Bar.Type.INSIDE)
            else:
                current_bar.delFlag(Bar.Type.INSIDE)
                previous = current_bar
            i += 1

    # }}}
    def __markOutsideDays(self):  # {{{
        bars = self.__chart.getBars()
        i = 0
        previous = bars[i]
        previous.delFlag(Bar.Type.OUTSIDE)
        i += 1

        while i < len(bars):
            current_bar = bars[i]
            if self.__isOutsideOf(current_bar, previous):
                current_bar.addFlag(Bar.Type.OUTSIDE)
            else:
                current_bar.delFlag(Bar.Type.OUTSIDE)
                previous = current_bar
            i += 1

    # }}}
    def __markOverflowDays(self):  # {{{
        bars = self.__chart.getBars()
        for bar in bars:
            if not bar.isInside() and not bar.isOutside():
                bar.addFlag(Bar.Type.OVERFLOW)

    # }}}
    def __skipInsideOutside(self):  # {{{
        # NOTE:
        # если их скипать получается гораздо больше неадеквата
        # чем если их оставить.
        # Самая жесть после СВО, там инсайд потом пол года идет.
        # Лучше пусть шорт-терм чаще колеблется, и больше смотреть
        # на m-term, l-term. Чисто визуально мне кажется это лучше
        # сейчас будет работать.
        without_inside_outside = list()
        bars = self.__chart.getBars()
        # NOTE:
        # Отключаю эту функцию временно, но не удаляю пока.
        return bars

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
                    elist.pop(i - 1)
                    previous = current
                    continue
                else:
                    elist.pop(i)
                    continue
            elif current.isMin() and previous.isMin():
                if current < previous:
                    elist.pop(i - 1)
                    previous = current
                    continue
                else:
                    elist.pop(i)
                    continue
            elif current.dt == previous.dt:
                elist.pop(i)
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


# }}}


class Term(enum.Enum):  # {{{
    SHORTTERM = 1
    MIDTERM = 2
    LONGTERM = 3


# }}}
class Trend:  # {{{
    def __init__(self, e1: Extremum, e2: Extremum, term: Term):  # {{{
        logger.debug(f"{self.__class__.__name__}.__init__({e1}, {e2})")
        # assert e1.dt < e2.dt

        self.__e1 = e1
        self.__e2 = e2
        self.__term = term

    # }}}

    @property  # begin  # {{{
    def begin(self):
        return self.__e1

    # }}}
    @property  # end  # {{{
    def end(self):
        return self.__e2

    # }}}
    @property  # asset  # {{{
    def asset(self):
        return self.__e1.bar.chart.instrument

    # }}}
    @property  # chart  # {{{
    def chart(self):
        return self.__e1.bar.chart

    # }}}
    @property  # timeframe  # {{{
    def timeframe(self):
        return self.__e1.bar.chart.timeframe

    # }}}
    @property  # term  # {{{
    def term(self):
        return self.__term

    # }}}

    def isBull(self) -> bool:  # {{{
        return self.__e2.price > self.__e1.price

    # }}}
    def isBear(self) -> bool:  # {{{
        return self.__e2.price < self.__e1.price

    # }}}
    def period(self) -> int:  # {{{
        return ExtremumList.period(self.__e1, self.__e2)

    # }}}
    def deltaPrice(self) -> float:  # {{{
        return ExtremumList.deltaPrice(self.__e1, self.__e2)

    # }}}
    def deltaPercent(self) -> float:  # {{{
        return ExtremumList.deltaPercent(self.__e1, self.__e2)

    # }}}
    def speedPrice(self) -> float:  # {{{
        return ExtremumList.speedPrice(self.__e1, self.__e2)

    # }}}
    def speedPercent(self) -> float:  # {{{
        return ExtremumList.speedPercent(self.__e1, self.__e2)

    # }}}
    def volume(self) -> int:  # {{{
        return ExtremumList.volume(self.__e1, self.__e2)

    # }}}


# }}}
class Vawe:  # {{{
    def __init__(self, t1: Trend, t2: Trend):  # {{{
        logger.debug(f"{self.__class__.__name__}.__init__({t1}, {t2})")

        self.__t1 = t1
        self.__t2 = t2

    # }}}

    @property  # one  # {{{
    def one(self):
        return self.__t1

    # }}}
    @property  # two  # {{{
    def two(self):
        return self.__t2

    # }}}
    @property  # begin  # {{{
    def begin(self):
        return self.__t1.begin

    # }}}
    @property  # center  # {{{
    def center(self):
        return self.__t1.end

    # }}}
    @property  # end  # {{{
    def end(self):
        return self.__t2.end

    # }}}
    @property  # asset  # {{{
    def asset(self):
        return self.__t1.asset

    # }}}
    @property  # chart  # {{{
    def chart(self):
        return self.__t1.chart

    # }}}
    @property  # timeframe  # {{{
    def timeframe(self):
        return self.__t1.timeframe

    # }}}
    @property  # term  # {{{
    def term(self):
        return self.__t1.term

    # }}}

    def isBull(self) -> bool:  # {{{
        """Например:
        то есть есть 3 экстремума: 100 90 110
        дельты:
        d1 = 90 - 100 = -10
        d2 = 110 - 90 = 20
        D = -10 + 20 = 10

        Или по другому через первую и последнюю точку:
        D = 110 - 100 = 10

        Очевидно что в любом случае получится одно и тоже.
        Поэтому проще будет посмотреть дельту по началу и концу
        меньше вычислений.
        """

        return self.__t2.end.price > self.__t1.begin.price

    # }}}
    def isBear(self) -> bool:  # {{{
        return self.__t2.end.price < self.__t1.begin.price

    # }}}
    def period(self) -> int:  # {{{
        return ExtremumList.period(self.__t1.begin, self.__t2.end)

    # }}}
    def deltaPrice(self) -> float:  # {{{
        return ExtremumList.deltaPrice(self.__t1.begin, self.__t2.end)

    # }}}
    def deltaPercent(self) -> float:  # {{{
        return ExtremumList.deltaPercent(self.__t1.begin, self.__t2.end)

    # }}}
    def speedPrice(self) -> float:  # {{{
        return ExtremumList.speedPrice(self.__t1.begin, self.__t2.end)

    # }}}
    def speedPercent(self) -> float:  # {{{
        return ExtremumList.speedPercent(self.__t1.begin, self.__t2.end)

    # }}}
    def volume(self) -> int:  # {{{
        return ExtremumList.volume(self.__t1.begin, self.__t2.end)

    # }}}

    def bullTrend(self) -> Trend:  # {{{
        if self.__t1.isBull():
            return self.__t1

        if self.__t2.isBull():
            return self.__t2

        assert False, "WTF???"

    # }}}
    def bearTrend(self) -> Trend:  # {{{
        if self.__t1.isBear():
            return self.__t1

        if self.__t2.isBear():
            return self.__t2

        assert False, "WTF???"

    # }}}


# }}}


if __name__ == "__main__":
    ...
