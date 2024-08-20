#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

from __future__ import annotations

import abc
import enum


class DataSource(enum.Enum):  # {{{
    MOEX = 1
    TINKOFF = 2

    @classmethod  # fromStr  # {{{
    def fromStr(cls, string):
        sources = {
            "MOEX": DataSource.MOEX,
            "TINKOFF": DataSource.TINKOFF,
        }
        return sources[string]

    # }}}
    @classmethod  # fromRecord  # {{{
    def fromRecord(cls, record):
        string = record["source"]
        source = cls.fromStr(string)
        return source

    # }}}


# }}}
class _AbstractSource(metaclass=abc.ABCMeta):  # {{{
    @abc.abstractmethod  # __init__# {{{
    def __init__(self): ...

    # }}}
    @abc.abstractmethod  # assets# {{{
    def assets(self, asset_type=None) -> list: ...

    # }}}
    @abc.abstractmethod  # find# {{{
    def find(
        self, exchange: str, asset_type: str, querry: str
    ) -> InstrumentId: ...

    # }}}
    @abc.abstractmethod  # info# {{{
    def info(self, ID: InstrumentId) -> dict: ...

    # }}}
    @abc.abstractmethod  # firstDateTime# {{{
    def firstDateTime(
        self, ID: InstrumentId, data_type: DataType
    ) -> datetime: ...

    # }}}
    @abc.abstractmethod  # download# {{{
    def download(
        self, ID: InstrumentId, data_type: DataType, year: int
    ) -> bool: ...

    # }}}
    @abc.abstractmethod  # export# {{{
    def export(self) -> bool: ...

    # }}}
    @abc.abstractmethod  # clear# {{{
    def clear(self) -> bool: ...

    # }}}
    @abc.abstractmethod  # getHistoricalBars# {{{
    def getHistoricalBars(
        self,
        ID: InstrumentId,
        data_type: DataType,
        begin: datetime,
        end: datetime,
    ) -> list[_Bar]: ...

    # }}}
    @classmethod  # _getStandartAssetType# {{{
    def _getStandartAssetType(cls, name):
        # TODO вот этот метод явно не тут должен быть.
        # или в классе конкретного источника данных, его заморочки с именами
        # или общий в классе AssetType
        names = {
            "index": AssetType.INDEX,
            "shares": AssetType.SHARE,
            "bonds": AssetType.BOND,
            "futures": AssetType.FUTURE,
            "currency": AssetType.CURRENCY,
            "currencies": AssetType.CURRENCY,
            "etfs": AssetType.ETF,
        }
        standart_asset_type = names[name]
        return standart_asset_type

    # }}}
    @classmethod  # _parseFileName# {{{
    def _parseFileName(cls, file_name):
        exchange, asset_type, ticker, data_type, year = file_name.split("-")

        exchange = Exchange.fromStr(exchange)
        asset_type = AssetType.fromStr(asset_type)
        # FIXME а как бы от сюда выпилить вызов фасадного класса..
        # и убрать все эти классы в другие файлы
        ID = Data.find(exchange, asset_type, ticker)

        data_type = DataType.fromStr(data_type)

        return ID, data_type

    # }}}


# }}}
