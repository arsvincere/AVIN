#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

from __future__ import annotations

from datetime import UTC, datetime, timedelta

from avin.const import DAY_BEGIN, DAY_END, Usr, WeekDays
from avin.data._data_bar import _Bar, _BarsData
from avin.data._source_moex import _MoexData
from avin.data._source_tinkoff import _TinkoffData
from avin.data.asset_type import AssetType
from avin.data.data_source import DataSource
from avin.data.data_type import DataType
from avin.data.exchange import Exchange
from avin.data.instrument_id import InstrumentId
from avin.keeper import Keeper
from avin.logger import logger
from avin.utils import Cmd, now


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
        check = cls.__checkArgs(
            asset_type=asset_type,
            exchange=exchange,
            ticker=ticker,
            figi=figi,
            name=name,
            source=source,
        )
        if not check:
            return None

        if source == DataSource.MOEX:
            class_ = _MoexData
        elif source == DataSource.TINKOFF:
            class_ = _TinkoffData

        # if source is None,
        # uses _MoexData for indexes,
        # and _TinkoffData otherwise
        elif asset_type == AssetType.INDEX:
            class_ = _MoexData
        else:
            class_ = _TinkoffData

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
            source=source, ID=ID, data_type=data_type, year=year
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
            return False

        if in_type.toTimedelta() > out_type.toTimedelta():
            logger.error(
                f"You're still a stupid monkey, how the fuck do you convert "
                f"'{in_type}' to '{out_type}'?"
            )
            return False

        await _Manager.convert(ID, in_type, out_type)

    # }}}
    @classmethod  # delete# {{{
    async def delete(
        cls,
        ID: InstrumentId,
        data_type: DataType,
    ) -> None:
        logger.debug(f"{cls.__name__}.delete()")
        check = cls.__checkArgs(
            ID=ID,
            data_type=data_type,
        )
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
        check = cls.__checkArgs(
            ID=ID,
            data_type=data_type,
        )
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


class _Manager:  # {{{
    _DATA_DIR = Usr.DATA
    _AUTO_UPDATE = Usr.AUTO_UPDATE_MARKET_DATA
    _LAST_UPDATE_FILE = Cmd.path(_DATA_DIR, "last_update")
    _DATA_IS_UP_TO_DATE = None

    class VoidBar:  # {{{
        """doc# {{{
        Utility class for data conversion
        """

        # }}}
        def __init__(self, dt: datetime):  # {{{
            self.dt = dt

        # }}}

    # }}}

    def __init__(self):  # {{{
        if _Manager._AUTO_UPDATE:
            self.__checkUpdate()

    # }}}
    @classmethod  # cacheAssetsInfo  # {{{
    async def cacheAssetsInfo(cls) -> None:
        logger.info(":: Start caching assets info")
        for i in DataSource:
            class_ = cls.__getDataSourceClass(i)
            await class_.cacheAssetsInfo()
        logger.info("Cache is up to date")

    # }}}
    @classmethod  # firstDateTime{{{
    async def firstDateTime(cls, source, ID, data_type) -> datetime:
        logger.debug(f"{cls.__name__}.firstDateTime()")
        class_ = cls.__getDataSourceClass(source)
        dt = await class_.firstDateTime(ID, data_type)
        return dt

    # }}}
    @classmethod  # download{{{
    async def download(cls, ID, data_type, year) -> None:
        logger.debug(f"{cls.__name__}.download()")
        # NOTE
        # пока грузим все исторические данные только с MOEX
        # независимо ни от чего
        await _MoexData.download(ID, data_type, year)

    # }}}
    @classmethod  # convert# {{{
    async def convert(
        cls, ID: InstrumentId, in_type: DataType, out_type: DataType
    ) -> None:
        logger.info(
            f":: Convert {ID.ticker}-{in_type.value} -> {out_type.value}"
        )
        converter = cls.__choseConverter(out_type)

        # load 'in' data
        # TODO: ну не надо же все подряд конвертить...
        # Надо сначала проверить какие данные уже
        # сконвертированы и есть ли они
        # и доставать не все пачкой а по годам
        # пока сделаю закладку begin end на будущее
        in_data = await _BarsData.load(ID, in_type, begin=None, end=None)

        # convert bars
        out_bars = converter(in_data.bars, in_type, out_type)

        # save converted data
        converted_data = _BarsData(ID, out_type, out_bars, in_data.source)
        await _BarsData.save(converted_data)

    # }}}
    @classmethod  # delete# {{{
    async def delete(
        cls,
        ID: InstrumentId,
        data_type: DataType,
    ) -> None:
        logger.info(f":: Delete {ID.ticker}-{data_type.value}")
        await _BarsData.delete(ID, data_type)
        logger.info("  - complete")

    # }}}
    @classmethod  # update{{{
    async def update(cls, ID: InstrumentId, data_type: DataType) -> None:
        logger.debug(f"{cls.__name__}.update()")
        # request info about availible data
        records = await Keeper.get(Data, ID=ID, data_type=data_type)
        assert len(records) == 1
        record = records[0]
        await cls.__update(record)

    # }}}
    @classmethod  # updateAll{{{
    async def updateAll(cls) -> None:
        logger.info(":: Update all market data")

        records = await Keeper.get(Data)
        for record in records:
            await cls.__update(record)

    # }}}
    @classmethod  # request# {{{
    async def request(
        cls,
        ID: InstrumentId,
        data_type: DataType,
        begin: datetime,
        end: datetime,
    ) -> list:
        logger.debug(f"{cls.__name__}.request()")
        if cls._AUTO_UPDATE and not cls._DATA_IS_UP_TO_DATE:
            cls.__checkUpdate()

        records = await Keeper.get(
            _Bar, ID=ID, data_type=data_type, begin=begin, end=end
        )
        return records

    # }}}
    @classmethod  # __getDataSourceClass# {{{
    def __getDataSourceClass(cls, source: DataSource) -> object:
        logger.debug(f"{cls.__name__}.__getDataSourceClass()")
        classes = {
            DataSource.MOEX: _MoexData,
            DataSource.TINKOFF: _TinkoffData,
        }
        class_ = classes.get(source)
        return class_

    # }}}
    @classmethod  # __checkUpdate# {{{
    def __checkUpdate(cls):
        logger.debug(f"{cls.__name__}.__checkUpdate()")
        # Check the file with the date of the last update of the market data
        if Cmd.isExist(cls._LAST_UPDATE_FILE):
            string = Cmd.read(cls._LAST_UPDATE_FILE)
            last_update = datetime.fromisoformat(string)
            if now().date() == last_update.date():
                cls._DATA_IS_UP_TO_DATE = True
                return

        # update all availible market data
        logger.info(":: Auto update market data")
        cls.updateAll()
        cls._DATA_IS_UP_TO_DATE = True

        # save last update datetime
        dt = now().isoformat()
        Cmd.write(dt, cls._LAST_UPDATE_FILE)
        logger.info("Update complete")

    # }}}
    @classmethod  # __fillVoid# {{{
    def __fillVoid(cls, bars: list[_Bar], data_type: DataType) -> list[_Bar]:
        logger.debug(f"{cls.__name__}.__fillVoid()")
        time = datetime.combine(bars[0].dt.date(), DAY_BEGIN)
        end = datetime.combine(bars[-1].dt.date(), DAY_END)
        step = data_type.toTimedelta()
        filled = list()
        i = 0
        while time <= end:
            if i < len(bars) and time == bars[i].dt:
                filled.append(bars[i])
                i += 1
            else:
                filled.append(_Manager.VoidBar(time))
            time += step
        return filled

    # }}}
    @classmethod  # __removeVoid# {{{
    def __removeVoid(cls, bars: list) -> list:
        logger.debug(f"{cls.__name__}.__removeVoid()")
        i = 0
        while i < len(bars):
            if isinstance(bars[i], _Manager.VoidBar):
                bars.pop(i)
            else:
                i += 1
        return bars

    # }}}
    @classmethod  # __choseConverter# {{{
    def __choseConverter(cls, out_type: DataType) -> Callable:
        logger.debug(f"{cls.__name__}.__choseConverter()")
        if out_type.toTimedelta() <= timedelta(days=1):
            conv = cls.__convertSmallTimeFrame
        elif out_type.value == "W":
            conv = cls.__convertWeekTimeFrame
        elif out_type.value == "M":
            conv = cls.__convertMonthTimeFrame
        return conv

    # }}}
    @classmethod  # __convertSmallTimeFrame# {{{
    def __convertSmallTimeFrame(cls, bars, in_type, out_type):
        logger.debug(f"{cls.__name__}.__convertSmallTimeFrame()")
        bars = cls.__fillVoid(bars, in_type)
        period = out_type.toTimedelta()
        i = 0
        converted = list()
        while i < len(bars):
            first = i
            last = i
            while last < len(bars):
                time_dif = bars[last].dt - bars[first].dt
                if time_dif < period:
                    last += 1
                else:
                    break
            new_bar = cls.__join(bars[first:last])
            if new_bar is not None:
                converted.append(new_bar)
            i = last
        return converted

    # }}}
    @classmethod  # __convertWeekTimeFrame# {{{
    def __convertWeekTimeFrame(cls, bars, in_type, out_type):
        logger.debug(f"{cls.__name__}.__convertWeekTimeFrame()")
        assert in_type.toTimedelta() == timedelta(days=1)
        bars = cls.__fillVoid(bars, in_type)
        first = 0
        last = 0
        converted = list()
        while last < len(bars):
            while last < len(bars):
                if bars[last].dt.weekday() == WeekDays.Mon.value:
                    break
                else:
                    last += 1
            new_bar = cls.__join(bars[first:last])
            if new_bar is not None:
                converted.append(new_bar)
            first = last
            last += 1
        return converted

    # }}}
    @classmethod  # __convertMonthTimeFrame# {{{
    def __convertMonthTimeFrame(cls, bars, in_type, out_type):
        logger.debug(f"{cls.__name__}.__convertMonthTimeFrame()")
        assert in_type.toTimedelta() == timedelta(days=1)
        bars = cls.__fillVoid(bars, in_type)
        first = 0
        last = 0
        converted = list()
        while last < len(bars):
            while last < len(bars):
                if bars[last].dt.day == 1:
                    break
                last += 1
            new_bar = cls.__join(bars[first:last])
            if new_bar is not None:
                converted.append(new_bar)
            first = last
            last += 1
        return converted

    # }}}
    @classmethod  # __join# {{{
    def __join(cls, bars):
        """
        Возвращает объединенный bar из bars, игнорируюя VoidBar
        Если все бары VoidBar, возвращает None
        """
        logger.debug(f"{cls.__name__}.__convertMonthTimeFrame()")

        if len(bars) == 0:
            return None

        dt_first_bar = bars[0].dt  # join_bar.dt == first bar dt
        bars = cls.__removeVoid(bars)

        # join
        if len(bars) > 0:
            opn = bars[0].open
            hgh = max([bar.high for bar in bars])
            low = min([bar.low for bar in bars])
            close = bars[-1].close
            volume = sum([bar.vol for bar in bars])
            join_bar = _Bar(dt_first_bar, opn, hgh, low, close, volume)
            return join_bar

        return None  # возвращаем None, если не было баров с данными

    # }}}
    @classmethod  # __update  # {{{
    async def __update(cls, record):
        logger.debug(f"{cls.__name__}.__update()")

        # parse record
        ID = await InstrumentId.byFigi(record["figi"])
        data_type = DataType.fromRecord(record)
        source = DataSource.fromRecord(record)
        source_class = cls.__getDataSourceClass(source)
        last_dt = record["last_dt"]
        logger.info(f"Updating {ID.ticker}-{data_type.value}")

        # request new bars
        begin = last_dt + data_type.toTimedelta()
        end = now().replace(microsecond=0)
        new_bars = await source_class.getHistoricalBars(
            ID, data_type, begin, end
        )

        # check: is new bars found
        count = len(new_bars)
        if count == 0:
            logger.info("  - no new bars")
            return

        # save new bars
        logger.info(f"  - received {count} bars -> {new_bars[-1].dt}")
        new_data = _BarsData(ID, data_type, new_bars, source)
        await _BarsData.save(new_data)

    # }}}


# }}}
