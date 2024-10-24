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
from typing import Optional

from avin.config import Usr
from avin.data.data_source import DataSource
from avin.data.data_type import DataType
from avin.data.instrument import Instrument
from avin.keeper import Keeper
from avin.utils import logger


@dataclass  # _Bar# {{{
class _Bar:
    dt: datetime
    open: float
    high: float
    low: float
    close: float
    vol: int

    def __str__(self):  # {{{
        usr_dt = self.dt + Usr.TIME_DIF
        str_dt = usr_dt.strftime("%Y-%m-%d %H:%M")
        string = (
            f"Bar {str_dt} O={self.open} H={self.high} "
            f"L={self.low} C={self.close} V={self.vol} "
        )
        return string

    # }}}
    @classmethod  # fromRecord{{{
    def fromRecord(cls, record: asyncpg.Record):
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
        source: DataSource,
        instrument: Instrument,
        data_type: DataType,
        bars: list[_Bar],
    ):
        self.__source = source
        self.__instrument = instrument
        self.__type = data_type
        self.__bars = bars

    # }}}
    @property  # source# {{{
    def source(self):
        return self.__source

    # }}}
    @property  # type# {{{
    def type(self):
        return self.__type

    # }}}
    @property  # instrument# {{{
    def instrument(self):
        return self.__instrument

    # }}}
    @property  # bars# {{{
    def bars(self):
        return self.__bars

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
        logger.debug(f"{cls.__name__}.save({data.instrument.ticker})")

        await Keeper.add(data)

    # }}}
    @classmethod  # load  # {{{
    async def load(
        cls,
        instrument: Instrument,
        data_type: DataType,
        begin: datetime,
        end: datetime,
    ) -> _BarsData:
        logger.debug(f"{cls.__name__}.load({instrument.ticker})")

        # Request source
        source = await Keeper.get(
            DataSource, instrument=instrument, data_type=data_type
        )

        # Request bars
        records = await Keeper.get(
            _Bar,
            instrument=instrument,
            data_type=data_type,
            begin=begin,
            end=end,
        )

        # Create bars from records
        bars = list()
        for i in records:
            bar = _Bar.fromRecord(i)
            bars.append(bar)

        # Create & return _BarsData object
        data = _BarsData(source, data_type, instrument, bars)
        return data

    # }}}
    @classmethod  # delete  # {{{
    async def delete(
        cls,
        instrument: Instrument,
        data_type: DataType,
        begin: Optional[int] = None,
        end: Optional[int] = None,
    ) -> None:
        logger.debug(f"{cls.__name__}.delete()")

        # Class Keeper can remove bars from period, if they are defined.
        # And it removes all the bars of a given
        # timeframe if it receive begin=None, end=None.
        await Keeper.delete(
            _BarsData,
            instrument=instrument,
            data_type=data_type,
            begin=begin,
            end=end,
        )

    # }}}


# }}}
