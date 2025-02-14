#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

from __future__ import annotations

from collections import defaultdict
from datetime import UTC, datetime

from avin.const import DAY_BEGIN, ONE_MINUTE
from avin.core import (
    Asset,
    Bar,
    BarChangedEvent,
    NewHistoricalBarEvent,
    TimeFrame,
    TimeFrameList,
)
from avin.keeper import Keeper
from avin.utils import Date, logger

# TODO: подумать как бы всетаки отправлять еще progress
# никто кроме стрима сейчас не может знать его
# как варинта - передавать сюда не бегин энд, а сам тест
# из него дергать бегин энд
# и тогда (я сейчас перенес сигнал progress в класс Test)
# можно будет от сюда дергать этот сигнал.

"""BarStream - выдает бары по очереди в хронологическом порядке

Пока работает только с одним активом. Assert если попытаться подписаться
на несколько разных активов.

Выдает свечи сначала младшего таймфрейма, потом старшего 1M - 5M - 1H - D ...

Сначала выдает историческую свечу, потом 'реал-тайм', выдача выглядит так:

stream: 2024-12-16 16:18:57 [DEBUG] BarStream.getNextBar()# {{{
1M-2023-08-01 06:59:00+00:00 NEW_HISTORICAL_BAR
1M-2023-08-01 07:00:00+00:00 BAR_CHANGED
5M-2023-08-01 06:55:00+00:00 NEW_HISTORICAL_BAR
5M-2023-08-01 07:00:00+00:00 BAR_CHANGED
1H-2023-08-01 06:00:00+00:00 NEW_HISTORICAL_BAR
1H-2023-08-01 07:00:00+00:00 BAR_CHANGED
1M-2023-08-01 07:00:00+00:00 NEW_HISTORICAL_BAR
1M-2023-08-01 07:01:00+00:00 BAR_CHANGED
1M-2023-08-01 07:01:00+00:00 NEW_HISTORICAL_BAR
1M-2023-08-01 07:02:00+00:00 BAR_CHANGED
1M-2023-08-01 07:02:00+00:00 NEW_HISTORICAL_BAR
1M-2023-08-01 07:03:00+00:00 BAR_CHANGED
1M-2023-08-01 07:03:00+00:00 NEW_HISTORICAL_BAR
1M-2023-08-01 07:04:00+00:00 BAR_CHANGED
1M-2023-08-01 07:04:00+00:00 NEW_HISTORICAL_BAR
1M-2023-08-01 07:05:00+00:00 BAR_CHANGED
5M-2023-08-01 07:00:00+00:00 NEW_HISTORICAL_BAR
5M-2023-08-01 07:05:00+00:00 BAR_CHANGED
1M-2023-08-01 07:05:00+00:00 NEW_HISTORICAL_BAR
1M-2023-08-01 07:06:00+00:00 BAR_CHANGED
1M-2023-08-01 07:06:00+00:00 NEW_HISTORICAL_BAR
1M-2023-08-01 07:07:00+00:00 BAR_CHANGED
1M-2023-08-01 07:07:00+00:00 NEW_HISTORICAL_BAR
1M-2023-08-01 07:08:00+00:00 BAR_CHANGED
1M-2023-08-01 07:08:00+00:00 NEW_HISTORICAL_BAR
1M-2023-08-01 07:09:00+00:00 BAR_CHANGED
1M-2023-08-01 07:09:00+00:00 NEW_HISTORICAL_BAR
1M-2023-08-01 07:10:00+00:00 BAR_CHANGED
5M-2023-08-01 07:05:00+00:00 NEW_HISTORICAL_BAR
5M-2023-08-01 07:10:00+00:00 BAR_CHANGED
1M-2023-08-01 07:10:00+00:00 NEW_HISTORICAL_BAR
1M-2023-08-01 07:11:00+00:00 BAR_CHANGED
1M-2023-08-01 07:11:00+00:00 NEW_HISTORICAL_BAR
1M-2023-08-01 07:12:00+00:00 BAR_CHANGED
1M-2023-08-01 07:12:00+00:00 NEW_HISTORICAL_BAR

...

1M-2023-08-01 20:45:00+00:00 NEW_HISTORICAL_BAR
1M-2023-08-01 20:46:00+00:00 BAR_CHANGED
1M-2023-08-01 20:46:00+00:00 NEW_HISTORICAL_BAR
1M-2023-08-01 20:47:00+00:00 BAR_CHANGED
1M-2023-08-01 20:47:00+00:00 NEW_HISTORICAL_BAR
1M-2023-08-01 20:48:00+00:00 BAR_CHANGED
1M-2023-08-01 20:48:00+00:00 NEW_HISTORICAL_BAR
1M-2023-08-01 20:49:00+00:00 BAR_CHANGED
1M-2023-08-01 20:49:00+00:00 NEW_HISTORICAL_BAR
1M-2023-08-02 06:59:00+00:00 BAR_CHANGED
5M-2023-08-01 20:45:00+00:00 NEW_HISTORICAL_BAR
5M-2023-08-02 06:55:00+00:00 BAR_CHANGED
1H-2023-08-01 20:00:00+00:00 NEW_HISTORICAL_BAR
1H-2023-08-02 06:00:00+00:00 BAR_CHANGED

D-2023-08-01 00:00:00+00:00 NEW_HISTORICAL_BAR
D-2023-08-02 00:00:00+00:00 BAR_CHANGED
1M-2023-08-02 06:59:00+00:00 NEW_HISTORICAL_BAR
1M-2023-08-02 07:00:00+00:00 BAR_CHANGED
5M-2023-08-02 06:55:00+00:00 NEW_HISTORICAL_BAR
5M-2023-08-02 07:00:00+00:00 BAR_CHANGED
1H-2023-08-02 06:00:00+00:00 NEW_HISTORICAL_BAR
1H-2023-08-02 07:00:00+00:00 BAR_CHANGED
1M-2023-08-02 07:00:00+00:00 NEW_HISTORICAL_BAR
1M-2023-08-02 07:01:00+00:00 BAR_CHANGED
1M-2023-08-02 07:01:00+00:00 NEW_HISTORICAL_BAR
1M-2023-08-02 07:02:00+00:00 BAR_CHANGED
1M-2023-08-02 07:02:00+00:00 NEW_HISTORICAL_BAR
1M-2023-08-02 07:03:00+00:00 BAR_CHANGED
1M-2023-08-02 07:03:00+00:00 NEW_HISTORICAL_BAR
1M-2023-08-02 07:04:00+00:00 BAR_CHANGED
1M-2023-08-02 07:04:00+00:00 NEW_HISTORICAL_BAR
1M-2023-08-02 07:05:00+00:00 BAR_CHANGED
5M-2023-08-02 07:00:00+00:00 NEW_HISTORICAL_BAR
5M-2023-08-02 07:05:00+00:00 BAR_CHANGED
1M-2023-08-02 07:05:00+00:00 NEW_HISTORICAL_BAR
1M-2023-08-02 07:06:00+00:00 BAR_CHANGED
1M-2023-08-02 07:06:00+00:00 NEW_HISTORICAL_BAR
1M-2023-08-02 07:07:00+00:00 BAR_CHANGED
1M-2023-08-02 07:07:00+00:00 NEW_HISTORICAL_BAR
...
# }}}
"""


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
        self.__subscriptions[asset].add(timeframe)

        if self.__asset is None:
            self.__asset = asset  # сохраняем ассет от первой подписки
        else:
            # NOTE:
            # пока можно подписываться только на один и тот же ассет
            # на разные таймфреймы. Выдача баров по нескольким активам
            # одновременно не реализована.
            # Чтобы не забыть - впилю тут асерт
            assert self.__asset == asset

    # }}}
    async def loadData(self, begin: Date, end: Date):  # {{{
        logger.debug(f"{self.__class__.__name__}.loadData()")
        assert isinstance(begin, Date)
        assert isinstance(end, Date)

        self.__bars.clear()
        self.__begin = datetime.combine(begin, DAY_BEGIN, UTC)
        self.__end = datetime.combine(end, DAY_BEGIN, UTC)

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


class BarStream2:
    def __init__(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__init__()")

        self.__asset = None
        self.__timeframe_list = TimeFrameList()
        self.__begin = None
        self.__end = None
        self.__bars = list()  # 1m bars
        self.__time = None

    # }}}
    def __iter__(self):  # {{{
        timeframes = sorted(self.__bars.keys())

        self.__time = self.__begin
        self.__sendInitialBars()

        while self.__time < self.__end:
            time += ONE_MINUTE

            if not self.__bars:
                continue
            if self.__time < self.__bars[0].dt + ONE_MINUTE:
                continue

            # send 1m historical bar
            last_bar = self.__bars.pop(0)
            figi = self.__asset.figi
            historical = NewHistoricalBarEvent(figi, timeframe, last_bar)
            yield historical

            # send 1m now bar
            if not bars:
                continue
            now_bar = bars[0]
            now_changed = BarChangedEvent(figi, timeframe, now_bar)
            yield now_changed

            # send other timeframes
            if self.__bar_5M is not None:
                self.__sendBar5M(now_bar)
            if self.__bar_1H is not None:
                self.__sendBar1H(now_bar)
            if self.__bar_D is not None:
                self.__sendBarD(now_bar)

    # }}}
    def setAsset(self, asset: Asset) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.setAsset()")
        assert isinstance(asset, Asset)

        self.__asset = asset

    # }}}
    def subscribe(self, timeframe) -> None:  # {{{
        assert str(timeframe) in ("1H", "5M", "1H", "D")

        self.__timeframe_list.add(timeframe)

    # }}}
    async def loadData(self, begin: Date, end: Date):  # {{{
        logger.debug(f"{self.__class__.__name__}.loadData()")
        assert isinstance(begin, Date)
        assert isinstance(end, Date)

        self.__bars = await Keeper.get(
            Bar,
            instrument=self.__asset,
            timeframe=TimeFrame("1M"),
            begin=begin,
            end=end,
        )
        self.__begin = datetime.combine(begin, DAY_BEGIN, UTC)
        self.__end = datetime.combine(end, DAY_BEGIN, UTC)

    # }}}

    def __sendInitialBars(self):  # {{{
        # send first 1m historical bar
        first_bar = self.__bars.pop(0)
        figi = self.__asset.figi
        event = NewHistoricalBarEvent(figi, TimeFrame("1M"), first_bar)
        yield event

        # send first 1m real-time bar
        now_bar = self.__bars.pop(0)

        # send other timeframes real-time bars
        if TimeFrame("5M") in self.__timeframe_list:
            self.__bar_5m = first_bar
            self.__time_5m = self.__getNextTime(TimeFrame("5M"), first_bar)
            event = BarChangedEvent(figi, TimeFrame("1H"), first_bar)
            yield event
        if TimeFrame("1H") in self.__timeframe_list:
            self.__bar_1h = first_bar
            self.__time_1h = self.__getNextTime(TimeFrame("1H"), first_bar)
            event = BarChangedEvent(figi, TimeFrame("1H"), first_bar)
            yield event
        if TimeFrame("D") in self.__timeframe_list:
            self.__bar_d = first_bar
            self.__time_d = self.__getNextTime(TimeFrame("D"), first_bar)
            event = BarChangedEvent(figi, TimeFrame("D"), first_bar)
            yield event

    # }}}
    def __sendBar1H(self, bar_1m: Bar):  # {{{
        if self.__time < self.__time_1h:
            self.__bar_1H = self.__joinBar(self.__bar_1H, bar_1m)
            event = BarChangedEvent(figi, TimeFrame("1H"), self.__bar_1H)
            return event

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

if __name__ == "__main__":
    ...
