#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime

from avin.data._bar import _Bar
from avin.data.data_type import DataType
from avin.data.instrument import Instrument


class _AbstractDataSource(ABC):
    @abstractmethod  # __init__# {{{
    def __init__(self): ...

    # }}}
    @classmethod  # abstractmethod cacheAssetsInfo# {{{
    @abstractmethod
    def cacheInstrumentsInfo(cls) -> None: ...

    # }}}
    @classmethod  # abstractmethod find# {{{
    @abstractmethod
    def find(
        cls, exchange: str, asset_type: str, ticker: str, figi: str, name: str
    ) -> list[Instrument]: ...

    # }}}
    @classmethod  # abstractmethod firstDateTime# {{{
    @abstractmethod
    def firstDateTime(
        cls, instrument: Instrument, data_type: DataType
    ) -> datetime: ...

    # }}}
    @classmethod  # abstractmethod download# {{{
    @abstractmethod
    def download(
        cls, instrument: Instrument, data_type: DataType, year: int
    ) -> None: ...

    # }}}
    @classmethod  # abstractmethod getHistoricalBars# {{{
    @abstractmethod
    def getHistoricalBars(
        cls,
        instrument: Instrument,
        data_type: DataType,
        begin: datetime,
        end: datetime,
    ) -> list[_Bar]: ...

    # }}}
