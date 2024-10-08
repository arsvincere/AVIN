#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

from __future__ import annotations

from avin.data.asset_type import AssetType
from avin.data.data_source import DataSource
from avin.data.exchange import Exchange
from avin.keeper import Keeper
from avin.utils import logger


class InstrumentId:
    """doc # {{{
    Unified identifier for all assets.
    """

    # }}}
    def __init__(  # {{{
        self,
        asset_type: AssetType,
        exchange: Exchange,
        ticker: str,
        figi: str,
        name: str,
    ):
        assert isinstance(asset_type, AssetType)
        assert hasattr(exchange, "name")

        self.__type = asset_type
        self.__exchange = exchange
        self.__ticker = ticker
        self.__figi = figi
        self.__name = name
        self.__info = None

    # }}}
    def __str__(self):  # {{{
        s = f"{self.type.name}-{self.exchange.name}-{self.ticker}"
        return s

    # }}}
    def __eq__(self, other: object) -> bool:  # {{{
        assert hasattr(other, "figi")
        return self.figi == other.figi

    # }}}
    @property  # exchange# {{{
    def exchange(self):
        return self.__exchange

    # }}}
    @property  # type# {{{
    def type(self):
        return self.__type

    # }}}
    @property  # ticker# {{{
    def ticker(self):
        return self.__ticker

    # }}}
    @property  # figi# {{{
    def figi(self):
        return self.__figi

    # }}}
    @property  # name# {{{
    def name(self):
        return self.__name

    # }}}
    @property  # info# {{{
    def info(self):
        return self.__info

    # }}}
    @property  # lot# {{{
    def lot(self):
        return int(self.info["lot"])

    # }}}
    @property  # min_price_step# {{{
    def min_price_step(self):
        return float(self.info["min_price_increment"])

    # }}}
    async def cacheInfo(self) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.loadInfo()")

        response = await Keeper.info(
            DataSource.TINKOFF, self.type, figi=self.figi
        )
        assert len(response) == 1  # response == [dict, ]
        self.__info = response[0]

    # }}}
    @classmethod  # fromRecord# {{{
    def fromRecord(cls, record) -> InstrumentId:
        ID = InstrumentId(
            asset_type=AssetType.fromStr(record["type"]),
            exchange=Exchange.fromStr(record["exchange"]),
            ticker=record["ticker"],
            figi=record["figi"],
            name=record["name"],
        )

        return ID

    # }}}
    @classmethod  # byFigi# {{{
    async def byFigi(cls, figi: str) -> InstrumentId:
        if not cls.__checkArgs(figi=figi):
            assert False

        id_list = await Keeper.get(InstrumentId, figi=figi)

        assert len(id_list) == 1
        ID = id_list[0]
        return ID

    # }}}
    @classmethod  # byTicker# {{{
    async def byTicker(
        cls, asset_type: AssetType, exchange: Exchange, ticker: str
    ) -> InstrumentId:
        logger.debug(f"{cls.__name__}.byTicker()")

        if not cls.__checkArgs(
            asset_type=asset_type, exchange=exchange, ticker=ticker
        ):
            assert False

        id_list = await Keeper.get(
            InstrumentId,
            asset_type=asset_type,
            exchange=exchange,
            ticker=ticker,
        )

        assert len(id_list) == 1
        ID = id_list[0]
        return ID

    # }}}
    @classmethod  # byUid# {{{
    async def byUid(cls, uid: str) -> InstrumentId | None:
        logger.debug(f"{cls.__name__}.byUid()")

        if not cls.__checkArgs(uid=uid):
            return None

        info_list = await Keeper.info(
            source=DataSource.TINKOFF, asset_type=None, uid=uid
        )
        assert len(info_list) == 1
        info = info_list[0]

        ID = InstrumentId(
            asset_type=AssetType.fromStr(info["type"]),
            exchange=Exchange.fromStr(info["exchange"]),
            ticker=info["ticker"],
            figi=info["figi"],
            name=info["name"],
        )

        return ID

    # }}}
    @classmethod  # __checkArgs{{{
    def __checkArgs(
        cls,
        asset_type=None,
        exchange=None,
        ticker=None,
        figi=None,
        name=None,
        uid=None,
    ):
        if asset_type:
            assert isinstance(asset_type, AssetType)
        if exchange:
            assert hasattr(exchange, "name")
        if ticker:
            assert isinstance(ticker, str)
        if figi:
            assert isinstance(figi, str)
        if name:
            assert isinstance(name, str)
        if uid:
            assert isinstance(uid, str)

        return True

    # }}}
