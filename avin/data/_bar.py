#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from avin.data.data_source import DataSource
from avin.keeper import Keeper
from avin.utils import logger


@dataclass  # _Bar# {{{
class _Bar:
    dt: datetime | str
    open: float
    high: float
    low: float
    close: float
    vol: int

    def __post_init__(self):  # {{{
        if isinstance(self.dt, str):
            self.dt = datetime.fromisoformat(self.dt)

    # }}}
    @classmethod  # fromRecord{{{
    def fromRecord(cls, record):
        bar = cls(
            record["dt"],
            record["open"],
            record["high"],
            record["low"],
            record["close"],
            record["volume"],
        )

        return bar

    # }}}


# }}}
class _BarsData:  # {{{
    def __init__(  # {{{
        self,
        ID: InstrumentId,
        data_type: DataType,
        bars: list[_Bar],
        source: Source,
    ):
        self.__ID = ID
        self.__type = data_type
        self.__bars = bars
        self.__source = source

    # }}}
    @property  # ID# {{{
    def ID(self):
        return self.__ID

    # }}}
    @property  # data_type# {{{
    def type(self):
        return self.__type

    # }}}
    @property  # bars# {{{
    def bars(self):
        return self.__bars

    # }}}
    @property  # source# {{{
    def source(self):
        return self.__source

    # }}}
    @property  # first_dt# {{{
    def first_dt(self):
        dt = self.bars[0].dt
        return dt

    # }}}
    @property  # last_dt# {{{
    def last_dt(self):
        dt = self.bars[-1].dt
        return dt

    # }}}
    @classmethod  # save  # {{{
    async def save(cls, data: _BarsData):
        logger.debug(f"{cls.__name__}.save({data.ID.ticker})")
        await Keeper.add(data)

    # }}}
    @classmethod  # load  # {{{
    async def load(
        cls,
        ID: InstrumentId,
        data_type: DataType,
        begin: datetime,
        end: datetime,
    ) -> _BarsData:
        logger.debug(f"{cls.__name__}.load({ID.ticker})")

        # Request source
        source = await Keeper.get(DataSource, ID=ID, data_type=data_type)

        # Request bars
        records = await Keeper.get(
            _Bar, ID=ID, data_type=data_type, begin=begin, end=end
        )

        # Create bars from records
        bars = list()
        for i in records:
            bar = _Bar.fromRecord(i)
            bars.append(bar)

        data = _BarsData(ID, data_type, bars, source)

        return data

    # }}}
    @classmethod  # delete  # {{{
    async def delete(
        cls,
        ID: InstrumentId,
        data_type: DataType,
        begin: int = None,
        end: int = None,
    ) -> _BarsData:
        logger.debug(f"{cls.__name__}.delete()")

        # If begin == end == None, delete all the data
        # fasade class Data do not provide the ability to delete data
        # from (begin-end) period, only all the asset data.
        # In this function, agrs 'begin' 'end' is preserved just in case,
        # it may be needed later. Class Keeper can remove bars from period,
        # if they are defined. And it removes all the bars of a given
        # timeframe if it receive begin=None, end=None.
        await Keeper.delete(
            _Bar, ID=ID, data_type=data_type, begin=begin, end=end
        )

    # }}}


# }}}
