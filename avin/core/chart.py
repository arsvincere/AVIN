#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

"""doc"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Optional

from avin.core.bar import Bar
from avin.core.timeframe import TimeFrame
from avin.data import InstrumentId
from avin.keeper import Keeper
from avin.utils import find_left, logger


class Chart:
    """Const"""  # {{{

    DEFAULT_BARS_COUNT = 5000

    # }}}
    def __init__(  # {{{
        self,
        ID: InstrumentId,
        timeframe: TimeFrame,
        bars: list[Bar],
    ):
        logger.debug(f"{self.__class__.__name__}.__init__()")

        check = self.__checkArgs(ID, timeframe, bars)
        if not check:
            return

        self.__ID = ID
        self.__timeframe = timeframe

        for i in bars:
            i.setChart(self)
        self.__bars = bars

        self.__head = len(self.__bars)  # index of HEAD bar
        self.__now: Optional[Bar] = None  # realtime bar

    # }}}
    def __getitem__(self, index: int):  # {{{
        """Доступ к барам графика по индексу
        ----------------------------------------------------------------------
        [0, 1, 2, 3] (real_time_bar)  - так данные лежат физически
         4  3  2  1        0          - так через getitem [i]
        По умолчанию head == len(bars) == 4, тогда:
        chart[0]   - перехватываем и возвращаем реал тайм бар,
        chart[1] == bars[4 - 1] == bars[3] указывает на вчерашний бар
        chart[2] == bars[4 - 2] == bars[2] указывает на позавчера
        chart[3] == bars[4 - 3] == bars[1] ...
        chart[4] == bars[4 - 4] == bars[0] самый старый исторический
        сhart[5] == 4 - 5 < 0 перехватываем и возвращаем None
        ----------------------------------------------------------------------
        Если head установить == 0, тогда:
        chart[0]     перехватываем и возвращаем реал тайм бар,
        chart[1] == 0 - 1 < 0 перехватываем и возвращаем None
        """
        logger.debug(f"{self.__class__.__name__}.__getitem__()")

        if index == 0:
            return self.__now  # возвращаем реал тайм бар
        index = self.__head - index
        if index < 0:
            return None
        if index >= len(self.__bars):
            return None
        return self.__bars[index]

    # }}}
    def __iter__(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__iter__()")
        return iter(self.__bars)

    # }}}
    @property  # ID# {{{
    def ID(self):
        return self.__ID

    # }}}
    @property  # timeframe# {{{
    def timeframe(self):
        return self.__timeframe

    # }}}
    @property  # first# {{{
    def first(self):
        """Возвращает самый старый исторический бар в графике"""
        return self.__bars[0]

    # }}}
    @property  # last# {{{
    def last(self):
        """
        Возвращает самый новый исторический бар (относительно head!!!)
        """
        index = self.__head - 1
        if 0 < index < len(self.__bars):
            return self.__bars[index]
        else:
            return None

    # }}}
    @property  # now# {{{
    def now(self):
        """
        Возвращает реал тайм бар, тоже что chart[0]
        """
        return self.__now

    # }}}
    def addNewBar(self, new_bar: Bar) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.update()")
        new_bar.setChart(self)
        self.__bars.append(new_bar)
        self.__head = len(self.__bars)
        self.__now = None

    # }}}
    def getBars(self) -> list[Bar]:  # {{{
        logger.debug(f"{self.__class__.__name__}.getBars()")
        return self.__bars[0 : self.__head]

    # }}}
    def getTodayBars(self) -> list[Bar]:  # {{{
        logger.debug(f"{self.__class__.__name__}.getTodayBars()")
        if self.__now is None:
            return list()
        today = self.__now.dt.date()
        i = self.__head
        while i - 1 > 0 and self.__bars[i - 1].dt.date() == today:
            i -= 1
        return self.__bars[i : self.__head]

    # }}}
    def setHeadIndex(self, index) -> bool:  # {{{
        logger.debug(f"{self.__class__.__name__}.setHeadIndex()")
        assert isinstance(index, int)
        if index < 0:
            return False
        if index > len(self.__bars):
            return False
        self.__head = index
        self.__now = self.__bars[self.__head]
        return True

    # }}}
    def getHeadIndex(self) -> int:  # {{{
        logger.debug(f"{self.__class__.__name__}.getHeadIndex()")
        return self.__head

    # }}}
    def setHeadDatetime(self, dt: datetime) -> bool:  # {{{
        logger.debug(f"{self.__class__.__name__}.setHeadDatetime()")
        assert isinstance(dt, datetime)

        index = find_left(self.__bars, dt, lambda x: x.dt)
        if index is not None:
            self.__head = index
            self.__now = self.__bars[index]
            return True
        else:
            assert False

    # }}}
    def resetHead(self) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.resetHead()")
        self.__head = len(self.__bars)
        self.__now = None

    # }}}
    def nextHead(self) -> Bar | None:  # {{{
        logger.debug(f"{self.__class__.__name__}.nextHead()")
        if self.__head < len(self.__bars) - 1:
            self.__head += 1
            self.__now = self.__bars[self.__head]
            return self.__now
        else:
            return None

    # }}}
    @classmethod  # load# {{{
    async def load(
        cls,
        ID: InstrumentId,
        timeframe: TimeFrame,
        begin: datetime,
        end: datetime,
    ) -> Chart:
        logger.debug(f"{cls.__name__}.load()")
        # check args, may be raise TypeError, ValueError
        cls.__checkArgs(
            ID=ID,
            timeframe=timeframe,
            begin=begin,
            end=end,
        )

        # request bars
        bars = await Keeper.get(
            Bar,
            ID=ID,
            timeframe=timeframe,
            begin=begin,
            end=end,
        )

        # create and return chart
        chart = Chart(ID, timeframe, bars)
        return chart

    # }}}
    @classmethod  # __checkArgs  # {{{
    def __checkArgs(
        cls,
        ID=None,
        timeframe=None,
        bars=None,
        begin=None,
        end=None,
    ):
        logger.debug(f"{cls.__name__}.__checkArgs()")
        if ID:
            cls.__checkID(ID)

        if timeframe:
            cls.__checkTimeFrame(timeframe)

        if bars:
            cls.__checkBars(bars)

        if begin:
            cls.__checkBegin(begin)

        if end:
            cls.__checkEnd(end)

        return True

    # }}}
    @classmethod  # __checkAsset  # {{{
    def __checkID(cls, ID):
        logger.debug(f"{cls.__name__}.__checkID()")

        if not isinstance(ID, InstrumentId):
            logger.critical(f"Invalid ID={ID}")
            raise TypeError(ID)

    # }}}
    @classmethod  # __checkTimeFrame  # {{{
    def __checkTimeFrame(cls, timeframe):
        logger.debug(f"{cls.__name__}.__checkTimeFrame()")

        if not isinstance(timeframe, TimeFrame):
            logger.critical(f"Invalid timeframe={timeframe}")
            raise TypeError(timeframe)

    # }}}
    @classmethod  # __checkBars  # {{{
    def __checkBars(cls, bars):
        logger.debug(f"{cls.__name__}.__checkBars()")

        if not isinstance(bars, list):
            logger.critical(f"Invalid bars={bars}")
            raise TypeError(bars)
        if len(bars) == 0:
            logger.critical("Impossible create chart from 0 bars")
            raise ValueError(bars)
        bar = bars[0]
        if not isinstance(bar, Bar):
            logger.critical(f"Invalid bar={bar}")
            raise TypeError(bar)

    # }}}
    @classmethod  # __checkBegin  # {{{
    def __checkBegin(cls, begin: datetime):
        logger.debug(f"{cls.__name__}.__checkBegin()")

        if not isinstance(begin, datetime):
            logger.critical(f"Invalid begin={begin}")
            raise TypeError(begin)

        if begin.tzinfo != UTC:
            logger.critical("Invalid begin timezone='{begin.tzinfo}")
            raise ValueError(begin)

    # }}}
    @classmethod  # __checkEnd  # {{{
    def __checkEnd(cls, end: datetime):
        logger.debug(f"{cls.__name__}.__checkEnd()")

        if not isinstance(end, datetime):
            logger.critical(f"Invalid end={end}")
            raise TypeError(end)

        if end.tzinfo != UTC:
            logger.critical("Invalid end timezone='{end.tzinfo}")
            raise ValueError(end)

    # }}}
