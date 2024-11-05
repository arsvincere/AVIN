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

from avin.config import Usr
from avin.const import ONE_DAY, ONE_WEEK
from avin.data._abstract_source import _AbstractDataSource
from avin.data._bar import _Bar, _BarsData
from avin.data._cache import _InstrumentsInfoCache
from avin.data.data_source import DataSource
from avin.data.data_type import DataType
from avin.data.exchange import Exchange
from avin.data.instrument import Instrument
from avin.keeper import Keeper
from avin.utils import Cmd, logger


class _MoexData(_AbstractDataSource):
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

    __SUB_DIR = "moex"
    __LOGIN = None
    __PASSWORD = None
    __AUTHORIZATION = None
    __AUTO_UPDATE = Usr.AUTO_UPDATE_ASSET_CACHE

    # }}}
    @classmethod  # cacheInstrumentsInfo  # {{{
    async def cacheInstrumentsInfo(cls) -> None:
        logger.debug(f"{cls.__name__}.cacheInstrumentsInfo()")

        if _InstrumentsInfoCache.checkCachingDate(cls.source):
            return

        logger.info(":: Caching instruments info from MOEX")
        if not await cls.__authorizate():
            return

        types = ["index", "shares", "currency", "futures"]
        for t in types:
            logger.info(f"  - caching {t}")
            response = cls.__requestAvailibleInstruments(t)
            original_info = cls.__originalInstrumentInfo(response)
            formatted_info = cls.__formatInstrumentInfo(response)
            itype = cls.__getStandartInstrumentType(t)
            cache = _InstrumentsInfoCache(
                cls.source,
                itype,
                original_info,
                formatted_info,
            )
            await _InstrumentsInfoCache.save(cache)

        _InstrumentsInfoCache.updateCachingDate(cls.source)

    # }}}
    @classmethod  # find  # {{{
    async def find(
        cls,
        exchange: Exchange,
        itype: Instrument.Type,
        ticker: str,
        figi: str,
        name: str,
    ) -> list[Instrument]:
        logger.debug(f"{cls.__name__}.find()")

        # check cache
        if cls.__AUTO_UPDATE:
            await _MoexData.cacheInstrumentsInfo()
            ...

        # request info
        instruments_info = await Keeper.info(
            cls.source,
            itype,
            exchange=exchange.name if exchange else None,
            ticker=ticker,
            figi=figi,
            name=name,
        )
        # for INDEXes:
        id_list = list()
        if itype == Instrument.Type.INDEX:
            for i in instruments_info:
                instrument = Instrument(i)
                id_list.append(instrument)
            return id_list

        # for other types, or None:
        # MOEX does not provide instruments 'figi',
        # load 'figi' and other from Tinkoff cache
        for i in instruments_info:
            tinkoff_info = await Keeper.info(
                DataSource.TINKOFF,
                itype=Instrument.Type.fromStr(i["type"]),
                exchange=Exchange.fromStr(i["exchange"]),
                ticker=i["ticker"],
            )
            if tinkoff_info:
                instrument = Instrument(tinkoff_info[0])
                id_list.append(instrument)
            else:
                # NOTE:
                # если у Тинька нет информации по активу, поторговать
                # им все равно пока не получится, так что просто
                # пропускаем этот актив
                pass

        return id_list

    # }}}
    @classmethod  # firstDateTime  # {{{
    async def firstDateTime(
        cls, instrument: Instrument, data_type: DataType
    ) -> datetime:
        logger.debug(f"{cls.__name__}.firstDateTime()")

        date_start = date(1990, 1, 1)
        try:
            asset = moexalgo.Ticker(instrument.ticker)
            candles = asset.candles(
                start=date_start,
                end="today",
                period=cls.__convert(data_type),
                use_dataframe=False,
            )
        except LookupError:
            logger.warning(
                f"_MoexData: no market data for {instrument.ticker}"
            )
            return None

        candle = candles.send(None)
        dt = candle.begin

        return cls.__toUTC(dt)

    # }}}
    @classmethod  # download  # {{{
    async def download(
        cls, instrument: Instrument, data_type: DataType, year: int
    ) -> None:
        logger.debug(f"{cls.__name__}.download()")
        assert data_type in cls.AVAILIBLE_DATA

        # Without authorization - delay is 15min
        # for authorized users delay is 2min
        await cls.__authorizate()

        logger.info(
            f":: Download {instrument.ticker}-{data_type.value} from {year}"
        )
        begin, end = cls.__getPeriod(year)
        candles = cls.__getHistoricalCandles(
            instrument, data_type, begin, end
        )
        if len(candles) == 0:
            logger.warning(
                f"No data received for {instrument.ticker}-{data_type.value}-{year}"
            )
            return

        bars = cls.__convertCandlesToBars(candles)
        data = _BarsData(cls.source, instrument, data_type, bars)
        await _BarsData.save(data)

    # }}}
    @classmethod  # getHistoricalBars  # {{{
    async def getHistoricalBars(
        cls,
        instrument: Instrument,
        data_type: DataType,
        begin: datetime,
        end: datetime,
    ) -> list[_Bar]:
        logger.debug(f"{cls.__name__}.getHistoricalBars()")

        if data_type not in cls.AVAILIBLE_DATA:
            logger.error(f"Can't update {instrument}-{data_type}")
            return list()

        # Without authorization - delay is more than 15min
        # for authorized users delay is 2-5 min
        await cls.__authorizate()

        begin = cls.__toMSK(begin)
        end = cls.__toMSK(end)

        candles = cls.__getHistoricalCandles(
            instrument, data_type, begin, end
        )
        bars = cls.__convert(candles)
        return bars

    # }}}
    @classmethod  # __authorizate  # {{{
    async def __authorizate(cls) -> None:
        logger.debug(f"{cls.__name__}.__authorizate()")

        if cls.__AUTHORIZATION:
            return True

        account_path = Cmd.path(Usr.CONNECT, cls.__SUB_DIR, Usr.MOEX_ACCOUNT)
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
            return False

        cls.__AUTHORIZATION = moexalgo.session.authorize(login, password)
        if cls.__AUTHORIZATION:
            _MoexData.__LOGIN = login
            _MoexData.__PASSWORD = password
            logger.info("MOEX Authorization successful")
            return True
        else:
            logger.warning(
                "MOEX authorization fault, check your login and password. "
                "Operations with real time market data unavailible. "
                f"Login='{login}' password='{password}'"
            )
            return False

    # }}}
    @classmethod  # __requestAvailibleInstruments# {{{
    def __requestAvailibleInstruments(cls, moex_type: str):
        logger.debug(f"{cls.__name__}.__requestAvailibleInstruments()")

        response = moexalgo.Market(moex_type).tickers(
            use_dataframe=False,
        )
        return response

    # }}}
    @classmethod  # __originalInstrumentInfo# {{{
    def __originalInstrumentInfo(cls, response) -> list[str]:
        logger.debug(f"{cls.__name__}.__originalInstrumentInfo()")

        original_info = list()
        for i in response:
            original_info.append(str(i))

        return original_info

    # }}}
    @classmethod  # __formatInstrumentInfo# {{{
    def __formatInstrumentInfo(cls, assets_info: list[dict]) -> list[dict]:
        logger.debug(f"{cls.__name__}.__formatInstrumentInfo()")

        formatted_info = list()
        for i in assets_info:
            info = {
                "name": i["SECNAME"] if i.get("SECNAME") else i["NAME"],
                "exchange": "MOEX",
                "exchange_specific": None,
                "type": cls.__getStandartInstrumentType(i["BOARDID"]).name,
                "ticker": i["SECID"],
                "figi": None,  # MOEX not provide instruments figi
                "uid": None,
                "lot": i.get("LOTSIZE", "0"),
                "min_price_step": i.get("MINSTEP", "0"),
                "short_enabled_flag": None,
                "klong": None,
                "kshort": None,
                "first_1m_bar_date": None,
                "first_d_bar_date": None,
                "trading_status": None,
                "trade_available_flag": None,
                "buy_available_flag": None,
                "sell_available_flag": None,
                "country": None,
                "currency": None,
                "class_code": None,
                "qual_investor_flag": None,
            }

            if i["BOARDID"] == "SNDX":
                # NOTE:
                # Indexes not have 'figi', but I'm use figi in class
                # Instrument - base identificator for all assets
                # for use search by figi, I'm add in to indices
                # not real global figi, its only my local idea,
                # figi = "_<exchane_name>_<ticker>"
                info["figi"] = f"_MOEX_{i['SECID']}"

            formatted_info.append(info)

        return formatted_info

    # }}}
    @classmethod  # __convert# {{{
    def __convert(cls, obj: object) -> Any:
        logger.debug(f"{cls.__name__}.__convert()")

        if isinstance(obj, DataType):
            return cls.__convertDataTypeToMoexPeriod(obj)
        elif isinstance(obj, list):
            return cls.__convertCandlesToBars(obj)
        else:
            assert False, f"unknown object type '{type(obj)}'"

    # }}}
    @classmethod  # __convertDataTypeToMoexPeriod# {{{
    def __convertDataTypeToMoexPeriod(cls, data_type: DataType) -> str:
        logger.debug(f"{cls.__name__}.__convertDataTypeToMoexPeriod()")

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
    def __convertCandlesToBars(cls, candles) -> list[_Bar]:
        logger.debug(f"{cls.__name__}.__convertCandlesToBars()")

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
        logger.debug(f"{cls.__name__}.__getPeriod()")

        begin = datetime(year, 1, 1)
        end = datetime(year + 1, 1, 1)
        if end >= datetime.now():
            end = datetime.now().replace(microsecond=0)
        return (begin, end)

    # }}}
    @classmethod  # __requestCandles# {{{
    def __requestCandles(
        cls,
        instrument: Instrument,
        data_type: DataType,
        begin: datetime,
        end: datetime,
    ) -> list[Candles]:
        logger.debug(f"{cls.__name__}.__requestCandles()")

        # PERF:
        # можно же сделать запрос по 10.000 баров.
        # начиная с бегин, и до тех пор пока меньше энд..
        # и не нужен будет этот геморой с small / big timeframe
        # и выкачивать быстрее будет

        # select method
        period = data_type.toTimeDelta()
        if period < ONE_DAY:
            method = cls.__requestCandlesSmallTimeFrame
        else:
            method = cls.__requestCandlesBigTimeFrame

        return method(instrument, data_type, begin, end)

    # }}}
    @classmethod  # __requestCandlesBigTimeFrame# {{{
    def __requestCandlesBigTimeFrame(
        cls,
        instrument: Instrument,
        data_type: DataType,
        begin: datetime,
        end: datetime,
    ) -> list[Candles]:
        logger.debug(f"{cls.__name__}.__requestCandlesBigTimeFrame()")

        all_candles = list()
        asset = moexalgo.Ticker(instrument.ticker)
        period = cls.__convert(data_type)
        current = begin

        while current < end:
            logger.info(
                f"  - request {instrument.ticker}-{data_type.value} {current.date()}"
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
    def __requestCandlesSmallTimeFrame(
        cls,
        instrument: Instrument,
        data_type: DataType,
        begin: datetime,
        end: datetime,
    ) -> list[Candles]:
        logger.debug(f"{cls.__name__}.__requestCandlesSmallTimeFrame()")

        all_candles = list()
        asset = moexalgo.Ticker(instrument.ticker)
        period = cls.__convert(data_type)
        current = begin
        while current < end:
            logger.info(
                f"  - request {instrument.ticker}-{data_type.value} "
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
        instrument: Instrument,
        data_type: DataType,
        begin: datetime,
        end: datetime,
    ) -> list[Candles]:
        logger.debug(f"{cls.__name__}.__getHistoricalCandles()")

        candles = cls.__requestCandles(instrument, data_type, begin, end)
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
        period = data_type.toTimeDelta()
        if period <= ONE_WEEK:
            last_candle_begin = candles[-1].begin
            last_candle_end = candles[-1].end
            if last_candle_end < last_candle_begin + period:
                candles.pop(-1)
            return candles

        assert False, "Тут мы никак не должны оказаться"

    # }}}
    @classmethod  # __toUTC# {{{
    def __toUTC(cls, moex_dt: datetime) -> datetime:
        logger.debug(f"{cls.__name__}.__toUTC()")

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
        logger.debug(f"{cls.__name__}.__toMSK()")

        # MOEX work with Moscow time, UTC+3, and use offset-naive datetime
        if utc_dt.hour != 0:
            return (utc_dt + cls.MSK_TIME_DIF).replace(tzinfo=None)
        else:
            # timeframe >= D, msk time = 00:00, only change timezone
            return utc_dt.replace(tzinfo=None)

    # }}}
    @classmethod  # __getStandartInstrumentType# {{{
    def __getStandartInstrumentType(cls, name: str) -> Instrument.Type:
        logger.debug(f"{cls.__name__}.__getStandartInstrumentType()")

        names = {
            "index": Instrument.Type.INDEX,
            "shares": Instrument.Type.SHARE,
            "futures": Instrument.Type.FUTURE,
            "currency": Instrument.Type.CURRENCY,
            "INDEX": Instrument.Type.INDEX,
            "SHARE": Instrument.Type.SHARE,
            "FUTURE": Instrument.Type.FUTURE,
            "CURRENCY": Instrument.Type.CURRENCY,
            "SNDX": Instrument.Type.INDEX,
            "TQBR": Instrument.Type.SHARE,
            "RFUD": Instrument.Type.FUTURE,
            "CETS": Instrument.Type.CURRENCY,
        }
        standart_asset_type = names[name]

        return standart_asset_type

    # }}}


if __name__ == "__main__":
    ...
