#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

from __future__ import annotations

import abc
import os
from dataclasses import dataclass
from datetime import UTC, date, datetime, time, timedelta

import moexalgo
import pandas as pd
import tinkoff.invest as ti

from avin.const import (
    DAY_BEGIN,
    DAY_END,
    ONE_DAY,
    ONE_WEEK,
    Dir,
    Res,
    Usr,
    WeekDays,
)
from avin.data.asset_type import AssetType
from avin.data.data_type import DataType
from avin.data.exchange import Exchange
from avin.data.instrument_id import InstrumentId
from avin.data.source import Source
from avin.keeper import Keeper
from avin.logger import logger
from avin.utils import Cmd, now


class Data:  # {{{
    @classmethod  # find# {{{
    async def find(
        cls,
        asset_type: AssetType = None,
        exchange: Exchange = None,
        ticker: str = None,
        figi: str = None,
        name: str = None,
        source: Source = None,
    ) -> list[InstrumentId]:
        """Find instrument id

        Args:
            asset_type - ...
        """
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

        if source == Source.MOEX:
            class_ = _MoexData
        elif source == Source.TINKOFF:
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
        check = cls.__checkArgs(ID=ID)
        if not check:
            return None

        if ID.exchange == Exchange.MOEX and ID.type == AssetType.INDEX:
            class_ = _MoexData
        else:
            class_ = _TinkoffData

        info = await class_.info(ID)
        return info

    # }}}
    @classmethod  # firstDateTime# {{{
    async def firstDateTime(
        cls, source: Source, data_type: DataType, ID: InstrumentId
    ) -> datetime:
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

        class_ = cls.__getSource(source)
        dt = await class_.firstDateTime(ID, data_type)
        return dt

    # }}}
    @classmethod  # download# {{{
    async def download(
        cls, source: Source, data_type: DataType, ID: InstrumentId, year: int
    ) -> None:
        check = cls.__checkArgs(
            source=source, ID=ID, data_type=data_type, year=year
        )
        if not check:
            return

        class_ = cls.__getSource(source)
        await class_.download(ID, data_type, year)

    # }}}
    @classmethod  # convert# {{{
    async def convert(
        cls, ID: InstrumentId, in_type: DataType, out_type: DataType
    ) -> bool:
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
        return True

    # }}}
    @classmethod  # delete# {{{
    async def delete(
        cls,
        ID: InstrumentId,
        data_type: DataType,
        begin: datetime = None,
        end: datetime = None,
    ) -> None:
        check = cls.__checkArgs(
            ID=ID,
            data_type=data_type,
        )
        if not check:
            return

        if data_type == DataType.BOOK or data_type == DataType.TIC:
            assert False

        await _Manager.delete(ID, data_type, begin, end)

    # }}}
    @classmethod  # update# {{{
    async def update(
        cls, ID: InstrumentId, data_type: DataType = None
    ) -> bool:
        assert ID.exchange == Exchange.MOEX
        assert data_type != DataType.TIC
        assert data_type != DataType.BOOK
        check = cls.__checkArgs(
            ID=ID,
            data_type=data_type,
        )
        if check:
            data_type = DataType(data_type)
            _Manager.update(ID, data_type)
            return True

    # }}}
    @classmethod  # updateAll# {{{
    async def updateAll(cls) -> bool:
        _Manager.updateAll()

    # }}}
    @classmethod  # request# {{{
    async def request(
        cls,
        ID: InstrumentId,
        data_type: DataType,
        begin: int,
        end: int,
    ) -> list[str]:
        check = cls.__checkArgs(
            ID=ID,
            data_type=data_type,
            begin=begin,
            end=end,
        )

        if check:
            if data_type == DataType.BOOK or data_type == DataType.TIC:
                assert False
            else:
                bars = _Manager.request(ID, data_type, begin, end)
                return bars

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
        if source:
            cls.__checkSource(source)
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
    @classmethod  # __checkSource# {{{
    def __checkSource(cls, source):
        if not isinstance(source, Source):
            raise TypeError(
                "You stupid monkey, select the 'source' from the enum "
                "Source."
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
    def __checkBeginEnd(cls, begin, end):
        if not isinstance(begin, int):
            raise TypeError(
                "You stupid monkey, use type <int> for argument 'begin'"
            )
        if not isinstance(end, int):
            raise TypeError(
                "You stupid monkey, use type <int> for argument 'end'"
            )
        if begin > end:
            raise ValueError(
                f"You're still a stupid monkey, how the fuck you to get data "
                f"data from '{begin}' to '{end}'?"
            )

    # }}}
    @classmethod  # __getSource# {{{
    def __getSource(cls, source: Source) -> object:
        classes = {Source.MOEX: _MoexData, Source.TINKOFF: _TinkoffData}
        class_ = classes.get(source)
        return class_

    # }}}


# }}}


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
    @classmethod  # toCSV# {{{
    def toCSV(cls, bar):
        dt = bar.dt.isoformat()
        s = f"{dt};{bar.open};{bar.high};{bar.low};{bar.close};{bar.vol}"
        return s

    # }}}
    @classmethod  # fromCSV# {{{
    def fromCSV(cls, string, requester=None):
        DT, OPEN, HIGH, LOW, CLOSE, VOLUME = range(6)
        fields = string.split(";")
        bar = _Bar(
            dt=datetime.fromisoformat(fields[DT]),
            open=float(fields[OPEN]),
            high=float(fields[HIGH]),
            low=float(fields[LOW]),
            close=float(fields[CLOSE]),
            vol=int(fields[VOLUME]),
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
        self.__data_type = data_type
        self.__bars = bars
        self.__source = source

    # }}}
    @property  # ID# {{{
    def ID(self):
        return self.__ID

    # }}}
    @property  # data_type# {{{
    def data_type(self):
        # TODO: rename 'data_type' -> 'type'
        return self.__data_type

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
        logger.info(f"Saved {data.ID.ticker}-{data.data_type.value}")

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

        bars = await Keeper.get(
            _Bar, ID=ID, data_type=data_type, begin=begin, end=end
        )
        # TODO
        # Пока источник данных только один Source.MOEX, и он не хранится...
        # Так что я его тут прямо беру и указываю, в будущем, источник
        # данных нужно тоже хранить в базе, и получать от туда
        data = _BarsData(ID, data_type, bars, Source.MOEX)
        return data

    # }}}
    @classmethod  # delete  # {{{
    async def delete(
        cls,
        ID: InstrumentId,
        data_type: DataType,
        begin: datetime,
        end: datetime,
    ) -> _BarsData:
        logger.debug(f"{cls.__name__}.delete()")

        bars = await Keeper.delete(
            _Bar, ID=ID, data_type=data_type, begin=begin, end=end
        )

    # }}}


# }}}
class _StockData:  # {{{
    ...


# }}}
class _TickData:  # {{{
    ...


# }}}
class _InstrumentInfoCache:  # {{{
    def __init__(  # {{{
        self,
        source: Source,
        asset_type: AssetType,
        assets_info: list,
    ):
        self.source = source
        self.asset_type = asset_type
        self.assets_info = assets_info

    # }}}
    @classmethod  # save# {{{
    async def save(cls, cache: _InstrumentInfoCache) -> None:
        # save cache in res files
        cache_dir = Cmd.path(Res.CACHE, cache.source.name.lower())
        file_path = Cmd.path(cache_dir, f"{cache.asset_type.name}.json")
        Cmd.saveJson(cache.assets_info, file_path, encoder=cls.encoderJson)

        # save cache in postgres
        await Keeper.update(cache)

    # }}}
    @classmethod  # load# {{{
    def load(cls, source: Source, asset_type: AssetType):
        cache_dir = Cmd.path(Res.CACHE, source.name.lower())
        cache_path = Cmd.path(cache_dir, f"{asset_type.name}.json")
        cache = Cmd.loadJson(cache_path, decoder=cls.decoderJson)
        return cache

    # }}}
    @classmethod  # checkCachingDate# {{{
    def checkCachingDate(cls, source: Source):
        file_path = Cmd.path(Res.CACHE, source.name.lower(), "last_update")
        if Cmd.isExist(file_path):
            string = Cmd.read(file_path)
            last_update = datetime.fromisoformat(string)
            if now().date() == last_update.date():
                return True
        return False

    # }}}
    @classmethod  # updateCachingDate# {{{
    def updateCachingDate(cls, source: Source):
        dt = now().isoformat()
        file_path = Cmd.path(Res.CACHE, source.name.lower(), "last_update")
        Cmd.write(dt, file_path)

    # }}}
    @staticmethod  # encoderJson# {{{
    def encoderJson(obj):
        # TODO: собрать сюда все что по модулю разбросано как
        # изменения в словаре для postgres... удаление ' в двух местах там
        # в моекс и в тиньков соурс... только как их тут
        # ????? Все строки реплейсить - бред
        # а если всетаки внутри кипера эти преобразования делать?
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()

    # }}}
    @staticmethod  # decoderJson# {{{
    def decoderJson(obj):
        # TODO:
        # см формат файлов кэша, там слишком много деталей спецефичных
        # сейчас в MOEX файлах после чтения остаются строками разные даты:
        # "SETTLEDATE": "2024-05-31"
        # "LASTTRADEDATE": "2025-03-20",
        # "LASTDELDATE": "2025-03-20",
        # "IMTIME": "2024-05-29T18:58:11",
        # Пока они нигде не используются, так что пусть так и лежат.
        # На будущее возможное решение - при сохранении все эти поля
        # проверять и переводить в UTC datetime сразу при кэшировании
        for k, v in obj.items():
            if isinstance(v, str) and "+00:00" in v:
                obj[k] = datetime.fromisoformat(obj[k])
        return obj

    # }}}


# }}}
class _AbstractSource(metaclass=abc.ABCMeta):  # {{{
    """const"""  # {{{

    _SUB_DIR = None

    # }}}
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
class _MoexData(_AbstractSource):  # {{{
    """const"""  # {{{

    source = Source.MOEX

    MSK_TIME_DIF = timedelta(hours=3)
    AVAILIBLE_DATA = [
        DataType.BAR_1M,
        DataType.BAR_10M,
        DataType.BAR_1H,
        DataType.BAR_D,
        DataType.BAR_W,
        DataType.BAR_M,
    ]

    _SUB_DIR = "moex"
    _DOWNLOAD = Cmd.path(Usr.DOWNLOAD, _SUB_DIR)

    _LOGIN = None
    _PASSWORD = None
    _AUTHORIZATION = None

    _AUTO_UPDATE = Usr.AUTO_UPDATE_ASSET_CACHE
    _INDEX_CACHE = None
    _SHARE_CACHE = None
    _FUTURE_CACHE = None
    _CURRENCY_CACHE = None

    # }}}
    @classmethod  # find  # {{{
    async def find(
        cls,
        asset_type: AssetType,
        exchange: Exchange,
        ticker: str,
        figi: str,
        name: str,
    ) -> InstrumentId:
        if cls._AUTO_UPDATE:
            await _MoexData.__cacheAssetsInfo()
            ...

        assets_info = await Keeper.info(
            cls.source,
            asset_type,
            EXCHANGE=exchange.name if exchange else None,
            SECID=ticker,
            FIGI=figi,
            NAME=name,
        )

        # for INDEXes:
        id_list = list()
        if asset_type == AssetType.INDEX:
            for i in assets_info:
                ID = InstrumentId(
                    asset_type,
                    Exchange.fromStr(i["EXCHANGE"]),
                    i["SECID"],
                    i["FIGI"],  # use my fake figi
                    i["NAME"],
                )
                id_list.append(ID)
            return id_list

        # for other types, or None:
        # MOEX does not provide instruments 'figi',
        # load 'figi' from Tinkoff cache
        # and use 'name' from Tinkoff too
        for i in assets_info:
            exchange = Exchange.fromStr(i["EXCHANGE"])
            asset_type = AssetType.fromStr(i["TYPE"])
            ticker = i["SECID"]
            tinkoff_info = await Keeper.info(
                Source.TINKOFF,
                asset_type,
                exchange=exchange.name,
                ticker=ticker,
            )
            if tinkoff_info:
                figi = tinkoff_info[0]["figi"]
                name = tinkoff_info[0]["name"]
                ID = InstrumentId(asset_type, exchange, ticker, figi, name)
                id_list.append(ID)
            else:
                # NOTE
                # если у Тинька нет информации по активу, поторговать
                # им все равно пока не получится, так что просто
                # пропускаем этот актив
                pass

        return id_list

    # }}}
    @classmethod  # info  # {{{
    async def info(cls, ID: InstrumentId) -> dict:
        assert ID.type == AssetType.INDEX
        info = await Keeper.info(cls.source, ID.type, FIGI=ID.figi)
        assert len(info) == 1
        return info[0]

    # }}}
    @classmethod  # firstDateTime  # {{{
    async def firstDateTime(
        cls, ID: InstrumentId, data_type: DataType
    ) -> datetime:
        date_start = date(1990, 1, 1)
        try:
            asset = moexalgo.Ticker(ID.ticker)
            candles = asset.candles(
                start=date_start,
                end="today",
                period=cls.__convert(data_type),
                use_dataframe=False,
            )
        except LookupError:
            logger.warning(f"_MoexData: no market data for {ID.ticker}")
            return None
        candle = candles.send(None)
        dt = candle.begin
        return cls.__toUTC(dt)

    # }}}
    @classmethod  # download  # {{{
    async def download(
        cls, ID: InstrumentId, data_type: DataType, year: int
    ) -> bool:
        assert data_type in cls.AVAILIBLE_DATA
        await cls.__authorizate()

        logger.info(f":: Download {ID.ticker}-{data_type.value} from {year}")
        begin, end = cls.__getPeriod(year)
        candles = cls.__getHistoricalCandles(ID, data_type, begin, end)
        if len(candles) == 0:
            logger.warning(
                f"No data received for {ID.ticker}-{data_type.value}-{year}"
            )
            return

        bars = cls.__convertCandlesToBars(candles)
        data = _BarsData(ID, data_type, bars, cls.source)
        await _BarsData.save(data)

    # }}}
    @classmethod  # export  # {{{
    async def export(cls) -> None:
        logger.info(":: MOEX exporting data in standart format")
        files = Cmd.getFiles(
            cls._DOWNLOAD, full_path=True, include_sub_dir=True
        )
        files = sorted(Cmd.select(files, extension=".csv"))
        for file in files:
            logger.info(f"  - exporting '{file}'")
            ID, data_type, bars = cls.__readDataFile(file)
            data = _BarsData(ID, data_type, bars, Source.MOEX)
            _BarsData.save(data)
        logger.info("Export complete")

    # }}}
    @classmethod  # clear  # {{{
    async def clear(cls) -> bool:
        logger.info(":: Clear MOEX files")
        path = cls._DOWNLOAD
        if not Cmd.isExist(path):
            logger.info(f"  - no data in '{path}'")
            return
        Cmd.deleteDir(path)
        logger.info("  - successful complete")

    # }}}
    @classmethod  # getHistoricalBars  # {{{
    async def getHistoricalBars(
        cls,
        ID: InstrumentId,
        data_type: DataType,
        begin: datetime,
        end: datetime,
    ) -> list[_Bar]:
        begin = cls.__toMSK(begin)
        end = cls.__toMSK(end)

        candles = cls.__getHistoricalCandles(ID, data_type, begin, end)
        bars = cls.__convert(candles)
        return bars

    # }}}
    @classmethod  # __authorizate  # {{{
    async def __authorizate(cls):
        if cls._AUTHORIZATION:
            return

        account_path = Cmd.path(Usr.CONNECT, cls._SUB_DIR, Usr.MOEX_ACCOUNT)
        if Cmd.isExist(account_path):
            login, password = Cmd.loadText(account_path)
            login, password = login.strip(), password.strip()
        else:
            logger.warning(
                "MOEX not exist account file, operations with real time "
                "market data unavailible. Register and put the file with "
                f"login and password in '{account_path}'. Read more: "
                "https://passport.moex.com/registration"
            )
            return

        cls._AUTHORIZATION = moexalgo.session.authorize(login, password)
        if cls._AUTHORIZATION:
            _MoexData._LOGIN = login
            _MoexData._PASSWORD = password
            logger.info("MOEX Authorization successful")
        else:
            logger.warning(
                "MOEX authorization fault, check your login and password. "
                "Operations with real time market data unavailible. "
                f"Login='{login}' password='{password}'"
            )

    # }}}
    @classmethod  # __cacheAssetsInfo  # {{{
    async def __cacheAssetsInfo(cls):
        if _InstrumentInfoCache.checkCachingDate(cls.source):
            return

        logger.info(":: Caching assets info from MOEX")
        await cls.__authorizate()
        if not cls._AUTHORIZATION:
            return

        types = ["index", "shares", "currency", "futures"]
        for type_ in types:
            logger.info(f"  - caching {type_}")
            assets_info = moexalgo.Market(type_).tickers(use_dataframe=False)
            assets_info = cls.__formatAssetsInfo(assets_info)
            asset_type = cls._getStandartAssetType(type_)
            cache = _InstrumentInfoCache(Source.MOEX, asset_type, assets_info)
            await _InstrumentInfoCache.save(cache)

        _InstrumentInfoCache.updateCachingDate(cls.source)

    # }}}
    @classmethod  # __formatAssetsInfo# {{{
    def __formatAssetsInfo(cls, assets_info: list[dict]):
        for i in assets_info:
            i["EXCHANGE"] = "MOEX"
            if i["BOARDID"] == "SNDX":
                i["TYPE"] = AssetType.INDEX.name
                # NOTE
                # Indexes not have 'figi', but I'm use figi in
                # InstrumentId - unified identificator for all assets
                # for use search by figi, I'm add in to indices
                # not real global figi, its only my local idea,
                # figi = <exchane_name>_<ticker>
                i["FIGI"] = f"_MOEX_{i['SECID']}"
            elif i["BOARDID"] == "TQBR":
                i["TYPE"] = AssetType.SHARE.name
                # NOTE
                # "Latname": "Perm 'Energosbyt", and other similar ones ..
                # a single roll then interferes when transforming
                # in postgres jsonb, delete thats fucked symbol '
                i["LATNAME"] = i["LATNAME"].replace("'", "")
            elif i["BOARDID"] == "RFUD":
                i["TYPE"] = AssetType.FUTURE.name
            elif i["BOARDID"] == "CETS":
                i["TYPE"] = AssetType.CURRENCY.name

        return assets_info

    # }}}
    @classmethod  # __convert# {{{
    def __convert(cls, obj: object):
        if isinstance(obj, DataType):
            return cls.__convertDataTypeToMoexPeriod(obj)
        elif isinstance(obj, list):
            return cls.__convertCandlesToBars(obj)
        else:
            assert False, f"unknown object type '{type(obj)}'"

    # }}}
    @classmethod  # __convertDataTypeToMoexPeriod# {{{
    def __convertDataTypeToMoexPeriod(cls, data_type: DataType):
        moex_period = {
            "1M": "1min",
            "10M": "10min",
            "1H": "1h",
            "D": "1d",
            "W": "1w",
            "M": "1m",
        }
        return moex_period[data_type.value]

    # }}}
    @classmethod  # __convertCandlesToBars# {{{
    def __convertCandlesToBars(cls, candles):
        bars = list()
        for i in candles:
            bar = _Bar(
                dt=cls.__toUTC(i.begin),
                open=i.open,
                high=i.high,
                low=i.low,
                close=i.close,
                vol=int(i.volume),
            )
            bars.append(bar)
        return bars

    # }}}
    @classmethod  # __getPeriod# {{{
    def __getPeriod(cls, year: int) -> (datetime, datetime):
        begin = datetime(year, 1, 1)
        end = datetime(year + 1, 1, 1)
        if end >= datetime.now():
            end = datetime.now().replace(microsecond=0)
        return (begin, end)

    # }}}
    @classmethod  # __requestCandles# {{{
    def __requestCandles(
        cls,
        ID: InstrumentId,
        data_type: DataType,
        begin: datetime,
        end: datetime,
    ):
        period = data_type.toTimedelta()
        if period < ONE_DAY:
            return cls.__requestCandlesSmallTimeFrame(
                ID, data_type, begin, end
            )
        else:
            return cls.__requestCandlesBigTimeFrame(ID, data_type, begin, end)

    # }}}
    @classmethod  # __requestCandlesBigTimeFrame# {{{
    def __requestCandlesBigTimeFrame(
        cls,
        ID: InstrumentId,
        data_type: DataType,
        begin: datetime,
        end: datetime,
    ):
        all_candles = list()
        asset = moexalgo.Ticker(ID.ticker)
        period = cls.__convert(data_type)
        current = begin

        while current < end:
            logger.info(
                f"  - request {ID.ticker}-{data_type.value} {current.date()}"
            )
            candles = asset.candles(
                start=current,
                end=current.replace(year=current.year + 1),
                period=period,
                use_dataframe=False,
            )
            for i in candles:
                all_candles.append(i)
            current = current.replace(year=current.year + 1)

        # Fucking MOEX returns candles in closed interval [begin, end]
        # fix it, return [begin, end)
        if all_candles and all_candles[-1].begin == end:
            all_candles.pop(-1)

        return all_candles

    # }}}
    @classmethod  # __requestCandlesSmallTimeFrame# {{{
    def __requestCandlesSmallTimeFrame(cls, ID, data_type, begin, end):
        all_candles = list()
        asset = moexalgo.Ticker(ID.ticker)
        period = cls.__convert(data_type)
        current = begin
        while current < end:
            logger.info(
                f"  - request {ID.ticker}-{data_type.value} "
                f"from {current.date()}"
            )
            candles = asset.candles(
                start=current,
                end=datetime.combine(current.date(), time(23, 59)),
                period=period,
                use_dataframe=False,
            )
            for i in candles:
                all_candles.append(i)
            current = datetime.combine(current.date() + ONE_DAY, time(00, 00))
        return all_candles

    # }}}
    @classmethod  # __getHistoricalCandles# {{{
    def __getHistoricalCandles(
        cls,
        ID: InstrumentId,
        data_type: DataType,
        begin: datetime,
        end: datetime,
    ):
        candles = cls.__requestCandles(ID, data_type, begin, end)
        if not candles:
            return list()

        # skip uncomplete candle timeframe M
        if data_type == DataType.BAR_M:
            last_candle_month = candles[-1].end.month
            now_month = date.today().month
            if last_candle_month == now_month:
                candles.pop(-1)
            return candles

        # skip uncomplete candle other timeframes
        period = data_type.toTimedelta()
        if period <= ONE_WEEK:
            last_candle_begin = candles[-1].begin
            last_candle_end = candles[-1].end
            if last_candle_end < last_candle_begin + period:
                candles.pop(-1)
            return candles

        assert False, "Тут мы никак не должны оказаться"

    # }}}

    @classmethod  # __createFilePath# {{{
    def __createFilePath(
        cls, ID: InstrumentId, data_type: DataType, year: int
    ):
        dir_path = Cmd.path(cls._DOWNLOAD, ID.type.name, ID.ticker)
        Cmd.makeDirs(dir_path)
        file_name = (
            f"{ID.exchange.name}-{ID.type.name}-{ID.ticker}-"
            f"{data_type.value}-{year}.csv"
        )
        full_path = Cmd.path(dir_path, file_name)
        return full_path

    # }}}
    @classmethod  # __saveCandles# {{{
    def __saveCandles(
        cls,
        ID: InstrumentId,
        data_type: DataType,
        year: int,
        candles: list[moexalgo.models.Candle],
    ):
        path = cls.__createFilePath(ID, data_type, year)
        df = pd.DataFrame(candles)
        df.to_csv(path, sep=";")
        logger.info(f"Saved {ID.ticker} {data_type.value} {year} in '{path}'")

    # }}}
    @classmethod  # __readDataFile# {{{
    def __readDataFile(cls, file_path: str):
        ID, data_type = cls._parseFileName(Cmd.name(file_path))
        bars = cls.__readFileText(Cmd.loadText(file_path))
        return ID, data_type, bars

    # }}}
    @classmethod  # __readFileText# {{{
    def __readFileText(cls, text):
        text.pop(0)  # skip header row
        bars = list()
        for line in text:
            bar = cls.__parseMoexLine(line)
            bars.append(bar)
        return bars

    # }}}
    @classmethod  # __parseMoexLine# {{{
    def __parseMoexLine(cls, line: str):
        NUM, OPEN, CLOSE, HIGH, LOW, VALUE, VOLUME, BEGIN, END = range(9)
        fields = line.split(";")
        open_ = float(fields[OPEN])
        high = float(fields[HIGH])
        low = float(fields[LOW])
        close = float(fields[CLOSE])
        volume = int(float(fields[VOLUME]))
        dt = cls.__toUTC(datetime.fromisoformat(fields[BEGIN]))
        return _Bar(dt, open_, high, low, close, volume)

    # }}}
    @classmethod  # __toUTC# {{{
    def __toUTC(cls, moex_dt: datetime) -> datetime:
        # Для таймфреймов 1M, 10M, 1H у MOEX поле с датой открытия
        # бара имеет и дату и время. Время московское, приводим его в UTC+0
        if moex_dt.hour != 0:
            return (moex_dt - cls.MSK_TIME_DIF).replace(tzinfo=UTC)
        else:
            # Для таймфреймов 1D, W, M в файлах MOEX поле с датой открытия
            # бара имеет только дату.
            # datetime.fromisoformat возвращает дату со временем 00:00
            # тут остается только заменить timezone на UTC+0
            return moex_dt.replace(tzinfo=UTC)

    # }}}
    @classmethod  # __toMSK# {{{
    def __toMSK(cls, utc_dt: datetime) -> datetime:
        # MOEX work with Moscow time, UTC+3, and use offset-naive datetime
        if utc_dt.hour != 0:
            return (utc_dt + cls.MSK_TIME_DIF).replace(tzinfo=None)
        else:
            # timeframe >= D, msk time = 00:00, only change timezone
            return utc_dt.replace(tzinfo=None)

    # }}}


# }}}
class _TinkoffData(_AbstractSource):  # {{{
    """const"""  # {{{

    source = Source.TINKOFF

    EXCLUDE_HOLIDAYS = True
    AVAILIBLE_DATA = [
        DataType.BAR_1M,
        DataType.BAR_5M,
        DataType.BAR_10M,
        DataType.BAR_1H,
        DataType.BAR_D,
        DataType.BAR_W,
        DataType.BAR_M,
    ]

    _SUB_DIR = "tinkoff"
    _DOWNLOAD = Cmd.path(Usr.DOWNLOAD, _SUB_DIR)

    _TARGET = ti.constants.INVEST_GRPC_API
    _TOKEN_PATH = Usr.TINKOFF_TOKEN
    _TOKEN = None

    _AUTO_UPDATE = Usr.AUTO_UPDATE_ASSET_CACHE
    _SHARE_CACHE = None
    _BONDS_CACHE = None
    _FUTURE_CACHE = None
    _CURRENCY_CACHE = None
    _ETF_CACHE = None

    # }}}
    @classmethod  # find  # {{{
    async def find(
        cls,
        asset_type: AssetType,
        exchange: Exchange,
        ticker: str,
        figi: str,
        name: str,
    ) -> InstrumentId:
        if cls._AUTO_UPDATE:
            await cls.__cacheAssetsInfo()

        assets_info = await Keeper.info(
            cls.source,
            asset_type,
            exchange=exchange.name if exchange else None,
            ticker=ticker,
            figi=figi,
            name=name,
        )

        id_list = list()
        for i in assets_info:
            ID = InstrumentId(
                AssetType.fromStr(i["type"]),
                Exchange.fromStr(i["exchange"]),
                i["ticker"],
                i["figi"],
                i["name"],
            )
            id_list.append(ID)
        return id_list

    # }}}
    @classmethod  # info  # {{{
    async def info(cls, ID: InstrumentId) -> dict:
        info = await Keeper.info(cls.source, ID.type, figi=ID.figi)
        assert len(info) == 1
        return info[0]

    # }}}
    @classmethod  # firstDateTime  # {{{
    async def firstDateTime(
        cls, ID: InstrumentId, data_type: DataType
    ) -> datetime:
        info = await cls.info(ID)
        if data_type.value == "1M":
            return info["first_1min_candle_date"]
        elif data_type.value == "D":
            return info["first_1day_candle_date"]

    # }}}
    @classmethod  # download  # {{{
    async def download(
        cls, ID: InstrumentId, data_type: DataType, year: int
    ) -> None:
        assert False, "переписать на postgres, пока качаю только с МОЕКС"

        assert data_type.value == "1M"
        auth = await cls.__authorizate()
        if not auth:
            return

        logger.info(f":: Download {ID.ticker}-{data_type.value} from {year}")
        cls.__requestHistoricalData(ID, year)

    # }}}
    @classmethod  # export  # {{{
    async def export(cls) -> None:
        assert False, "переписать на postgres, пока качаю только с МОЕКС"

        # TODO fix - not exclude holidays files
        logger.info(":: Tinkoff exporting data in standart format")
        files = Cmd.getFiles(
            cls._DOWNLOAD, full_path=True, include_sub_dir=True
        )
        archives = sorted(Cmd.select(files, extension=".zip"))

        for archive in archives:
            logger.info(f"  - exporting '{archive}'")
            tmp_dir = Cmd.path(Dir.TMP, cls._SUB_DIR)
            Cmd.extract(archive, tmp_dir)

            bars = cls.__loadDataDir(tmp_dir)
            ID, data_type = cls._parseFileName(Cmd.name(archive))

            data = _BarsData(ID, data_type, bars, Source.TINKOFF)
            _BarsData.save(data)

            Cmd.deleteDir(tmp_dir)

        logger.info("Export complete")

    # }}}
    @classmethod  # clear  # {{{
    async def clear(cls) -> None:
        assert False, "переписать на postgres, пока качаю только с МОЕКС"

        logger.info(":: Clear Tinkoff files")
        path = cls._DOWNLOAD
        if not Cmd.isExist(path):
            logger.info(f"  - no data in '{path}'")
            return
        Cmd.deleteDir(path)
        logger.info("  - successful complete")

    # }}}
    @classmethod  # getHistoricalBars  # {{{
    async def getHistoricalBars(
        cls,
        ID: InstrumentId,
        data_type: DataType,
        begin: datetime,
        end: datetime,
    ) -> list[_Bar]:
        assert False, "переписать на postgres, пока качаю только с МОЕКС"
        logger.info(
            f"  - request {ID.ticker}-{data_type.value} from {begin.date()}"
        )

        if not cls.__authorizate():
            return

        new_bars = list()
        with ti.Client(cls._TOKEN) as client:
            try:
                candles = client.get_all_candles(
                    figi=ID.figi,
                    from_=begin,
                    to=end,
                    interval=_TinkoffData.__CandleIntervalFrom(data_type),
                )
                for candle in candles:
                    if candle.is_complete:
                        bar = _TinkoffData.__toBar(candle)
                        new_bars.append(bar)
            except ti.exceptions.RequestError as err:
                logger.exception(err)
                return list()
            return new_bars

    # }}}
    @classmethod  # __authorizate# {{{
    async def __authorizate(cls) -> bool:
        # if cls._TOKEN is not None, then it's valid token
        if cls._TOKEN is not None:
            return True

        # check token file
        if not Cmd.isExist(cls._TOKEN_PATH):
            logger.warning(
                "Tinkoff not exist token file, operations with market data "
                "and orders unavailible. Make a token and put it in a "
                f"'{cls._TOKEN_PATH}'. Read more about token: "
                "https://developer.tinkoff.ru/docs/intro/"
                "manuals/self-service-auth"
            )
            return False

        # read token from file, and try to connect
        token = Cmd.read(cls._TOKEN_PATH).strip()
        try:
            with ti.Client(token) as client:
                response = client.users.get_accounts()
                if response:
                    _TinkoffData._TOKEN = token
                    logger.info("Tinkoff Authorization successful")
                    return True
        except ti.exceptions.UnauthenticatedError as err:
            logger.exception(err)
            logger.error(
                "Tinkoff authorization fault, check your token. "
                "Operations with market data unavailible. "
                f"Token='{token}'"
            )
            return False

    # }}}
    @classmethod  # __cacheAssetsInfo# {{{
    async def __cacheAssetsInfo(cls):
        if _InstrumentInfoCache.checkCachingDate(cls.source):
            return

        logger.info(":: Caching assets info from Tinkoff")
        auth = await cls.__authorizate()
        if not auth:
            return

        types = ["shares", "bonds", "futures", "currencies"]
        for type_ in types:
            logger.info(f"  - caching {type_}")
            assets_info = cls.__requestAvailibleAssets(type_)
            asset_type = cls._getStandartAssetType(type_)
            cache = _InstrumentInfoCache(cls.source, asset_type, assets_info)
            await _InstrumentInfoCache.save(cache)

        _InstrumentInfoCache.updateCachingDate(cls.source)

    # }}}
    @classmethod  # __requestAvailibleAssets# {{{
    def __requestAvailibleAssets(cls, asset_type: str):
        # asset_type must be availible for tinkoff invest API
        # for example: "shares", "bonds", "futures", "currencies"...
        with ti.Client(cls._TOKEN) as client:
            all_info = list()
            response: list[ti.Instrument] = getattr(
                client.instruments, asset_type
            )().instruments
            for item in response:
                item_info = cls.__extractBrokerInfo(item)
                if item_info["exchange"] is None:
                    continue
                item_info["type"] = cls._getStandartAssetType(asset_type).name
                all_info.append(item_info)
            return all_info

    # }}}
    @classmethod  # __extractBrokerInfo# {{{
    def __extractBrokerInfo(cls, instr: ti.Instrument) -> dict:
        # set simple exchange name, original exchange name
        # will saved after in the key 'exchange_specific'
        if "MOEX" in instr.exchange.upper():
            # NOTE
            # "instr.exchange" contain values as "MOEX_PLUS", "MOEX_WEEKEND"..
            # set "echange"="MOEX"
            exchange = "MOEX"
        elif "SPB" in instr.exchange.upper():
            # NOTE
            # "instr.exchange" contain values as "SPB_RU_MORNING"...
            # set "echange"="SPB"
            exchange = "SPB"
        elif "FORTS" in instr.exchange.upper():
            # NOTE
            # FUTURE - у них биржа указана FORTS_EVENING, но похеру
            # пока для простоты ставлю им тоже биржу MOEX
            exchange = "MOEX"
        elif instr.exchange == "FX":
            # NOTE
            # CURRENCY - у них биржа указана FX, но похеру
            # пока для простоты ставлю им тоже биржу MOEX
            exchange = "MOEX"
        else:
            # NOTE
            # там всякая странная хуйня еще есть в биржах
            # "otc_ncc", "LSE_MORNING", "moex_close", "Issuance",
            # "unknown"...
            # Часть из них по факту американские биржи, по которым сейчас
            # один хрен торги не доступны, другие хз, внебирживые еще, я всем
            # этим не торгую, поэтому сейчас ставим всем непонятным активам
            # биржу None, а потом перед сохранением делаем фильтр
            # если биржа None - отбрасываем этот ассет из кэша
            exchange = None

        # define short function name
        to_decimal = ti.utils.quotation_to_decimal
        info = {
            # NOTE
            # "name": "O'Key Group SA", и другие подобные
            # одинарная кавчка потом мешается при преобразовании
            # в postgres jsonb
            "name": instr.name.replace("'", ""),  # remove ' in name
            "ticker": instr.ticker,
            "country_of_risk": instr.country_of_risk,
            "currency": instr.currency,
            "exchange": exchange,
            "exchange_specific": instr.exchange,
            "class_code": instr.class_code,
            "figi": instr.figi,
            "uid": instr.uid,
            "lot": instr.lot,
            "min_price_increment": float(
                to_decimal(instr.min_price_increment)
            ),
            "trading_status": ti.SecurityTradingStatus(
                instr.trading_status
            ).name,
            "for_qual_investor_flag": instr.for_qual_investor_flag,
            "api_trade_available_flag": instr.api_trade_available_flag,
            "buy_available_flag": instr.buy_available_flag,
            "sell_available_flag": instr.sell_available_flag,
            "short_enabled_flag": instr.short_enabled_flag,
            "klong": float(to_decimal(instr.klong)),
            "kshort": float(to_decimal(instr.kshort)),
            "first_1min_candle_date": instr.first_1min_candle_date,
            "first_1day_candle_date": instr.first_1day_candle_date,
        }

        # save attributes "isin" & "sector", if availible
        if hasattr(instr, "isin"):
            info["isin"] = instr.isin
        if hasattr(instr, "sector"):
            info["sector"] = instr.sector

        return info

    # }}}
    @classmethod  # __getId# {{{
    def __getId(cls, info: dict) -> InstrumentId:
        # In dictionaries received from the broker, the moex exchange is
        # designated in several ways:
        # MOEX, MOEX_PLUS, MOEX_EVENING_WEEKEND, moex_extended...
        if (
            "MOEX" in info["exchange"].upper()
            or info["exchange"] == "FORTS_EVENING"
        ):
            exchange = Exchange.MOEX
        # Similar to SPB exchange: spb_close, SPB_RU_MORNING..
        elif "SPB" in info["exchange"].upper():
            exchange = Exchange.SPB
        else:
            logger.critical(
                f"_TinkoffData.__getId: unknown exchange={info['exchange']}"
            )
            exit(1)

        ID = InstrumentId(
            exchange=exchange,
            asset_type=AssetType.fromStr(info["type"]),
            name=info["name"],
            ticker=info["ticker"],
            figi=info["figi"],
        )
        return ID

    # }}}
    @classmethod  # __getAllId# {{{
    def __getAllId(cls, cache: list[dict]) -> list(InstrumentId):
        all_id = list()
        for asset in cache:
            ID = cls.__getId(asset)
            all_id.append(ID)
        return all_id

    # }}}
    @classmethod  # __requestHistoricalData# {{{
    def __requestHistoricalData(cls, ID: InstrumentId, year: int):
        exchange = ID.exchange.name
        type_ = ID.type.name
        figi = ID.figi
        ticker = ID.ticker
        file_name = f"{exchange}-{type_}-{ticker}-1M-{year}.zip"
        file_path = Cmd.path(cls._DOWNLOAD, type_, ticker, file_name)
        data_url = "https://invest-public-api.tinkoff.ru/history-data"

        bash_command = (
            f"curl -s --location '{data_url}?figi={figi}&year={year}' "
            f"-H 'Authorization: Bearer {cls._TOKEN}' "
            f"-o {file_name} "
        )
        os.system(bash_command)

        if Cmd.isExist(file_name):
            Cmd.replace(file_name, file_path)
            logger.info(f"  - saved {file_path}")

    # }}}
    @classmethod  # __loadDataDir# {{{
    def __loadDataDir(cls, dir_path):
        files = sorted(Cmd.getFiles(dir_path, full_path=True))
        if cls.EXCLUDE_HOLIDAYS:
            files = cls.__excludeHolidaysFiles(files)
        all_bars = list()
        for file in files:
            tinkoff_bars = cls.__readTinkoffFile(file)
            all_bars += tinkoff_bars
        return all_bars

    # }}}
    @classmethod  # __excludeHolidaysFiles# {{{
    def __excludeHolidaysFiles(cls, files):
        # file name like: '53b67587-96eb-4b41-8e0c-d2e3c0bdd234_20190103.csv'
        # consist of 'uid_date.csv'
        i = 0
        while i < len(files):
            file = files[i]
            file_name = Cmd.name(file, extension=False)
            file_date = date.fromisoformat(file_name.split("_")[1])
            week_day = file_date.weekday()
            if WeekDays.isHoliday(week_day):
                files.pop(i)
            else:
                i += 1
        return files

    # }}}
    @classmethod  # __excludeHolidaysBars# {{{
    def __excludeHolidaysBars(cls, bars: list[Bar]) -> list[Bar]:
        i = 0
        while i < len(bars):
            week_day = bars[i].dt.weekday()
            if WeekDays.isHoliday(week_day):
                bars.pop(i)
            else:
                i += 1
        return bars

    # }}}
    @classmethod  # __readTinkoffFile# {{{
    def __readTinkoffFile(cls, file_path):
        tinkoff_bars = list()
        text = Cmd.loadText(file_path)
        for line in text:
            bar = cls.__parseLineTinkoff(line)
            tinkoff_bars.append(bar)
        return tinkoff_bars

    # }}}
    @classmethod  # __parseLineTinkoff# {{{
    def __parseLineTinkoff(cls, line):
        fields = line.split(";")
        UID, DATETIME, OPEN, CLOSE, HIGH, LOW, VOLUME = range(7)
        opn = float(fields[OPEN])
        cls = float(fields[CLOSE])
        hgh = float(fields[HIGH])
        low = float(fields[LOW])
        vol = int(fields[VOLUME])
        dt = fields[DATETIME]
        bar = _Bar(dt, opn, hgh, low, cls, vol)
        return bar

    # }}}
    @classmethod  # __CandleIntervalFrom# {{{
    def __CandleIntervalFrom(cls, data_type: DataType) -> ti.CandleInterval:
        intervals = {
            "1M": ti.CandleInterval.CANDLE_INTERVAL_1_MIN,
            "10M": ti.CandleInterval.CANDLE_INTERVAL_10_MIN,
            "5M": ti.CandleInterval.CANDLE_INTERVAL_5_MIN,
            "1H": ti.CandleInterval.CANDLE_INTERVAL_HOUR,
            "D": ti.CandleInterval.CANDLE_INTERVAL_DAY,
            "W": ti.CandleInterval.CANDLE_INTERVAL_WEEK,
            "M": ti.CandleInterval.CANDLE_INTERVAL_MONTH,
        }
        return intervals[data_type.value]

    # }}}
    @classmethod  # __toBar# {{{
    def __toBar(cls, candle) -> _Bar:
        opn = float(ti.utils.quotation_to_decimal(candle.open))
        cls = float(ti.utils.quotation_to_decimal(candle.close))
        hgh = float(ti.utils.quotation_to_decimal(candle.high))
        low = float(ti.utils.quotation_to_decimal(candle.low))
        vol = candle.volume
        dt = candle.time
        bar = _Bar(dt, opn, hgh, low, cls, vol)
        return bar

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
    @classmethod  # allDataList{{{
    def allDataList(cls) -> list[tuple(InstrumentId, DataType, Source)]:
        logger.debug("Data.getAllDataDirs()")

        all_list = list()
        for root, dirs, files in os.walk(Usr.DATA):
            id_file = Cmd.select(files, name="id")
            type_file = Cmd.select(files, name="data_type")
            source_file = Cmd.select(files, name="source")
            csv_files = sorted(Cmd.select(files, extension=".csv"))

            # only one file per folder is possible, therefore use [0]
            if id_file and type_file and source_file and csv_files:
                id_path = Cmd.path(root, id_file[0])
                type_path = Cmd.path(root, type_file[0])
                source_path = Cmd.path(root, source_file[0])

                ID = InstrumentId.load(id_path)
                data_type = DataType.load(type_path)
                source = Source.load(source_path)

                all_list.append((ID, data_type, source))
        return all_list

    # }}}
    @classmethod  # availibleYears# {{{
    def availibleYears(cls, ID: InstrumentId, data_type: DataType):
        files = cls.__findFiles(ID, data_type)
        csv_files = Cmd.select(files, extension=".csv")
        years = [int(Cmd.name(i)) for i in (csv_files)]  # file_name == year
        if len(years) == 0:
            logger.warning(f"{ID.ticker}-{data_type.value} no data files")
        return years

    # }}}
    @classmethod  # convert# {{{
    async def convert(
        cls, ID: InstrumentId, in_type: DataType, out_type: DataType
    ):
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
        # TODO
        # Пока источник данных только один Source.MOEX, и он не хранится...
        # Так что я его тут прямо беру и указываю, в будущем, источник
        # данных нужно тоже хранить в базе, и получать от туда
        converted_data = _BarsData(ID, out_type, out_bars, Source.MOEX)
        await _BarsData.save(converted_data)

    # }}}
    @classmethod  # update# {{{
    def update(cls, ID: InstrumentId, data_type: DataType):
        data = cls.__lastBarsDataFile(ID, data_type)
        if not data:
            logger.error(
                f"No data for {ID.ticker}-{data_type.value}. "
                f"Operation canceled."
            )
            return

        # selecting the same source as the data and
        # check availiblity data_type
        if (
            data.source == Source.MOEX
            and data_type in _MoexData.AVAILIBLE_DATA
        ):
            cls.__update(data, _MoexData)
        elif (
            data.source == Source.TINKOFF
            and data_type in _TinkoffData.AVAILIBLE_DATA
        ):
            cls.__update(data, _TinkoffData)
        else:
            logger.error(
                f"Data source '{data.source.name}' "
                f"does not provide type '{data_type.value}'. "
                f"Operation canceled."
            )

    # }}}
    @classmethod  # updateAll# {{{
    def updateAll(cls):
        logger.info(":: Update all market data")
        data_list = cls.allDataList()
        count = len(data_list)
        for n, i in enumerate(data_list, 1):
            ID, data_type, source = i
            logger.info(f":: updating {n}/{count}")
            cls.update(ID, data_type)

    # }}}
    @classmethod  # request# {{{
    def request(
        cls, ID: InstrumentId, data_type: DataType, begin: int, end: int
    ) -> list:
        if cls._AUTO_UPDATE and not cls._DATA_IS_UP_TO_DATE:
            cls.__checkUpdate()

        files = cls.__findFiles(ID, data_type)
        files = cls.__selectYear(files, begin, end)
        return files

    # }}}
    @classmethod  # delete# {{{
    async def delete(
        cls,
        ID: InstrumentId,
        data_type: DataType,
        begin: datetime,
        end: datetime,
    ):
        logger.info(f":: Delete {ID.ticker}-{data_type.value}")
        await _BarsData.delete(ID, data_type, begin, end)
        logger.info("  - complete")

    # }}}
    @classmethod  # __checkUpdate# {{{
    def __checkUpdate(cls):
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
    @classmethod  # __findFiles# {{{
    def __findFiles(cls, ID: InstrumentId, data_type: DataType) -> list[str]:
        data_dir = Cmd.path(ID.dir_path, data_type.value)
        if not Cmd.isExist(data_dir):
            return list()
        files = sorted(Cmd.getFiles(data_dir, full_path=True))
        files = Cmd.select(files, extension=".csv")
        return files

    # }}}
    @classmethod  # __selectYear# {{{
    def __selectYear(cls, files, begin: int, end: int):
        out_files = list()
        for file in files:
            # Имена файлов выглядят так: 2022.csv, 2023.csv ...
            file_year = int(Cmd.name(file))
            if begin <= file_year <= end:
                out_files.append(file)
        return out_files

    # }}}
    @classmethod  # __lastBarsDataFile# {{{
    def __lastBarsDataFile(
        cls, ID: InstrumentId, data_type: DataType
    ) -> _BarsData:
        years = cls.availibleYears(ID, data_type)
        if years:
            data = _BarsData.load(ID, data_type, years[-1])
            return data
        else:
            return None

    # }}}
    @classmethod  # __update# {{{
    def __update(cls, data: _BarsData, source: _AbstractSource):
        begin = data.last_dt + data.data_type.toTimedelta()
        end = now().replace(microsecond=0)
        src = source()  # FIXME: это пиздец как не очевидно, что тут
        # создается объект _MoexData или _TinkoffData
        # надо как то переделать
        new_bars = src.getHistoricalBars(data.ID, data.data_type, begin, end)
        count = len(new_bars)
        if count == 0:
            logger.info("  - no new bars")
            return

        logger.info(f"  - received {count} bars -> {new_bars[-1].dt}")
        cls.__saveNewBars(data, new_bars)

    # }}}
    @classmethod  # __saveNewBars # {{{
    def __saveNewBars(cls, data: _BarsData, new_bars):
        year = data.year
        bars = cls.__popYear(new_bars, year)  # extract only equal year
        data.add(bars)
        _BarsData.save(data)

        # if 'new_bars' consist some more bars, create new files
        ID = data.ID
        data_type = data.data_type
        source = data.source
        while len(new_bars) > 0:
            year += 1
            bars = cls.__popYear(new_bars, year)
            new_data = _BarsData(ID, data_type, bars, source)
            _BarsData.save(new_data)

    # }}}
    @classmethod  # __popYear# {{{
    def __popYear(cls, bars, year):
        assert isinstance(bars, list)
        assert isinstance(year, int)
        extract = list()
        while len(bars) > 0 and bars[0].dt.year == year:
            bar = bars.pop(0)
            extract.append(bar)
        return extract

    # }}}
    @classmethod  # __fillVoid# {{{
    def __fillVoid(cls, bars: list[_Bar], data_type: DataType) -> list[_Bar]:
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
        if len(bars) == 0:
            return None
        dt_first_bar = bars[0].dt  # join_bar.dt будет как dt у первого bar-а
        bars = cls.__removeVoid(bars)  # удалим VoidBars
        # Собираем один общий бар
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


# }}}
