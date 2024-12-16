#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

from __future__ import annotations

from collections import defaultdict
from datetime import UTC, date, datetime

from avin.const import DAY_BEGIN, ONE_MINUTE
from avin.core import (
    Bar,
    BarChangedEvent,
    NewHistoricalBarEvent,
    TimeFrameList,
)
from avin.keeper import Keeper
from avin.utils import logger

# TODO: подумать как бы всетаки отправлять еще progress
# никто кроме стрима сейчас не может знать его
# как варинта - передавать сюда не бегин энд, а сам тест
# из него дергать бегин энд
# и тогда (я сейчас перенес сигнал progress в класс Test)
# можно будет от сюда дергать этот сигнал.

# TODO: нихера не помню как он отправляет свечи
# надо проверить - и задокументировать.
# и еще подумать как лучше все таки выдавать свечи 5M 1H
# в конце периода перед новой 1М свечей? или после новой 1М свечи?
# Логичнее в конце периода.
# Сейчас наверное не так работает.
# Надо подумать как бы сделать так.


class BarStream:
    def __init__(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__init__()")
        self.__subscriptions: defaultdict[Asset, TimeFrameList] = defaultdict(
            TimeFrameList
        )
        self.__bars = dict()
        self.__asset = None
        self.__begin = None
        self.__end = None

    # }}}
    def __iter__(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.getNextBar()")

        timeframes = sorted(self.__bars.keys())

        time = self.__begin
        while time < self.__end:
            for timeframe in timeframes:
                bars = self.__bars[timeframe]
                if not bars:
                    continue
                if time < bars[0].dt + timeframe:
                    continue

                # send new historical bar
                last_bar = bars.pop(0)
                figi = self.__asset.figi
                historical = NewHistoricalBarEvent(figi, timeframe, last_bar)
                yield historical

                # send now bar
                if not bars:
                    continue
                now_bar = bars[0]
                now_changed = BarChangedEvent(figi, timeframe, now_bar)
                yield now_changed

            time += ONE_MINUTE

    # }}}
    def subscribe(self, asset, timeframe) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.subscribe()")

        tflist = TimeFrameList([timeframe])
        self.__subscriptions[asset] += tflist

        # WARN:
        # костыль пока работает только по 1 активу
        # когда понадобится делать стрим на несколько активов
        # тогда и переделаю.
        # Пока из этой переменной класс берет фиги, для
        # создания NewBarEvent, подразумевая что актив всегда
        # один и тот же, и в списке баров только бары этого актива
        self.__asset = asset

    # }}}
    async def loadData(self, begin: date, end: date):  # {{{
        logger.debug(f"{self.__class__.__name__}.loadData()")
        assert isinstance(begin, date)
        assert isinstance(end, date)

        self.__begin = datetime.combine(begin, DAY_BEGIN, UTC)
        self.__end = datetime.combine(end, DAY_BEGIN, UTC)
        self.__bars.clear()
        for asset, tflist in self.__subscriptions.items():
            for timeframe in tflist:
                bars = await Keeper.get(
                    Bar,
                    instrument=asset,
                    timeframe=timeframe,
                    begin=begin,
                    end=end,
                )
                self.__bars[timeframe] = bars

    # }}}


if __name__ == "__main__":
    ...
