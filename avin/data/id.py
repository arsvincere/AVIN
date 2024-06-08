#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

from __future__ import annotations
from avin.const import Usr
from avin.data.exchange import Exchange
from avin.data.asset_type import AssetType
from avin.utils import Cmd

class Id():# {{{
    """ doc # {{{
    Unified identifier for all assets.
    """
    # }}}
    def __init__(# {{{
        self,
        exchange: Exchange,
        asset_type: AssetType,
        name: str,
        ticker: str,
        figi: str,
        ):

        self.__info = {
            "exchange": exchange,
            "type": asset_type,
            "name": name,
            "ticker": ticker,
            "figi": figi,
            }
    # }}}
    def __str__(self):# {{{
        s = f"{self.exchange.name}-{self.type.name}-{self.ticker}-{self.figi}"
        return s
    # }}}
    def __eq__(self, other):# {{{
        return self.__info == other.__info
    # }}}
    @property  #exchange# {{{
    def exchange(self):
        return self.__info["exchange"]
    # }}}
    @property  #type# {{{
    def type(self):
        return self.__info["type"]
    # }}}
    @property  #name# {{{
    def name(self):
        return self.__info["name"]
    # }}}
    @property  #ticker# {{{
    def ticker(self):
        return self.__info["ticker"]
    # }}}
    @property  #figi# {{{
    def figi(self):
        return self.__info["figi"]
    # }}}
    @property  #dir_path# {{{
    def dir_path(self):
        path = Cmd.path(
            Usr.DATA, self.exchange.name, self.type.name, self.ticker
            )
        return path
    # }}}
    @classmethod  #save# {{{
    def save(cls, ID: Id, file_path: str):
        Cmd.saveJson(ID, file_path, Id._encoderJson)
    # }}}
    @classmethod  #load# {{{
    def load(cls, file_path):
        obj = Cmd.loadJson(file_path, Id._decoderJson)
        ID = Id(
            obj["exchange"],
            obj["type"],
            obj["name"],
            obj["ticker"],
            obj["figi"],
            )
        return ID
    # }}}
    @staticmethod  #_encoderJson# {{{
    def _encoderJson(obj):
        if isinstance(obj, (Id)):
            return obj.__info
        if isinstance(obj, (Exchange, AssetType)):
            return obj.name
    # }}}
    @staticmethod  #_decoderJson# {{{
    def _decoderJson(obj):
        # TODO: encoder and decoder - вынести в классы потомки,
        # см формат файлов кэша, там слишком много деталей спецефичных
        # сейчас даты в MOEX файлах после чтения остаются строками:
        # "SETTLEDATE": "2024-05-31"
        # "LASTTRADEDATE": "2025-03-20",
        # "LASTDELDATE": "2025-03-20",
        # "IMTIME": "2024-05-29T18:58:11",
        # возможное решение - при сохранении все эти поля проверять и
        # переводить в UTC datetime
        for k, v in obj.items():
            if k == "exchange":
                obj[k] = Exchange.fromStr(v)
            if k == "type":
                obj[k] = AssetType.fromStr(v)
        return obj
    # }}}
# }}}
