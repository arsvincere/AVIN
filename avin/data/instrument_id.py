#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

from __future__ import annotations

from avin.const import Usr
from avin.data.asset_type import AssetType
from avin.data.exchange import Exchange
from avin.utils import Cmd


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
    def __eq__(self, other):  # {{{
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
    @property  # dir_path# {{{
    def dir_path(self):
        path = Cmd.path(Usr.DATA, self.exchange.name, self.type.name, self.ticker)
        return path

    # }}}
    @classmethod  # save# {{{
    def save(cls, ID: InstrumentId, file_path: str) -> None:
        obj = cls.toJson(ID)
        Cmd.saveJson(obj, file_path)

    # }}}
    @classmethod  # load# {{{
    def load(cls, file_path) -> InstrumentId:
        obj = Cmd.loadJson(file_path)
        ID = cls.fromJson(obj)
        return ID

    # }}}
    @classmethod  # toJson# {{{
    def toJson(cls, ID: InstrumentId) -> object:
        obj = {
            "exchange": ID.exchange.name,
            "type": ID.type.name,
            "ticker": ID.ticker,
            "figi": ID.figi,
            "name": ID.name,
        }
        return obj

    # }}}
    @classmethod  # fromJson# {{{
    def fromJson(cls, obj) -> InstrumentId:
        ID = InstrumentId(
            exchange=Exchange.fromStr(obj["exchange"]),
            asset_type=AssetType.fromStr(obj["type"]),
            name=obj["name"],
            ticker=obj["ticker"],
            figi=obj["figi"],
        )
        return ID

    # }}}


# }}}
