#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

""" doc """

from __future__ import annotations
import csv
from datetime import datetime
from avin.data import Data, DataType
from avin.core.bar import Bar
from avin.utils import findLeft
from avin.logger import logger

class Chart():# {{{
    """ Const """# {{{
    DEFAULT_BARS_COUNT = 5000
    # }}}
    def __init__(# {{{
        self,
        asset: Asset,
        timeframe: TimeFrame,
        begin: datetime,
        end: datetime
        ):

        self._asset = asset
        self._timeframe = timeframe
        self._bars = self.__loadBars(asset, timeframe, begin, end)
        self.__head = len(self._bars)  # индекс HEAD бара
        self.__now = None  # хранит реал-тайм бар
    # }}}
    def __getitem__(self, index):# {{{
        """ Доступ к барам графика по индексу
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
        if index == 0:
            return self.__now  # возвращаем реал тайм бар
        index = self.__head - index
        if index < 0:
            return None
        if index >= len(self._bars):
            return None
        return self._bars[index]
    # }}}
    def __iter__(self):# {{{
        return iter(self._bars)
    # }}}
    @property  #asset# {{{
    def asset(self):
        return self._asset
    # }}}
    @property  #timeframe# {{{
    def timeframe(self):
        return self._timeframe
    # }}}
    @property  #first# {{{
    def first(self):
        """ Возвращает самый старый исторический бар в графике """
        return self._bars[0]
    # }}}
    @property  #last# {{{
    def last(self):
        """
        Возвращает самый новый исторический бар (относительно head!!!)
        """
        index = self.__head - 1
        if 0 < index < len(self._bars):
            return self._bars[index]
        else:
            return None
    # }}}
    @property  #now# {{{
    def now(self):
        """
        Возвращает реал тайм бар, тоже что chart[0]
        """
        return self.__now
    # }}}
    def update(self, new_bars: list[Bar]):# {{{
        for bar in new_bars:
            bar.setChart(self)
            self._bars.append(bar)
        self.__head = len(self._bars)  # индекс HEAD бара перемещаем
        self.__now = None
    # }}}
    def getBars(self) -> list[Bar]:# {{{
        return self._bars[0:self.__head]
    # }}}
    def getTodayBars(self):# {{{
        if self.__now is None:
            return list()
        today = self.__now.dt.date()
        i = self.__head
        while i - 1 > 0 and self._bars[i - 1].dt.date() == today:
            i -= 1
        return self._bars[i: self.__head]
    # }}}
    def _setHeadIndex(self, index):# {{{
        assert False
        assert isinstance(index, int)
        if index < 0:
            return False
        if index > len(self._bars):
            return False
        self.__head = index
        self.__now = self._bars[self.__head]
        return True
    # }}}
    def _getHeadIndex(self):# {{{
        assert False
        return self.__head
    # }}}
    def _setHeadDatetime(self, dt: datetime):# {{{
        assert False
        assert isinstance(dt, datetime)
        index = findLeft(self._bars, dt, lambda x: x.dt)
        if index is not None:
            self.__head = index
            self.__now = self._bars[index]
            return True
        else:
            assert False
    # }}}
    def _resetHead(self):# {{{
        assert False
        self.__head = len(self._bars)
        self.__now = None
    # }}}
    def _nextHead(self):# {{{
        assert False
        if self.__head < len(self._bars) - 1:
            self.__head += 1
            self.__now = self._bars[self.__head]
            return self.__now
        else:
            return None
    # }}}
    def __loadBars(self, asset, timeframe, begin, end):# {{{
        logger.debug(f"Chart.__loadBars()")
        files = Data.request(
            asset.ID,
            timeframe.toDataType(),
            begin.year,
            end.year
            )

        all_bars = list()
        for file_path in files:
            with open(file_path, "r", encoding="utf-8", newline='') as file:
                reader = csv.reader(file, delimiter=";")
                for row in reader:
                    bar = Bar.fromCSV(row, chart=self)
                    if begin <= bar.dt < end:
                        all_bars.append(bar)

        assert len(all_bars) > 0
        return all_bars
    # }}}

# }}}



if __name__ == "__main__":
    ...

