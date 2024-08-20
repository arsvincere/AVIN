#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

from __future__ import annotations

import tinkoff.invest as ti

from avin.const import Usr
from avin.data._cache import _InstrumentInfoCache
from avin.data.asset_type import AssetType
from avin.data.data_source import DataSource, _AbstractSource
from avin.data.data_type import DataType
from avin.data.exchange import Exchange
from avin.data.instrument_id import InstrumentId
from avin.keeper import Keeper
from avin.utils import Cmd


# TODO rename -> TinkoffSource
class _TinkoffData(_AbstractSource):  # {{{
    """const"""  # {{{

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

    _SUB_DIR = "tinkoff"
    _DOWNLOAD = Cmd.path(Usr.DOWNLOAD, _SUB_DIR)

    _TARGET = ti.constants.INVEST_GRPC_API
    _TOKEN_PATH = Usr.TINKOFF_TOKEN
    _TOKEN = None

    _AUTO_UPDATE = Usr.AUTO_UPDATE_ASSET_CACHE

    # }}}
    @classmethod  # cacheAssetsInfo# {{{
    async def cacheAssetsInfo(cls):
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
            await cls.cacheAssetsInfo()

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
