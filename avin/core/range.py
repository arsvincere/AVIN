#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

""" Doc """

from __future__ import annotations
import sys
import enum

sys.path.append("/home/alex/AVIN")
sys.path.append("/home/alex/AVIN/env/lib/python3.12/site-packages")

class Range():# {{{
    """ doc# {{{
    Закрытый диапазон [min, max]
    Представляет части бара - тело, тени или весь диапазон бара.
    --
    Example:
    r = Range[10, 18]
    print(11 in r)  # True
    print(30 in r)  # False
    print(r.mid())  # 14
    print(r.abs())  # 8
    --
    bar = Bar(now(), 10, 11, 11.1, 9.9, 1000)
    body = bar.body  # Range(10, 11)
    print(10.9 in body)  # True
    """
    # }}}
    class Type(enum.Enum):# {{{
        UNDEFINE =  0
        RANGE =     1
        BODY =      2
        UPPER =     3
        LOWER =     4
    # }}}
    class Size(enum.Enum):# {{{
        UNDEFINE =          0
        BLACKSWAN_SMALL =   1
        ANOMAL_SMALL =      2
        EXTRA_SMALL =       3
        VERY_SMALL =        4
        SMALLEST =          5
        SMALLER =           6
        SMALL =             7
        NORMAL =            8
        BIG =               9
        BIGGER =            10
        BIGGEST =           11
        VERY_BIG =          12
        EXTRA_BIG =         13
        ANOMAL_BIG =        14
        BLACKSWAN_BIG =     15
    # }}}
    def __init__(# {{{
            self, min_: float, max_: float, type_ = Type.UNDEFINE, bar = None
            ):
        self.__min = min_
        self.__max = max_
        self.__type = type_
        self.__bar = bar
    # }}}
    def __getitem__(self, slice_):# {{{
        """ doc
        Возвращает диапазон
        [0, 10] - от 0 до 10% исходного диапазона
        [40, 100] - от 40% до 100% исходного диапазона
        --
        Example:
        bar.body[0, 5] - нижние 5% тела бара
        bar.upper[90, 100] - верхние 10% верхней тени бара
        """
        assert isinstance(slice_, slice)
        assert slice_.step is None
        assert slice_.start >= 0
        assert slice_.stop <= 100
        assert slice_.start < slice_.stop
        if slice_.start == 0:
            start = self.__min
        else:
            tmp = (self.__max - self.__min) * slice_.start / 100
            start = self.__min + tmp
        if slice_.stop == 0:
            stop = self.__max
        else:
            tmp = (self.__max - self.__min) * slice_.stop / 100
            stop = self.__min + tmp
        return Range(start, stop)
    # }}}
    def __contains__(self, price: float) -> bool:# {{{
        return self.__min <= price <= self.__max
    # }}}
    def __repr__(self):# {{{
        return f"Range({self.min}, {self.max})"
    # }}}
    @property  #min# {{{
    def min(self):
        return self.__min
    # }}}
    @property  #max# {{{
    def max(self):
        return self.__max
    # }}}
    @property  #type# {{{
    def type(self):
        return self.__type
    # }}}
    @property  #bar# {{{
    def bar(self):
        """ doc
        Return parent Bar
        """
        return self.__bar
    # }}}
    def percent(self) -> float:# {{{
        """ doc
        Return percent of range
        """
        percent = (self.__max - self.__min) / self.__max * 100
        return round(percent, 2)
    # }}}
    def abs(self) -> float:# {{{
        """ doc
        Return abs of range
        """
        return self.__max - self.__min
    # }}}
    def mid(self) -> float:# {{{
        """ doc
        Return middle of range
        """
        half = (self.__max - self.__min) / 2
        return self.__min + half
    # }}}
    def half(self, n) -> Range:# {{{
        """ doc
        Возвращает диапазон n-ой половины бара -> Range
               #
               ###
               #        Это 2 половина <half2>
               #
        ----   #   ----
               #
               #        Это 1 половина <half1>
             ###
               #
        """
        assert n in (1, 2)
        half = (self.__max - self.__min) / 2
        if n == 1:
            return Range(self.__min, self.__min + half)
        elif n == 2:
            return Range(self.__min + half, self.__max)
    # }}}
    def third(self, n) -> Range:# {{{
        """ doc
        Возвращает диапазон n-ой трети бара -> Range
               #
               ###      Это 3 треть
        ----   #   ----
               #
               #        Это 2 треть
        ----   #   ----
             ###
               #        Это 1 треть
        """
        assert n in (1, 2, 3)
        third = (self.__max - self.__min) / 3
        if n == 1:
            return Range(self.__min, self.__min + third)
        elif n == 2:
            return Range(self.__min + third, self.__min + 2 * third)
        elif n == 3:
            return Range(self.__min + 2 * third, self.__max)
    # }}}
    def quarter(self, n) -> Range:# {{{
        """ doc
        Возвращает диапазон n-ой четверти бара -> Range
               #
               ###      Это 4 четверть
        ----   #   ----
               #        Это 3 четверть
        ----   #   ----
               #        Это 2 четверть
        ----   #   ----
             ###        Это 1 четверть
               #
        """
        assert n in (1, 2, 3, 4)
        quarter = (self.__max - self.__min) / 4
        if n == 1:
            return Range(self.__min, self.__min + quarter)
        elif n == 2:
            return Range(self.__min + quarter, self.__min + 2 * quarter)
        elif n == 3:
            return Range(self.__min + 2 * quarter, self.__min + 3 * quarter)
        elif n == 4:
            return Range(self.__min + 3 * quarter, self.__max)
    # }}}
# }}}
