#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

from __future__ import annotations

from datetime import UTC, date, datetime, timedelta

from avin.config import Auto, Usr
from avin.const import DAY_BEGIN, DAY_END, WeekDays
from avin.data._bar import _Bar, _BarsData
from avin.data._moex import _MoexData
from avin.data._tinkoff import _TinkoffData
from avin.data.convert import ConvertTaskList
from avin.data.data_info import DataInfo, DataInfoNode
from avin.data.data_source import DataSource
from avin.data.data_type import DataType
from avin.data.instrument import Instrument
from avin.keeper import Keeper
from avin.utils import Cmd, logger, now


class _DataManager:
    __AUTO_UPDATE = Auto.UPDATE_MARKET_DATA
    __LAST_UPDATE_FILE = Cmd.path(Usr.DATA, "last_update")
    __DATA_IS_UP_TO_DATE = None

    class VoidBar:  # {{{
        """Utility class for data conversion"""

        def __init__(self, dt: datetime):  # {{{
            self.dt = dt

        # }}}

    # }}}

    @classmethod  # cacheInstrumentsInfo  # {{{
    async def cacheInstrumentsInfo(cls) -> None:
        logger.info(":: Start caching assets info")

        for i in DataSource:
            if i == DataSource.CONVERT:
                continue

            class_ = cls.__getDataSourceClass(i)
            await class_.cacheInstrumentsInfo()

        logger.info("Cache is up to date")

    # }}}
    @classmethod  # find  # {{{
    async def find(
        cls, exchange, itype, ticker, figi, name, source
    ) -> list[Instrument]:
        logger.debug(f"{cls.__name__}.find()")
        logger.info(f":: Find instruments {source} {itype}")

        if source == DataSource.MOEX:
            class_ = _MoexData
        elif source == DataSource.TINKOFF:
            class_ = _TinkoffData
        # if source is None,
        # uses _MoexData for indexes, and _TinkoffData otherwise
        elif itype == Instrument.Type.INDEX:
            class_ = _MoexData
        else:
            class_ = _TinkoffData

        # find instrument
        id_list = await class_.find(exchange, itype, ticker, figi, name)

        logger.info(f"Finded {len(id_list)} instruments!")

        return id_list

    # }}}
    @classmethod  # info  # {{{
    async def info(cls, instr, data_type) -> DataInfo:
        logger.debug(f"{cls.__name__}.download()")

        info = await DataInfo.load(instr, data_type)
        return info

    # }}}
    @classmethod  # firstDateTime  # {{{
    async def firstDateTime(cls, source, instr, data_type) -> datetime:
        logger.debug(f"{cls.__name__}.firstDateTime()")

        class_ = cls.__getDataSourceClass(source)
        dt = await class_.firstDateTime(instr, data_type)
        return dt

    # }}}
    @classmethod  # download  # {{{
    async def download(cls, source, instr, data_type, year) -> None:
        logger.debug(f"{cls.__name__}.download()")
        # NOTE:
        # пока грузим все исторические данные только с MOEX
        # независимо от переменной 'source'
        await _MoexData.download(instr, data_type, year)

    # }}}
    @classmethod  # convert  # {{{
    async def convert(cls, instr, in_type, out_type) -> None:
        logger.debug(f"{cls.__name__}.convert()")
        logger.info(f":: Convert {instr.ticker}-{in_type} -> {out_type}")

        # check availible converted data
        data_info = await DataInfoNode.load(instr, out_type)
        if not data_info:
            begin = None  # select from first availible
            end = datetime.combine(date.today(), DAY_BEGIN, UTC)  # to today
        else:
            begin = data_info.last_dt  # select from last converted
            end = datetime.combine(date.today(), DAY_BEGIN, UTC)  # to today

        # load in_type data
        in_data = await _BarsData.load(instr, in_type, begin, end)

        # convert bars
        converter = cls.__choseConverter(out_type)
        out_bars = converter(in_data.bars, in_type, out_type)

        # save converted data
        converted_data = _BarsData(
            DataSource.CONVERT, instr, out_type, out_bars
        )
        await _BarsData.save(converted_data)

    # }}}
    @classmethod  # delete  # {{{
    async def delete(
        cls,
        instr: Instrument,
        data_type: DataType,
        begin: Optional[datetime] = None,
        end: Optional[datetime] = None,
    ) -> None:
        logger.info(f":: Delete {instr.ticker}-{data_type.value}")

        await _BarsData.delete(instr, data_type, begin, end)
        logger.info("  - complete")

    # }}}
    @classmethod  # update  # {{{
    async def update(cls, instr, data_type) -> None:
        logger.debug(f"{cls.__name__}.update()")

        node = await DataInfoNode.load(instr, data_type)
        await cls.__update(node)

    # }}}
    @classmethod  # updateAll  # {{{
    async def updateAll(cls) -> None:
        logger.info(":: Update all market data")

        # update
        data_info = await DataInfo.load()  # load all
        for node in data_info:
            await cls.__update(node)

        # convert timeframes
        if not Auto.CONVERT_MARKET_DATA:
            return

        clist = await ConvertTaskList.load("convert_list")
        for task in clist:
            await cls.convert(task.instrument, task.in_type, task.out_type)

    # }}}
    @classmethod  # request  # {{{
    async def request(
        cls,
        instr: Instrument,
        data_type: DataType,
        begin: datetime,
        end: datetime,
    ) -> list:
        logger.debug(f"{cls.__name__}.request()")

        if cls.__AUTO_UPDATE and not cls.__DATA_IS_UP_TO_DATE:
            await cls.__checkUpdate()

        records = await Keeper.get(
            _Bar, instrument=instr, data_type=data_type, begin=begin, end=end
        )

        return records

    # }}}
    @classmethod  # __getDataSourceClass  # {{{
    def __getDataSourceClass(cls, source: DataSource) -> object:
        logger.debug(f"{cls.__name__}.__getDataSourceClass()")

        classes = {
            DataSource.MOEX: _MoexData,
            DataSource.TINKOFF: _TinkoffData,
        }
        class_ = classes.get(source)

        return class_

    # }}}
    @classmethod  # __checkUpdate  # {{{
    async def __checkUpdate(cls):
        logger.debug(f"{cls.__name__}.__checkUpdate()")

        # Check the file with the date of the last update of the market data
        if Cmd.isExist(cls.__LAST_UPDATE_FILE):
            string = Cmd.read(cls.__LAST_UPDATE_FILE)
            last_update = datetime.fromisoformat(string)
            if now().date() == last_update.date():
                cls.__DATA_IS_UP_TO_DATE = True
                return

        # update all availible market data
        logger.info(":: Auto update market data")
        await cls.updateAll()
        cls.__DATA_IS_UP_TO_DATE = True

        # save last update datetime
        dt = now().isoformat()
        Cmd.write(dt, cls.__LAST_UPDATE_FILE)
        logger.info("Update complete")

    # }}}
    @classmethod  # __fillVoid  # {{{
    def __fillVoid(cls, bars: list[_Bar], data_type: DataType) -> list[_Bar]:
        logger.debug(f"{cls.__name__}.__fillVoid()")

        time = datetime.combine(bars[0].dt.date(), DAY_BEGIN)
        end = datetime.combine(bars[-1].dt.date(), DAY_END)
        step = data_type.toTimeDelta()

        i = 0
        filled = list()
        while time <= end:
            if i < len(bars) and time == bars[i].dt:
                filled.append(bars[i])
                i += 1
            else:
                filled.append(cls.VoidBar(time))
            time += step

        return filled

    # }}}
    @classmethod  # __removeVoid  # {{{
    def __removeVoid(cls, bars: list) -> list:
        logger.debug(f"{cls.__name__}.__removeVoid()")

        i = 0
        while i < len(bars):
            if isinstance(bars[i], cls.VoidBar):
                bars.pop(i)
            else:
                i += 1

        return bars

    # }}}
    @classmethod  # __choseConverter  # {{{
    def __choseConverter(cls, out_type: DataType) -> Callable:
        logger.debug(f"{cls.__name__}.__choseConverter()")

        if out_type.toTimeDelta() <= timedelta(days=1):
            conv = cls.__convertSmallTimeFrame
        elif out_type.value == "W":
            conv = cls.__convertWeekTimeFrame
        elif out_type.value == "M":
            conv = cls.__convertMonthTimeFrame

        return conv

    # }}}
    @classmethod  # __convertSmallTimeFrame  # {{{
    def __convertSmallTimeFrame(cls, bars, in_type, out_type):
        logger.debug(f"{cls.__name__}.__convertSmallTimeFrame()")

        bars = cls.__fillVoid(bars, in_type)
        period = out_type.toTimeDelta()

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
    @classmethod  # __convertWeekTimeFrame  # {{{
    def __convertWeekTimeFrame(cls, bars, in_type, out_type):
        logger.debug(f"{cls.__name__}.__convertWeekTimeFrame()")
        assert in_type.toTimeDelta() == timedelta(days=1)

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
    @classmethod  # __convertMonthTimeFrame  # {{{
    def __convertMonthTimeFrame(cls, bars, in_type, out_type):
        logger.debug(f"{cls.__name__}.__convertMonthTimeFrame()")
        assert in_type.toTimeDelta() == timedelta(days=1)

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
    @classmethod  # __join  # {{{
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
    async def __update(cls, node):
        logger.debug(f"{cls.__name__}.__update()")

        # If the data is obtained by convertation, go out
        if node.source == DataSource.CONVERT:
            return

        instr = node.instrument
        data_type = node.data_type
        source = node.source
        source_class = cls.__getDataSourceClass(source)
        last_dt = node.last_dt
        logger.info(f"Updating {instr.ticker}-{data_type.value}")

        # request new bars
        begin = last_dt + data_type.toTimeDelta()
        end = now().replace(microsecond=0)
        new_bars = await source_class.getHistoricalBars(
            instr, data_type, begin, end
        )

        # check: is new bars found
        count = len(new_bars)
        if count == 0:
            logger.info("  - no new bars")
            return

        # save new bars
        logger.info(f"  - received {count} bars -> {new_bars[-1].dt}")
        new_data = _BarsData(source, instr, data_type, new_bars)
        await _BarsData.save(new_data)

    # }}}


if __name__ == "__main__":
    ...
