#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

from __future__ import annotations

import tinkoff.invest as ti

from avin.config import Auto, Usr
from avin.const import Res
from avin.data._abstract_source import _AbstractDataSource
from avin.data._cache import _InstrumentsInfoCache
from avin.data.data_source import DataSource
from avin.data.data_type import DataType
from avin.data.exchange import Exchange
from avin.data.instrument import Instrument
from avin.keeper import Keeper
from avin.utils import Cmd, logger


class _TinkoffData(_AbstractDataSource):
    source = DataSource.TINKOFF

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

    __SUB_DIR = "tinkoff"
    __DOWNLOAD = Cmd.path(Res.DOWNLOAD, __SUB_DIR)
    __TARGET = ti.constants.INVEST_GRPC_API
    __TOKEN_PATH = Usr.TINKOFF_TOKEN
    __TOKEN = None
    __AUTO_UPDATE = Auto.UPDATE_ASSET_CACHE

    @classmethod  # cacheInstrumentsInfo# {{{
    async def cacheInstrumentsInfo(cls) -> None:
        logger.debug(f"{cls.__name__}.cacheInstrumentsInfo()")

        if _InstrumentsInfoCache.checkCachingDate(cls.source):
            return

        logger.info(":: Caching assets info from Tinkoff")
        if not await cls.__authorizate():
            return

        types = ["shares", "bonds", "futures", "currencies"]
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

        if cls.__AUTO_UPDATE:
            await cls.cacheInstrumentsInfo()

        # request instruments info
        instruments_info = await Keeper.info(
            cls.source,
            itype,
            exchange=exchange.name if exchange else None,
            ticker=ticker,
            figi=figi,
            name=name,
        )

        # create Instrument objects
        instr_list = list()
        for i in instruments_info:
            instrument = Instrument(i)
            instr_list.append(instrument)

        return instr_list

    # }}}
    @classmethod  # firstDateTime  # {{{
    async def firstDateTime(
        cls, instrument: Instrument, data_type: DataType
    ) -> datetime:
        logger.debug(f"{cls.__name__}.firstDateTime()")

        if data_type.value == "1M":
            return instrument.info["first_1m_bar_date"]
        elif data_type.value == "D":
            return instrument.info["first_d_bar_date"]

    # }}}
    @classmethod  # download  # {{{
    async def download(
        cls, instrument: Instrument, data_type: DataType, year: int
    ) -> None:
        logger.debug(f"{cls.__name__}.download()")
        assert False, "переписать на postgres, пока качаю только с МОЕКС"

        assert data_type.value == "1M"
        auth = await cls.__authorizate()
        if not auth:
            return

        logger.info(
            f":: Download {instrument.ticker}-{data_type.value} from {year}"
        )
        cls.__requestHistoricalData(instrument, year)

    # }}}
    @classmethod  # export  # {{{
    async def export(cls) -> None:
        logger.debug(f"{cls.__name__}.export()")
        assert False, "переписать на postgres, пока качаю только с МОЕКС"

        # FIX: - not exclude holidays files
        logger.info(":: Tinkoff exporting data in standart format")
        files = Cmd.getFiles(
            cls.__DOWNLOAD, full_path=True, include_sub_dir=True
        )
        archives = sorted(Cmd.select(files, extension=".zip"))

        for archive in archives:
            logger.info(f"  - exporting '{archive}'")
            tmp_dir = Cmd.path(Dir.TMP, cls.__SUB_DIR)
            Cmd.extract(archive, tmp_dir)

            bars = cls.__loadDataDir(tmp_dir)
            instrument, data_type = cls.__parseFileName(Cmd.name(archive))

            data = _BarsData(instrument, data_type, bars, Source.TINKOFF)
            _BarsData.save(data)

            Cmd.deleteDir(tmp_dir)

        logger.info("Export complete")

    # }}}
    @classmethod  # clear  # {{{
    async def clear(cls) -> None:
        logger.debug(f"{cls.__name__}.clear()")
        assert False, "переписать на postgres, пока качаю только с МОЕКС"

        logger.info(":: Clear Tinkoff files")
        path = cls.__DOWNLOAD
        if not Cmd.isExist(path):
            logger.info(f"  - no data in '{path}'")
            return
        Cmd.deleteDir(path)
        logger.info("  - successful complete")

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
        assert False, "переписать на postgres, пока качаю только с МОЕКС"

        if data_type not in cls.AVAILIBLE_DATA:
            logger.error(f"Can't update {instrument}-{data_type}")
            return

        logger.info(
            f"  - request {instrument.ticker}-{data_type.value} from {begin.date()}"
        )

        if not cls.__authorizate():
            return

        new_bars = list()
        with ti.Client(cls.__TOKEN) as client:
            try:
                candles = client.get_all_candles(
                    figi=instrument.figi,
                    from_=begin,
                    to=end,
                    interval=cls.__CandleIntervalFromTimeFrame(data_type),
                )
                for candle in candles:
                    if candle.is_complete:
                        bar = cls.__toBar(candle)
                        new_bars.append(bar)
            except ti.exceptions.RequestError as err:
                logger.exception(err)
                return list()
            return new_bars

    # }}}
    @classmethod  # __authorizate# {{{
    async def __authorizate(cls) -> bool:
        logger.debug(f"{cls.__name__}.__authorizate()")

        # if cls.__TOKEN is not None, then it's valid token
        if cls.__TOKEN is not None:
            return True

        # check token file
        if not Cmd.isExist(cls.__TOKEN_PATH):
            logger.warning(
                "Tinkoff not exist token file, operations with market data "
                "and orders unavailible. Make a token and put it in a "
                f"'{cls.__TOKEN_PATH}'. Read more about token: "
                "https://developer.tinkoff.ru/docs/intro/"
                "manuals/self-service-auth"
            )
            return False

        # read token from file, and try to connect
        token = Cmd.read(cls.__TOKEN_PATH).strip()
        try:
            with ti.Client(token) as client:
                response = client.users.get_accounts()
                if response:
                    cls.__TOKEN = token
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
    @classmethod  # __requestAvailibleInstruments# {{{
    def __requestAvailibleInstruments(cls, tinkoff_type: str):
        logger.debug(f"{cls.__name__}.__requestAvailibleInstruments()")

        # tinkoff_type must be availible for tinkoff invest API
        # for example: "shares", "bonds", "futures", "currencies"...
        with ti.Client(cls.__TOKEN) as client:
            all_info = list()
            method = getattr(client.instruments, tinkoff_type)
            response: list[ti.Instrument] = method().instruments
            # response: list[ti.Instrument] = getattr(
            #     client.instruments, tinkoff_type
            # )().instruments
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
    def __formatInstrumentInfo(cls, response: list[ti.Instrument]) -> dict:
        logger.debug(f"{cls.__name__}.__formatInstrumentInfo()")

        formatted_info = list()
        for i in response:
            info = cls.__extractInfoFromResponse(i)

            # skip None exchange
            if info["exchange"] is None:
                continue

            formatted_info.append(info)

        return formatted_info

    # }}}
    @classmethod  # __extractInfoFromResponse  # {{{
    def __extractInfoFromResponse(cls, instr: ti.Instrument) -> dict:
        logger.debug(f"{cls.__name__}.__extractInfoFromResponse()")

        # define short alias
        to_decimal = ti.utils.quotation_to_decimal
        ti_status = ti.SecurityTradingStatus

        # create instrument info dict
        info = {
            # NOTE:
            # "name": "O'Key Group SA", и другие подобные
            # одинарная кавчка потом мешается при преобразовании
            # в postgres тип "jsonb"
            "name": instr.name.replace("'", ""),  # remove ' in name
            "exchange": cls.__getStandartExchangeName(instr.exchange),
            "exchange_specific": instr.exchange,  # original exchange name
            "type": None,  # set below in this function
            "ticker": instr.ticker,
            "figi": instr.figi,
            "uid": instr.uid,
            "lot": instr.lot,
            "min_price_step": float(to_decimal(instr.min_price_increment)),
            "short_enabled_flag": instr.short_enabled_flag,
            "klong": float(to_decimal(instr.klong)),
            "kshort": float(to_decimal(instr.kshort)),
            "first_1m_bar_date": instr.first_1min_candle_date,
            "first_d_bar_date": instr.first_1day_candle_date,
            "trading_status": ti_status(instr.trading_status).name,
            "trade_available_flag": instr.api_trade_available_flag,
            "buy_available_flag": instr.buy_available_flag,
            "sell_available_flag": instr.sell_available_flag,
            "country": instr.country_of_risk,
            "currency": instr.currency,
            "class_code": instr.class_code,
            "qual_investor_flag": instr.for_qual_investor_flag,
        }

        # save attributes "isin" & "sector", if availible
        if hasattr(instr, "isin"):
            info["isin"] = instr.isin
        if hasattr(instr, "sector"):
            info["sector"] = instr.sector

        # set standart instrument type
        if isinstance(instr, ti.Share):
            info["type"] = Instrument.Type.SHARE.name
        elif isinstance(instr, ti.Bond):
            info["type"] = Instrument.Type.BOND.name
        elif isinstance(instr, ti.Future):
            info["type"] = Instrument.Type.FUTURE.name
        elif isinstance(instr, ti.Currency):
            info["type"] = Instrument.Type.CURRENCY.name
        else:
            print(instr)
            assert False, "Unknown instrument type"

        return info

    # }}}
    @classmethod  # __requestHistoricalData# {{{
    def __requestHistoricalData(cls, instrument: Instrument, year: int):
        logger.debug(f"{cls.__name__}.__requestHistoricalData()")

        exchange = instrument.exchange.name
        type_ = instrument.type.name
        figi = instrument.figi
        ticker = instrument.ticker
        file_name = f"{exchange}-{type_}-{ticker}-1M-{year}.zip"
        file_path = Cmd.path(cls.__DOWNLOAD, type_, ticker, file_name)
        data_url = "https://invest-public-api.tinkoff.ru/history-data"

        bash_command = (
            f"curl -s --location '{data_url}?figi={figi}&year={year}' "
            f"-H 'Authorization: Bearer {cls.__TOKEN}' "
            f"-o {file_name} "
        )
        os.system(bash_command)

        if Cmd.isExist(file_name):
            Cmd.replace(file_name, file_path)
            logger.info(f"  - saved {file_path}")

    # }}}
    @classmethod  # __loadDataDir# {{{
    def __loadDataDir(cls, dir_path):
        logger.debug(f"{cls.__name__}.__loadDataDir()")

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
        logger.debug(f"{cls.__name__}.__excludeHolidaysFiles()")

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
        logger.debug(f"{cls.__name__}.__excludeHolidaysBars()")

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
        logger.debug(f"{cls.__name__}.__readTinkoffFile()")

        tinkoff_bars = list()
        text = Cmd.loadText(file_path)
        for line in text:
            bar = cls.__parseLineTinkoff(line)
            tinkoff_bars.append(bar)
        return tinkoff_bars

    # }}}
    @classmethod  # __parseLineTinkoff# {{{
    def __parseLineTinkoff(cls, line):
        logger.debug(f"{cls.__name__}.__parseLineTinkoff()")

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
    @classmethod  # __CandleIntervalFromTimeFrame# {{{
    def __CandleIntervalFromTimeFrame(
        cls, data_type: DataType
    ) -> ti.CandleInterval:
        logger.debug(f"{cls.__name__}.__CandleIntervalFromTimeFrame()")

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
        logger.debug(f"{cls.__name__}.__toBar()")

        opn = float(ti.utils.quotation_to_decimal(candle.open))
        cls = float(ti.utils.quotation_to_decimal(candle.close))
        hgh = float(ti.utils.quotation_to_decimal(candle.high))
        low = float(ti.utils.quotation_to_decimal(candle.low))
        vol = candle.volume
        dt = candle.time
        bar = _Bar(dt, opn, hgh, low, cls, vol)
        return bar

    # }}}
    @classmethod  # __getStandartInstrumentType# {{{
    def __getStandartInstrumentType(cls, name: str) -> Instrument.Type:
        logger.debug(f"{cls.__name__}.__getStandartInstrumentType()")

        names = {
            "shares": Instrument.Type.SHARE,
            "bonds": Instrument.Type.BOND,
            "futures": Instrument.Type.FUTURE,
            "currencies": Instrument.Type.CURRENCY,
        }
        standart_asset_type = names[name]
        return standart_asset_type

    # }}}
    @classmethod  # __getStandartExchangeName# {{{
    def __getStandartExchangeName(cls, name: str) -> str | None:
        logger.debug(f"{cls.__name__}.__getStandartExchangeName()")

        if "MOEX" in name.upper():
            # values as "MOEX_PLUS", "MOEX_WEEKEND".. set "echange"="MOEX"
            standart_exchange_name = "MOEX"
        elif "SPB" in name.upper():
            # values as "SPB_RU_MORNING"... set "echange"="SPB"
            standart_exchange_name = "SPB"
        elif "FORTS" in name.upper():
            # NOTE:
            # FUTURE - у них биржа указана FORTS_EVENING, но похеру
            # пока для простоты ставлю им тоже биржу MOEX
            standart_exchange_name = "MOEX"
        elif name == "FX":
            # NOTE:
            # CURRENCY - у них биржа указана FX, но похеру
            # пока для простоты ставлю им тоже биржу MOEX
            standart_exchange_name = "MOEX"
        else:
            # NOTE:
            # там всякая странная хуйня еще есть в биржах
            # "otc_ncc", "LSE_MORNING", "moex_close", "Issuance",
            # "unknown"...
            # Часть из них по факту американские биржи, по которым сейчас
            # один хрен торги не доступны, другие хз, внебирживые еще, я всем
            # этим не торгую, поэтому сейчас ставим всем непонятным активам
            # биржу None, а потом перед сохранением делаем фильтр
            # если биржа None - отбрасываем этот ассет из кэша
            standart_exchange_name = None

        return standart_exchange_name

    # }}}
    @classmethod  # __parseFileName# {{{
    def __parseFileName(cls, file_name):
        logger.debug(f"{cls.__name__}.__getStandartInstrumentType()")

        exchange, itype, ticker, data_type, _ = file_name.split("-")

        exchange = Exchange.fromStr(exchange)
        itype = Instrument.Type.fromStr(itype)
        data_type = DataType.fromStr(data_type)

        # FIXME выпилить вызов фасадного класса..
        # заменить вызовом кипера
        instrument = Data.find(exchange, itype, ticker)

        return instrument, data_type

    # }}}


if __name__ == "__main__":
    ...
