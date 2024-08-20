#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

from __future__ import annotations

from datetime import UTC, date, datetime, time, timedelta

import moexalgo

from avin.const import ONE_DAY, ONE_WEEK, Usr
from avin.data._cache import _InstrumentInfoCache
from avin.data._data_bar import _Bar, _BarsData
from avin.data.asset_type import AssetType
from avin.data.data_source import DataSource, _AbstractSource
from avin.data.data_type import DataType
from avin.data.exchange import Exchange
from avin.data.instrument_id import InstrumentId
from avin.keeper import Keeper
from avin.logger import logger
from avin.utils import Cmd


# TODO rename -> MoexSource
class _MoexData(_AbstractSource):  # {{{
    """const"""  # {{{

    source = DataSource.MOEX

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

    # }}}
    @classmethod  # cacheAssetsInfo  # {{{
    async def cacheAssetsInfo(cls):
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
            await _MoexData.cacheAssetsInfo()
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
        # Without authorization - delay is more than 15min
        # for authorized users delay is 2-4 min
        await cls.__authorizate()

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
        # TODO
        # можно же сделать запрос по 10.000 баров.
        # начиная с бегин, и до тех пор пока меньше энд..
        # и не нужен будет этот геморой с small / big timeframe
        # и выкачивать быстрее будет
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
