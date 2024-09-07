#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

from __future__ import annotations

import abc
from datetime import datetime
from typing import Any, Optional, Union

import pandas as pd

from avin.core.chart import Chart
from avin.core.event import NewBarEvent
from avin.core.timeframe import TimeFrame
from avin.data import AssetType, DataSource, Exchange, InstrumentId
from avin.keeper import Keeper
from avin.utils import AsyncSignal, logger, now


class AssetError(Exception): ...


class Asset(metaclass=abc.ABCMeta):  # {{{
    @abc.abstractmethod  # __init__# {{{
    def __init__(self, ID: InstrumentId):
        logger.debug(f"{self.__class__.name}.__init__()")

        # private fields
        self.__ID: InstrumentId = ID
        self.__charts: dict[TimeFrame, Chart] = dict()
        self.__info: dict[str, Any] | None = None

        # signals
        self.newBar1m = AsyncSignal(Asset, Chart)
        self.newBar5m = AsyncSignal(Asset, Chart)
        self.newBar10m = AsyncSignal(Asset, Chart)
        self.newBar1h = AsyncSignal(Asset, Chart)
        self.newBarD = AsyncSignal(Asset, Chart)
        self.newBarW = AsyncSignal(Asset, Chart)
        self.newBarM = AsyncSignal(Asset, Chart)
        self.updated = AsyncSignal(Asset)

    # }}}
    def __str__(self):  # {{{
        return str(self.__ID)

    # }}}
    def __eq__(self, other):  # {{{
        return self.__ID == other.__ID

    # }}}
    @property  # ID# {{{
    def ID(self):
        return self.__ID

    # }}}
    @property  # exchange# {{{
    def exchange(self):
        return self.__ID.exchange

    # }}}
    @property  # type# {{{
    def type(self):
        return self.__ID.type

    # }}}
    @property  # ticker# {{{
    def ticker(self):
        return self.__ID.ticker

    # }}}
    @property  # figi# {{{
    def figi(self):
        return self.__ID.figi

    # }}}
    @property  # name# {{{
    def name(self):
        return self.__ID.name

    # }}}
    @property  # info# {{{
    def info(self):
        if not self.__info:
            raise AssetError(f"Info not loaded, asset={self}")

        return self.__info

    # }}}
    def chart(self, timeframe: Union[TimeFrame, str]) -> Chart:  # {{{
        logger.debug(f"{self.__class__.name}.chart()")

        # convert type if needed
        if isinstance(timeframe, str):
            timeframe = TimeFrame(timeframe)

        chart = self.__charts.get(timeframe, None)
        if not chart:
            raise AssetError(f"Chart {self.ticker}-{timeframe} not cached")

        return chart

    # }}}
    def clearCache(self) -> None:  # {{{
        logger.debug(f"{self.__class__.name}.clearCache()")
        self.__charts.clear()

    # }}}
    async def cacheChart(  # {{{
        self,
        timeframe: Union[TimeFrame, str],
        begin: Optional[datetime] = None,
        end: Optional[datetime] = None,
    ) -> None:
        logger.debug(f"{self.__class__.__name__}.cacheChart()")

        # format args
        timeframe, begin, end = self.__formatArgs(timeframe, begin, end)

        # load chart and keep it
        chart = await Chart.load(self.ID, timeframe, begin, end)
        self.__charts[timeframe] = chart

    # }}}
    async def cacheInfo(self) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.loadInfo()")

        response = await Keeper.info(
            DataSource.TINKOFF, self.type, figi=self.figi
        )
        assert len(response) == 1  # response == [dict, ]
        self.__info = response[0]

    # }}}
    async def update(self, new_bar_event: NewBarEvent) -> None:  # {{{
        logger.debug(f"{self.__class__.name}.update()")

        # select chart
        timeframe = new_bar_event.timeframe
        chart = self.chart(timeframe)

        # add new bar in this chart
        chart.update(new_bar_event.bar)

        # emiting special signal for the bar timeframe
        signals = {
            "1M": self.newBar1m,
            "5M": self.newBar5m,
            "10M": self.newBar10m,
            "1H": self.newBar1h,
            "D": self.newBarD,
            "W": self.newBarW,
            "M": self.newBarM,
        }
        signal = signals[str(timeframe)]
        await signal.async_emit(self, chart)

        # emiting common signal
        await self.updated.async_emit(self)

    # }}}
    async def loadChart(  # {{{
        self,
        timeframe: Union[TimeFrame, str],
        begin: Optional[datetime] = None,
        end: Optional[datetime] = None,
    ) -> Chart:
        logger.debug(f"{self.__class__.__name__}.loadChart()")

        # format args
        timeframe, begin, end = self.__formatArgs(timeframe, begin, end)

        # load chart and return it
        chart = await Chart.load(self.ID, timeframe, begin, end)
        return chart

    # }}}
    async def loadData(  # {{{
        self,
        timeframe: Union[TimeFrame, str],
        begin: datetime,
        end: datetime,
    ) -> pd.DataFrame:
        logger.debug(f"{self.__class__.name}.loadData()")

        # TODO: return dataframe
        assert False

    # }}}
    @classmethod  # fromRecord# {{{
    def fromRecord(cls, record: asyncpg.Record) -> Asset:
        logger.debug(f"{cls.__name__}.fromRecord()")
        exchange = Exchange.fromStr(record["exchange"])
        asset_type = AssetType.fromStr(record["type"])
        ticker = record["ticker"]
        figi = record["figi"]
        name = record["name"]
        ID = InstrumentId(asset_type, exchange, ticker, figi, name)
        asset = Asset.byId(ID)
        return asset

    # }}}
    @classmethod  # byId #{{{
    def byId(cls, ID: InstrumentId) -> Asset:
        logger.debug(f"{cls.__name__}.byId()")

        asset = cls.__getCertainTypeAsset(ID)
        return asset

    # }}}
    @classmethod  # byTicker# {{{
    async def byTicker(
        cls, asset_type: AssetType, exchange: Exchange, ticker: str
    ) -> Asset:
        logger.debug(f"{cls.__name__}.byTicker()")
        assert isinstance(asset_type, AssetType)
        assert hasattr(exchange, "name")
        assert isinstance(ticker, str)

        asset = await Keeper.get(
            Asset, asset_type=asset_type, exchange=exchange, ticker=ticker
        )
        return asset

    # }}}
    @classmethod  # byFigi# {{{
    async def byFigi(cls, figi: str) -> Asset:
        logger.debug(f"{cls.__name__}.byFigi()")

        asset = await Keeper.get(Asset, figi=figi)
        return asset

    # }}}
    @classmethod  # __formatArgs# {{{
    def __formatArgs(
        cls, timeframe, begin, end
    ) -> tuple[TimeFrame, datetime, datetime]:
        logger.debug(f"{cls.__name__}.__formatArgs()")

        # check timeframe
        if isinstance(timeframe, TimeFrame):
            pass
        elif isinstance(timeframe, str):
            timeframe = TimeFrame(timeframe)
        else:
            logger.critical(
                f"Wrong timeframe='{timeframe}', use valid 'str' "
                "or class TimeFrame"
            )
            raise TypeError(timeframe)

        # when begin & end == None, load DEFAULT_BARS_COUNT
        if begin is None and end is None:
            period = timeframe * Chart.DEFAULT_BARS_COUNT
            begin = now().replace(microsecond=0) - period
            end = now()

        # 'begin', 'end' must be datetime
        if not isinstance(begin, datetime):
            raise TypeError(f"Invalid begin='{begin}'")
        if not isinstance(end, datetime):
            raise TypeError(f"Invalid end='{end}'")

        return timeframe, begin, end

    # }}}
    @classmethod  # __getCertainTypeAsset# {{{
    def __getCertainTypeAsset(cls, ID: InstrumentId):
        logger.debug(f"{cls.__name__}.__getCertainTypeAsset()")

        if ID.type == AssetType.INDEX:
            return Index(ID)
        elif ID.type == AssetType.SHARE:
            return Share(ID)

        logger.critical(f"Unknown asset type={ID.type}")
        assert False

    # }}}


# }}}
class Index(Asset):  # {{{
    def __init__(self, ID: InstrumentId):  # {{{
        logger.debug(f"{self.__class__.name}.__init__()")
        assert ID.type == AssetType.INDEX
        super().__init__(ID)

    # }}}


# }}}
class Share(Asset):  # {{{
    # {{{-- doc
    """ """

    # }}}

    def __init__(self, ID: InstrumentId):  # {{{
        logger.debug(f"{self.__class__.name}.__init__()")
        assert ID.type == AssetType.SHARE
        super().__init__(ID)
        self.__book = None
        self.__tic = None

    # }}}
    @property  # uid{{{
    def uid(self):
        return self.info["uid"]

    # }}}
    @property  # lot{{{
    def lot(self):
        return int(self.info["lot"])

    # }}}
    @property  # min_price_step{{{
    def min_price_step(self):
        return float(self.info["min_price_increment"])

    # }}}


# }}}
class AssetList:  # {{{
    def __init__(self, name: str = "unnamed"):  # {{{
        logger.debug(f"{self.__class__.__name__}.__init__({name})")
        self.__name = name
        self.__assets: list[Asset] = list()

    # }}}
    def __getitem__(self, index: int) -> Asset:  # {{{
        assert index < len(self.__assets)
        return self.__assets[index]

    # }}}
    def __iter__(self):  # {{{
        return iter(self.__assets)

    # }}}
    def __contains__(self, asset: Asset) -> bool:  # {{{
        return any(i.ID == asset.ID for i in self.__assets)

    # }}}
    @property  # name  # {{{
    def name(self) -> str:
        return self.__name

    @name.setter
    def name(self, name: str):
        assert isinstance(name, str)
        self.__name = name

    # }}}
    @property  # assets  # {{{
    def assets(self) -> list[Asset]:
        return self.__assets

    @assets.setter
    def assets(self, assets):
        assert isinstance(assets, list)
        for i in assets:
            assert isinstance(i, Asset)
        self.__assets = assets

    # }}}
    @property  # count  # {{{
    def count(self) -> int:
        return len(self.__assets)

    # }}}
    def add(self, asset: Asset) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.add({asset.ticker})")
        assert isinstance(asset, Asset)
        if asset not in self:
            self.__assets.append(asset)
            return

        logger.warning(f"{asset} already in list '{self.name}'")

    # }}}
    def remove(self, asset: Asset) -> None:  # {{{
        logger.debug(f"AssetList.remove({asset.ticker})")
        try:
            self.__assets.remove(asset)
            return
        except ValueError:
            logger.exception(
                f"AssetList.remove(asset): Fail: "
                f"инструмент '{asset.ticker}' нет в списке '{self.name}'",
            )
            return

    # }}}
    def clear(self) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.clear()")
        self.__assets.clear()

    # }}}
    def find(  # {{{
        self, ID: InstrumentId | None = None, figi: str | None = None
    ) -> Asset | None:
        logger.debug(f"{self.__class__.__name__}.find()")
        if ID:
            return self.__findById(ID)
        if figi:
            asset = self.__findByFigi(figi)
            return asset

        assert False, "Bad arguments"

    # }}}
    def __findById(self, ID: InstrumentId) -> Asset | None:  # {{{
        logger.debug(f"{self.__class__.__name__}.__findById()")
        for i in self.__assets:
            if i.ID == ID:
                return i

        return None

    # }}}
    def __findByFigi(self, figi: str) -> Asset | None:  # {{{
        logger.debug(f"{self.__class__.__name__}.__findByFigi()")
        for i in self.__assets:
            if i.figi == figi:
                return i

        return None

    # }}}
    @classmethod  # fromRecord  # {{{
    async def fromRecord(cls, record: asyncpg.Record) -> AssetList:
        logger.debug(f"{cls.__name__}.fromRecord()")
        name = record["name"]
        figi_list = record["assets"]

        alist = cls(name)
        for figi in figi_list:
            asset = await Asset.byFigi(figi)
            alist.add(asset)

        return alist

    # }}}
    @classmethod  # save  # {{{
    async def save(cls, asset_list: AssetList) -> None:
        logger.debug(f"{cls.__name__}.save()")
        assert isinstance(asset_list, AssetList)
        await Keeper.add(asset_list)

    # }}}
    @classmethod  # load  # {{{
    async def load(cls, name: str) -> AssetList:
        logger.debug(f"{cls.__name__}.load()")
        response = await Keeper.get(cls, name=name)
        assert len(response) == 1  # response == [AssetList, ]
        return response[0]

    # }}}
    @classmethod  # delete  # {{{
    async def delete(cls, asset_list: AssetList) -> None:
        logger.debug(f"{cls.__name__}.delete()")
        assert isinstance(asset_list, AssetList)
        await Keeper.delete(asset_list)

    # }}}
    @classmethod  # rename  # {{{
    async def rename(cls, asset_list: AssetList, new_name: str) -> None:
        logger.debug(f"{cls.__name__}.rename()")
        assert isinstance(new_name, str)
        assert len(new_name) > 0

        await cls.delete(asset_list)
        asset_list.name = new_name
        await cls.save(asset_list)

    # }}}
    @classmethod  # copy  # {{{
    async def copy(cls, asset_list: AssetList, new_name: str) -> None:
        logger.debug(f"{cls.__name__}.copy()")
        new_list = AssetList(new_name)
        new_list.assets = asset_list.assets
        await cls.save(new_list)

    # }}}
    @classmethod  # requestAll# {{{
    async def requestAll(cls) -> list[str]:
        names = await Keeper.get(cls, get_only_names=True)
        return names

    # }}}


# }}}
