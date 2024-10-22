#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

from __future__ import annotations

import abc


class _AbstractDataSource(metaclass=abc.ABCMeta):  # {{{
    @abc.abstractmethod  # __init__# {{{
    def __init__(self): ...

    # }}}
    @abc.abstractclassmethod  # cacheAssetsInfo# {{{
    def cacheAssetsInfofind(cls) -> None: ...

    # }}}
    @abc.abstractclassmethod  # find# {{{
    def find(
        cls, exchange: str, asset_type: str, querry: str
    ) -> list[InstrumentId]: ...

    # }}}
    @abc.abstractclassmethod  # info# {{{
    def info(cls, ID: InstrumentId) -> dict: ...

    # }}}
    @abc.abstractclassmethod  # firstDateTime# {{{
    def firstDateTime(
        cls, ID: InstrumentId, data_type: DataType
    ) -> datetime: ...

    # }}}
    @abc.abstractclassmethod  # download# {{{
    def download(
        cls, ID: InstrumentId, data_type: DataType, year: int
    ) -> None: ...

    # }}}
    @abc.abstractclassmethod  # getHistoricalBars# {{{
    def getHistoricalBars(
        cls,
        ID: InstrumentId,
        data_type: DataType,
        begin: datetime,
        end: datetime,
    ) -> list[_Bar]: ...

    # }}}


# }}}
