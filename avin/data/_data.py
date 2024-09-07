#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

from __future__ import annotations

from datetime import UTC, datetime

from avin.data._manager import _Manager
from avin.data._moex import _MoexData
from avin.data._tinkoff import _TinkoffData
from avin.data.asset_type import AssetType
from avin.data.data_source import DataSource
from avin.data.data_type import DataType
from avin.data.exchange import Exchange
from avin.data.instrument_id import InstrumentId
from avin.utils import logger


class Data:  # {{{
    @classmethod  # cache# {{{
    async def cache(cls) -> None:
        """Make cache of assets info"""

        logger.debug(f"{cls.__name__}.cache()")
        await _Manager.cacheAssetsInfo()

    # }}}
    @classmethod  # find# {{{
    async def find(
        cls,
        asset_type: AssetType = None,
        exchange: Exchange = None,
        ticker: str = None,
        figi: str = None,
        name: str = None,
        source: DataSource = None,
    ) -> list[InstrumentId]:
        """Find instrument id

        Args:
            asset_type - ...
        """
        logger.debug(f"{cls.__name__}.find()")

        # check args
        check = cls.__checkArgs(
            asset_type=asset_type,
            exchange=exchange,
            ticker=ticker,
            figi=figi,
            name=name,
            source=source,
        )
        if not check:
            return

        # select data source
        if source == DataSource.MOEX:
            class_ = _MoexData
        elif source == DataSource.TINKOFF:
            class_ = _TinkoffData
        # if source is None,
        # uses _MoexData for indexes, and _TinkoffData otherwise
        elif asset_type == AssetType.INDEX:
            class_ = _MoexData
        else:
            class_ = _TinkoffData

        # find instrument IDs
        id_list = await class_.find(asset_type, exchange, ticker, figi, name)
        return id_list

    # }}}
    @classmethod  # info# {{{
    async def info(cls, ID: InstrumentId) -> dict:
        logger.debug(f"{cls.__name__}.info()")
        check = cls.__checkArgs(ID=ID)
        if not check:
            return None

        class_ = _MoexData if ID.type == AssetType.INDEX else _TinkoffData
        info = await class_.info(ID)
        return info

    # }}}
    @classmethod  # firstDateTime# {{{
    async def firstDateTime(
        cls, source: DataSource, data_type: DataType, ID: InstrumentId
    ) -> datetime:
        logger.debug(f"{cls.__name__}.firstDateTime()")
        check = cls.__checkArgs(
            source=source,
            ID=ID,
            data_type=data_type,
        )
        if not check:
            return None

        if data_type.value not in ["1M", "D"]:
            logger.error("First datetime availible only for '1M' and 'D'")
            return None

        dt = await _Manager.firstDateTime(source, ID, data_type)
        return dt

    # }}}
    @classmethod  # download# {{{
    async def download(
        cls,
        source: DataSource,
        data_type: DataType,
        ID: InstrumentId,
        year: int,
    ) -> None:
        logger.debug(f"{cls.__name__}.download()")

        check = cls.__checkArgs(
            source=source,
            ID=ID,
            data_type=data_type,
            year=year,
        )
        if not check:
            return

        await _Manager.download(ID, data_type, year)

    # }}}
    @classmethod  # convert# {{{
    async def convert(
        cls, ID: InstrumentId, in_type: DataType, out_type: DataType
    ) -> None:
        logger.debug(f"{cls.__name__}.convert()")

        check = cls.__checkArgs(ID=ID, in_type=in_type, out_type=out_type)
        if not check:
            return

        if in_type.toTimeDelta() > out_type.toTimeDelta():
            logger.error(
                f"You're still a stupid monkey, how the fuck do you convert "
                f"'{in_type}' to '{out_type}'?"
            )
            return

        await _Manager.convert(ID, in_type, out_type)

    # }}}
    @classmethod  # delete# {{{
    async def delete(
        cls,
        ID: InstrumentId,
        data_type: DataType,
    ) -> None:
        logger.debug(f"{cls.__name__}.delete()")

        check = cls.__checkArgs(ID=ID, data_type=data_type)
        if not check:
            return

        if data_type == DataType.BOOK or data_type == DataType.TIC:
            assert False

        await _Manager.delete(ID, data_type)

    # }}}
    @classmethod  # update# {{{
    async def update(
        cls, ID: InstrumentId, data_type: DataType = None
    ) -> None:
        logger.debug(f"{cls.__name__}.update()")
        assert ID.exchange == Exchange.MOEX
        assert data_type != DataType.TIC
        assert data_type != DataType.BOOK

        check = cls.__checkArgs(ID=ID, data_type=data_type)
        if not check:
            return

        await _Manager.update(ID, data_type)

    # }}}
    @classmethod  # updateAll# {{{
    async def updateAll(cls) -> None:
        logger.debug(f"{cls.__name__}.updateAll()")
        await _Manager.updateAll()

    # }}}
    @classmethod  # request# {{{
    async def request(
        cls,
        ID: InstrumentId,
        data_type: DataType,
        begin: datetime,
        end: datetime,
    ) -> list[Record]:
        logger.debug(f"{cls.__name__}.request()")
        check = cls.__checkArgs(
            ID=ID,
            data_type=data_type,
            begin=begin,
            end=end,
        )
        if not check:
            return

        if data_type == DataType.BOOK or data_type == DataType.TIC:
            assert False

        records = await _Manager.request(ID, data_type, begin, end)
        return records

    # }}}
    @classmethod  # __checkArgs# {{{
    def __checkArgs(
        cls,
        source=None,
        asset_type=None,
        exchange=None,
        ticker=None,
        figi=None,
        name=None,
        ID=None,
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
        if asset_type:
            cls.__checkAssetType(asset_type)
        if ticker:
            cls.__checkTicker(ticker)
        if figi:
            cls.__checkFigi(figi)
        if name:
            cls.__checkName(name)
        if ID:
            cls.__checkID(ID)
        if data_type:
            cls.__checkDataType(data_type)
        if year:
            cls.__checkYear(year)
        if in_type and out_type:
            cls.__checkIOType(in_type, out_type)
        if begin and end:
            cls.__checkBeginEnd(begin, end)
        return True

    # }}}
    @classmethod  # __checkDataSource# {{{
    def __checkDataSource(cls, source):
        if not isinstance(source, DataSource):
            raise TypeError(
                "You stupid monkey, select the 'source' from the enum "
                "DataSource."
            )

    # }}}
    @classmethod  # __checkExchange# {{{
    def __checkExchange(cls, exchange):
        # if not isinstance(exchange, Exchange):
        #     raise TypeError(
        #         "You stupid monkey, select the 'exchange' from the enum "
        #         "Exchange."
        #         )
        ...

    # }}}
    @classmethod  # __checkAssetType# {{{
    def __checkAssetType(cls, asset_type):
        if not isinstance(asset_type, AssetType):
            raise TypeError(
                "You stupid monkey, select the 'asset_type' from the enum "
                "AssetType."
            )

    # }}}
    @classmethod  # __checkTicker# {{{
    def __checkTicker(cls, ticker):
        if not isinstance(ticker, str):
            raise TypeError(
                "You stupid monkey, use type str for argument 'ticker'"
            )

    # }}}
    @classmethod  # __checkFigi# {{{
    def __checkFigi(cls, figi):
        if not isinstance(figi, str):
            raise TypeError(
                "You stupid monkey, use type str for argument 'figi'"
            )

    # }}}
    @classmethod  # __checkName# {{{
    def __checkName(cls, name):
        if not isinstance(name, str):
            raise TypeError(
                "You stupid monkey, use type str for argument 'name'"
            )

    # }}}
    @classmethod  # __checkID# {{{
    def __checkID(cls, ID):
        if not isinstance(ID, InstrumentId):
            raise TypeError(
                "You stupid monkey, use type InstrumentId for argument 'ID'"
            )

    # }}}
    @classmethod  # __checkDataType# {{{
    def __checkDataType(cls, data_type):
        assert data_type != DataType.BOOK
        assert data_type != DataType.TIC
        if not isinstance(data_type, DataType):
            raise TypeError(
                "You stupid monkey, select the 'data_type' from the enum "
                "DataType."
            )

    # }}}
    @classmethod  # __checkYear# {{{
    def __checkYear(cls, year):
        if not isinstance(year, int):
            raise TypeError(
                "You stupid monkey, use type int for argument 'year'"
            )

    # }}}
    @classmethod  # __checkIOType# {{{
    def __checkIOType(cls, in_type, out_type):
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

    # }}}
    @classmethod  # __checkBeginEnd# {{{
    def __checkBeginEnd(cls, begin: datetime, end: datetime):
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
                f"You're still a stupid monkey, how the fuck you to get data "
                f"data from '{begin}' to '{end}'?"
            )
        assert begin.tzinfo == UTC
        assert end.tzinfo == UTC

    # }}}


# }}}
