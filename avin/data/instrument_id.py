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

        self.__info = {
            "type": asset_type,
            "exchange": exchange,
            "ticker": ticker,
            "figi": figi,
            "name": name,
        }

    # }}}
    def __str__(self):  # {{{
        s = f"{self.type.name}-{self.exchange.name}-{self.ticker}"
        return s

    # }}}
    def __eq__(self, other: InstrumentId):  # {{{
        return self.__info == other.__info

    # }}}
    @property  # exchange# {{{
    def exchange(self):
        return self.__info["exchange"]

    # }}}
    @property  # type# {{{
    def type(self):
        return self.__info["type"]

    # }}}
    @property  # ticker# {{{
    def ticker(self):
        return self.__info["ticker"]

    # }}}
    @property  # figi# {{{
    def figi(self):
        return self.__info["figi"]

    # }}}
    @property  # name# {{{
    def name(self):
        return self.__info["name"]

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
    async def byFigi(cls, figi) -> InstrumentId:
        id_list = await Keeper.get(InstrumentId, figi=figi)
        assert len(id_list) == 1
        ID = id_list[0]

        return ID

    # }}}


# }}}
