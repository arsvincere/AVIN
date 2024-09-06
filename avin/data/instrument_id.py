#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

from __future__ import annotations

from avin.data.asset_type import AssetType
from avin.data.exchange import Exchange
from avin.keeper import Keeper
from avin.utils import logger


class InstrumentId:  # {{{
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
    @classmethod  # fromRecord# {{{
    def fromRecord(cls, record) -> InstrumentId:
        ID = InstrumentId(
            exchange=Exchange.fromStr(record["exchange"]),
            asset_type=AssetType.fromStr(record["type"]),
            name=record["name"],
            ticker=record["ticker"],
            figi=record["figi"],
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
    @classmethod  # __checkArgs{{{
    def __checkArgs(
        cls,
        asset_type=None,
        exchange=None,
        ticker=None,
        figi=None,
        name=None,
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

        return True

    # }}}


# }}}
