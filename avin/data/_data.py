#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

from __future__ import annotations

from datetime import UTC, datetime
from typing import Optional

from avin.data._data_manager import _DataManager
from avin.data.data_info import DataInfo
from avin.data.data_source import DataSource
from avin.data.data_type import DataType
from avin.data.exchange import Exchange
from avin.data.instrument import Instrument
from avin.utils import logger


class Data:
    @classmethod  # cache  # {{{
    async def cache(cls) -> None:
        """Make cache of instruments info"""

        logger.debug(f"{cls.__name__}.cache()")

        await _DataManager.cacheInstrumentsInfo()

    # }}}
    @classmethod  # find  # {{{
    async def find(
        cls,
        exchange: Optional[Exchange] = None,
        itype: Optional[Instrument.Type] = None,
        ticker: Optional[str] = None,
        figi: Optional[str] = None,
        name: Optional[str] = None,
        source: Optional[DataSource] = None,
    ) -> list[Instrument]:
        """Find instrument"""

        logger.debug(f"{cls.__name__}.find()")

        # check args
        check = cls.__checkArgs(
            exchange=exchange,
            itype=itype,
            ticker=ticker,
            figi=figi,
            name=name,
            source=source,
        )
        if not check:
            return list()

        instr_list = await _DataManager.find(
            exchange, itype, ticker, figi, name, source
        )
        return instr_list

    # }}}
    @classmethod  # info  # {{{
    async def info(
        cls,
        instrument: Optional[Instrument] = None,
        data_type: Optional[DataType] = None,
    ) -> DataInfo | None:
        logger.debug(f"{cls.__name__}.info()")

        check = cls.__checkArgs(
            instrument=instrument,
            data_type=data_type,
        )
        if not check:
            return None

        info = await _DataManager.info(instrument, data_type)
        return info

    # }}}
    @classmethod  # firstDateTime  # {{{
    async def firstDateTime(
        cls, source: DataSource, instrument: Instrument, data_type: DataType
    ) -> datetime | None:
        logger.debug(f"{cls.__name__}.firstDateTime()")

        check = cls.__checkArgs(
            source=source,
            instrument=instrument,
            data_type=data_type,
        )
        if not check:
            return None

        if data_type.value not in ["1M", "D"]:
            logger.error("First datetime availible only for '1M' and 'D'")
            return None

        dt = await _DataManager.firstDateTime(source, instrument, data_type)
        return dt

    # }}}
    @classmethod  # download  # {{{
    async def download(
        cls,
        source: DataSource,
        instrument: Instrument,
        data_type: DataType,
        year: int,
    ) -> None:
        logger.debug(f"{cls.__name__}.download()")

        check = cls.__checkArgs(
            source=source,
            instrument=instrument,
            data_type=data_type,
            year=year,
        )
        if not check:
            return

        await _DataManager.download(source, instrument, data_type, year)

    # }}}
    @classmethod  # convert  # {{{
    async def convert(
        cls, instrument: Instrument, in_type: DataType, out_type: DataType
    ) -> None:
        logger.debug(f"{cls.__name__}.convert()")

        check = cls.__checkArgs(
            instrument=instrument,
            in_type=in_type,
            out_type=out_type,
        )
        if not check:
            return

        await _DataManager.convert(instrument, in_type, out_type)

    # }}}
    @classmethod  # delete  # {{{
    async def delete(
        cls,
        instrument: Instrument,
        data_type: DataType,
        begin: Optional[datetime] = None,
        end: Optional[datetime] = None,
    ) -> None:
        logger.debug(f"{cls.__name__}.delete()")

        check = cls.__checkArgs(
            instrument=instrument,
            data_type=data_type,
            begin=begin,
            end=end,
        )
        if not check:
            return

        if data_type == DataType.BOOK or data_type == DataType.TIC:
            assert False

        await _DataManager.delete(instrument, data_type, begin, end)

    # }}}
    @classmethod  # update  # {{{
    async def update(
        cls, instrument: Instrument, data_type: Optional[DataType] = None
    ) -> None:
        logger.debug(f"{cls.__name__}.update()")
        assert instrument.exchange == Exchange.MOEX
        assert data_type != DataType.TIC
        assert data_type != DataType.BOOK

        check = cls.__checkArgs(instrument=instrument, data_type=data_type)
        if not check:
            return

        await _DataManager.update(instrument, data_type)

    # }}}
    @classmethod  # updateAll  # {{{
    async def updateAll(cls) -> None:
        logger.debug(f"{cls.__name__}.updateAll()")

        await _DataManager.updateAll()

    # }}}
    @classmethod  # request  # {{{
    async def request(
        cls,
        instrument: Instrument,
        data_type: DataType,
        begin: datetime,
        end: datetime,
    ) -> list[asyncpg.Record]:
        logger.debug(f"{cls.__name__}.request()")

        check = cls.__checkArgs(
            instrument=instrument,
            data_type=data_type,
            begin=begin,
            end=end,
        )
        if not check:
            return list()

        if data_type == DataType.BOOK or data_type == DataType.TIC:
            assert False

        records = await _DataManager.request(
            instrument, data_type, begin, end
        )
        return records

    # }}}
    @classmethod  # __checkArgs  # {{{
    def __checkArgs(
        cls,
        source=None,
        itype=None,
        exchange=None,
        ticker=None,
        figi=None,
        name=None,
        instrument=None,
        data_type=None,
        year=None,
        in_type=None,
        out_type=None,
        begin=None,
        end=None,
    ):
        logger.debug(f"{cls.__name__}.__checkArgs()")

        if source:
            cls.__checkDataSource(source)
        if exchange:
            cls.__checkExchange(exchange)
        if itype:
            cls.__checkInstrumentType(itype)
        if ticker:
            cls.__checkTicker(ticker)
        if figi:
            cls.__checkFigi(figi)
        if name:
            cls.__checkName(name)
        if instrument:
            cls.__checkInstrument(instrument)
        if data_type:
            cls.__checkDataType(data_type)
        if year:
            cls.__checkYear(year)
        if in_type and out_type:
            cls.__checkInOutDataType(in_type, out_type)
        if begin and end:
            cls.__checkBeginEnd(begin, end)

        return True

    # }}}
    @classmethod  # __checkDataSource# {{{
    def __checkDataSource(cls, source):
        logger.debug(f"{cls.__name__}.__checkDataSource()")

        if not isinstance(source, DataSource):
            raise TypeError(
                "You stupid monkey, select the 'source' from the enum "
                "DataSource."
            )

    # }}}
    @classmethod  # __checkExchange  # {{{
    def __checkExchange(cls, exchange):
        logger.debug(f"{cls.__name__}.__checkExchange()")

        if not hasattr(exchange, "name"):
            raise TypeError(
                "You stupid monkey, select the 'exchange' "
                "from the subclasses of class Exchange"
            )

    # }}}
    @classmethod  # __checkInstrumentType  # {{{
    def __checkInstrumentType(cls, itype):
        logger.debug(f"{cls.__name__}.__checkInstrumentType()")

        if not isinstance(itype, Instrument.Type):
            raise TypeError(
                "You stupid monkey, select the 'itype' from the enum "
                "Instrument.Type."
            )

    # }}}
    @classmethod  # __checkTicker  # {{{
    def __checkTicker(cls, ticker):
        logger.debug(f"{cls.__name__}.__checkTicker()")

        if not isinstance(ticker, str):
            raise TypeError(
                "You stupid monkey, use type str for argument 'ticker'"
            )

    # }}}
    @classmethod  # __checkFigi  # {{{
    def __checkFigi(cls, figi):
        logger.debug(f"{cls.__name__}.__checkFigi()")

        if not isinstance(figi, str):
            raise TypeError(
                "You stupid monkey, use type str for argument 'figi'"
            )

    # }}}
    @classmethod  # __checkName  # {{{
    def __checkName(cls, name):
        logger.debug(f"{cls.__name__}.__checkName()")

        if not isinstance(name, str):
            raise TypeError(
                "You stupid monkey, use type str for argument 'name'"
            )

    # }}}
    @classmethod  # __checkInstrument  # {{{
    def __checkInstrument(cls, instrument):
        logger.debug(f"{cls.__name__}.__checkInstrument()")

        if not isinstance(instrument, Instrument):
            raise TypeError(
                "You stupid monkey, use type Instrument "
                "for argument 'instrument'"
            )

    # }}}
    @classmethod  # __checkDataType  # {{{
    def __checkDataType(cls, data_type):
        logger.debug(f"{cls.__name__}.__checkDataType()")

        assert data_type != DataType.BOOK
        assert data_type != DataType.TIC
        if not isinstance(data_type, DataType):
            raise TypeError(
                "You stupid monkey, select the 'data_type' from the enum "
                "DataType."
            )

    # }}}
    @classmethod  # __checkYear  # {{{
    def __checkYear(cls, year):
        logger.debug(f"{cls.__name__}.__checkYear()")

        if not isinstance(year, int):
            raise TypeError(
                "You stupid monkey, use type int for argument 'year'"
            )

    # }}}
    @classmethod  # __checkInOutDataType  # {{{
    def __checkInOutDataType(cls, in_type, out_type):
        logger.debug(f"{cls.__name__}.__checkInOutDataType()")

        assert in_type != DataType.BOOK
        assert in_type != DataType.TIC
        assert out_type != DataType.BOOK
        assert out_type != DataType.TIC
        if not isinstance(in_type, DataType):
            raise TypeError(
                "You stupid monkey, select the 'in_type' from the enum "
                "DataType."
            )
        if not isinstance(out_type, DataType):
            raise TypeError(
                "You stupid monkey, select the 'out_type' from the enum "
                "DataType."
            )

        if in_type.toTimeDelta() >= out_type.toTimeDelta():
            raise ValueError(
                f"You're still stupid monkey, how the fuck you want to "
                f"convert {in_type} -> {out_type} ???"
            )

    # }}}
    @classmethod  # __checkBeginEnd  # {{{
    def __checkBeginEnd(cls, begin: datetime, end: datetime):
        logger.debug(f"{cls.__name__}.__checkBeginEnd()")

        if not isinstance(begin, datetime):
            raise TypeError(
                "You stupid monkey, use type <datetime> for argument 'begin'"
            )
        if not isinstance(end, datetime):
            raise TypeError(
                "You stupid monkey, use type <datetime> for argument 'end'"
            )
        if begin > end:
            raise ValueError(
                f"You're still a stupid monkey, how the fuck you want "
                f"from '{begin}' to '{end}'?"
            )
        assert begin.tzinfo == UTC
        assert end.tzinfo == UTC

    # }}}


if __name__ == "__main__":
    ...
