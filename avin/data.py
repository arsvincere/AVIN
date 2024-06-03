#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

from __future__ import annotations
import os
import sys
import abc
import enum
import moexalgo
import tinkoff.invest
import pandas as pd
from dataclasses import dataclass
from datetime import datetime, time, date, timedelta
from avin.const import *
from avin.logger import logger
from avin.utils import Cmd, now
sys.path.append("/home/alex/AVIN")
sys.path.append("/home/alex/AVIN/env/lib/python3.12/site-packages")

__all__ = ("Data", "Source", "DataType", "Exchange", "AssetType", "Id")

#TODO:# {{{
# import gettext
# domain = "messages"
# localedir = "/home/alex/ya/arsvincere/lang"
# gettext.install(domain, localedir=localedir, names="gettext")


#TODO fix - not exclude holidays files on update data from tinkoff
# }}}


class Source(enum.Enum):# {{{
    UNDEFINE    = 0
    MOEX        = 1
    TINKOFF     = 2

    @staticmethod  #save# {{{
    def save(source: Source, file_path: str):
        string = source.name
        Cmd.write(string, file_path)
    # }}}
    @staticmethod  #load# {{{
    def load(file_path):
        string = Cmd.read(file_path).strip()
        sources = {
            "UNDEFINE": Source.UNDEFINE,
            "MOEX":     Source.MOEX,
            "TINKOFF":  Source.TINKOFF,
            }
        return sources[string]
    # }}}
# }}}
class DataType(enum.Enum):# {{{
    """ doc# {{{
    This is extension of class <DataType> with some utils for work with data.

    The <DataType> class is needed only to hide the methods below from the
    user. Making these methods simply private methods of class DataType made
    things more difficult since they are called by other classes. Making them
    protected is not logical, because no one inherits the enumeration.
    Therefore, a separate class DataType was made.

    While the class <DataType> - public enum for user to selet what data
    type want to download.
    """
    # }}}
    BAR_1M      = "1M"
    BAR_5M      = "5M"
    BAR_10M     = "10M"
    BAR_1H      = "1H"
    BAR_D       = "D"
    BAR_W       = "W"
    BAR_M       = "M"
    TIC         = "tic"
    BOOK        = "book"
    ANALYSE     = "analyse"

    def __hash__(self):# {{{
        return hash(self.name)
    # }}}
    def toTimedelta(self):# {{{
        periods = {
            "1M":  timedelta(minutes=1),
            "5M":  timedelta(minutes=5),
            "10M": timedelta(minutes=10),
            "1H":  timedelta(hours=1),
            "D":   timedelta(days=1),
            "W":   timedelta(weeks=1),
            "M":   timedelta(days=30),
            }
        return periods[self.value]
    # }}}
    @staticmethod  #save# {{{
    def save(data_type, file_path):
        string = data_type.value
        Cmd.write(string, file_path)
    # }}}
    @staticmethod  #load# {{{
    def load(file_path):
        string = Cmd.read(file_path).strip()
        data_type = DataType.fromStr(string)
        return data_type
    # }}}
    @staticmethod  #fromStr#{{{
    def fromStr(string_type: str):
        types = {
            "1M":       DataType.BAR_1M,
            "5M":       DataType.BAR_5M,
            "10M":      DataType.BAR_10M,
            "1H":       DataType.BAR_1H,
            "D":        DataType.BAR_D,
            "W":        DataType.BAR_W,
            "M":        DataType.BAR_M,
            "book":     DataType.BOOK,
            "tic":      DataType.TIC,
            "analyse":  DataType.ANALYSE
            }
        return types[string_type]
    # }}}
# }}}
class Exchange(enum.Enum):# {{{
    UNDEFINE    = 0
    MOEX        = 1
    SPB         = 2

    @staticmethod  #fromStr# {{{
    def fromStr(string):
        types = {
            "UNDEFINE": Exchange.UNDEFINE,
            "MOEX":     Exchange.MOEX,
            "SPB":      Exchange.SPB,
            }
        return types[string]
    # }}}
# }}}
class AssetType(enum.Enum):# {{{
    UNDEFINE    = 0
    Index       = 1
    Share       = 2
    Bond        = 3
    Future      = 4
    Currency    = 5
    Etf         = 6

    @staticmethod  #fromStr# {{{
    def fromStr(string):
        types = {
            "UNDEFINE": AssetType.UNDEFINE,
            "Index":    AssetType.Index,
            "Share":    AssetType.Share,
            "Bond":     AssetType.Bond,
            "Future":   AssetType.Future,
            "Currency": AssetType.Currency,
            "Etf":      AssetType.Etf,
            }
        return types[string]
    # }}}
# }}}
class Id():# {{{
    """ doc # {{{
    Unified identifier for all assets.

    Constructor trying to find asset by 'querry', then create 'Id' object with
    fully information of this instrument: exchange, type, name, ticker, figi,
    uid are availible as property. Other information: min price step, lots,
    last price, etc.. loading on call.

    Args:
        exchange (str): short name like "MOEX", "SPB", "NASDAQ"...
        asset_type (str): availible: "Index", "Share", "Bond"...
        querry (str): ticker | figi | uid

    Attributes:
        exchange: str
        type: str
        name: str
        ticker: str
        figi: str
        uid: str

    Examples:
        >>> Id("MOEX", "Share", "SBER")
        >>> Id("MOEX", "Share", "BBG004S683W7")
        >>> Id("MOEX", "Share", "962e2a95-02a9-4171-abd7-aa198dbe643a"
        >>> Id("MOEX", "Index", "IMOEX"

    Availible exchange:
        MOEX,

    Availible asset type:
        Index, Share, Bond, Future, Currency, Etf

    Availible querry:
        ticker: for example "GAZP", "ROSN", "YNDX"
        figi: for example "BBG004S683W7", "BBG004730N88"
        tinkoff uid: for example "10e17a87-3bce-4a1f-9dfc-720396f98a3c"
    """
# }}}
    def __init__(# {{{
        self,
        exchange: Exchange,
        asset_type: AssetType,
        name: str,
        ticker: str,
        figi: str,
        ):

        self.__info = {
            "exchange": exchange,
            "type": asset_type,
            "name": name,
            "ticker": ticker,
            "figi": figi,
            }
        # }}}
    def __str__(self):# {{{
        s = f"{self.exchange.name}-{self.type.name}-{self.ticker}-{self.figi}"
        return s
        # }}}
    def __eq__(self, other):# {{{
        return self.__info == other.__info
    # }}}
    @property  #exchange# {{{
    def exchange(self):
        return self.__info["exchange"]
        # }}}
    @property  #type# {{{
    def type(self):
        return self.__info["type"]
        # }}}
    @property  #name# {{{
    def name(self):
        return self.__info["name"]
        # }}}
    @property  #ticker# {{{
    def ticker(self):
        return self.__info["ticker"]
        # }}}
    @property  #figi# {{{
    def figi(self):
        return self.__info["figi"]
        # }}}
    @property  #dir_path# {{{
    def dir_path(self):
        path = Cmd.path(
            Usr.DATA, self.exchange.name, self.type.name, self.ticker
            )
        return path
        # }}}
    @classmethod  #save# {{{
    def save(cls, ID: Id, file_path: str):
        Cmd.saveJson(ID, file_path, Id._encoderJson)
        # }}}
    @classmethod  #load# {{{
    def load(cls, file_path):
        obj = Cmd.loadJson(file_path, Id._decoderJson)
        ID = Id(
            obj["exchange"],
            obj["type"],
            obj["name"],
            obj["ticker"],
            obj["figi"],
            )
        return ID
        # }}}
    @staticmethod  #_encoderJson# {{{
    def _encoderJson(obj):
        if isinstance(obj, (Id)):
            return obj.__info
        if isinstance(obj, (Exchange, AssetType)):
            return obj.name
    # }}}
    @staticmethod  #_decoderJson# {{{
    def _decoderJson(obj):
        # TODO: encoder and decoder - вынести в классы потомки,
        # см формат файлов кэша, там слишком много деталей спецефичных
        # сейчас даты в MOEX файлах после чтения остаются строками:
        # "SETTLEDATE": "2024-05-31"
        # "LASTTRADEDATE": "2025-03-20",
        # "LASTDELDATE": "2025-03-20",
        # "IMTIME": "2024-05-29T18:58:11",
        # возможное решение - при сохранении все эти поля проверять и
        # переводить в UTC datetime
        for k, v in obj.items():
            if k == "exchange":
                obj[k] = Exchange.fromStr(v)
            if k == "type":
                obj[k] = AssetType.fromStr(v)
        return obj
    # }}}
# }}}
class Data():# {{{
    @classmethod  #assets # {{{
    def assets(cls, source: Source, asset_type: AssetType) -> list[Id]:
        check = cls.__checkArgs(
            source=     source,
            asset_type= asset_type
            )
        if check:
            source = cls.__getSource(source)
            return source.assets(asset_type)
    # }}}
    @classmethod  #find# {{{
    def find(
        cls,
        exchange: Exchange,
        asset_type: AssetType,
        querry: str
        ) -> Id:

        check = cls.__checkArgs(
            exchange=   exchange,
            asset_type= asset_type,
            querry=     querry,
            )
        if not check:
            return None

        if exchange == Exchange.MOEX and asset_type == AssetType.Index:
            md = _MoexData()
            return md.find(exchange, asset_type, querry)
        else:
            td = _TinkoffData()
            return td.find(exchange, asset_type, querry)
    # }}}
    @classmethod  #info# {{{
    def info(cls, ID: Id) -> dict:
        check = cls.__checkArgs(
            ID= ID
            )
        if not check:
            return None

        if ID.exchange == Exchange.MOEX and ID.type == AssetType.Index:
            md = _MoexData()
            return md.info(ID)
        else:
            td = _TinkoffData()
            return td.info(ID)
    # }}}
    @classmethod  #firstDateTime# {{{
    def firstDateTime(cls, source: Source, data_type: Type, ID: Id) -> datetime:
        check = cls.__checkArgs(
            source=     source,
            ID=         ID,
            data_type=  data_type,
            )
        if not check:
            return None

        if data_type.value not in ["1M", "D"]:
            logger.error("First datetime availible only for '1M' and 'D'")
            return None

        source = cls.__getSource(source)
        dt = source.firstDateTime(ID, data_type)
        return dt
    # }}}
    @classmethod  #download# {{{
    def download(
        cls, source: Source, data_type: DataType, ID: Id, year: int
        ) -> bool:

        check = cls.__checkArgs(
            source=     source,
            ID=         ID,
            data_type=  data_type,
            year=       year
            )
        if check:
            source = cls.__getSource(source)
            source.download(ID, data_type, year)
            return True
        return False
    # }}}
    @classmethod  #add# {{{
    def add(cls, source: Source) -> bool:
        check = cls.__checkArgs(
            source=     source,
            )
        if check:
            source = cls.__getSource(source)
            source.export()
            return True
        return False
    # }}}
    @classmethod  #convert# {{{
    def convert(cls, ID: Id, in_type: Type, out_type: Type) -> bool:
        check = cls.__checkArgs(
            ID=         ID,
            in_type=    in_type,
            out_type=   out_type
            )
        if not check:
            return False

        if in_type.toTimedelta() > out_type.toTimedelta():
            logger.error(
                f"You're still a stupid monkey, how the fuck do you convert "
                f"'{in_type}' to '{out_type}'?"
                )
            return False

        _Manager.convert(ID, in_type, out_type)
        return True
    # }}}
    @classmethod  #clear# {{{
    def clear(cls, source: Source) -> bool:
        check = cls.__checkArgs(
            source=     source,
            )
        if check:
            source = cls.__getSource(source)
            source.clear()
            return True
        return False
    # }}}
    @classmethod  #delete# {{{
    def delete(cls, ID: Id, data_type: Type) -> bool:
        check = cls.__checkArgs(
            ID=         ID,
            data_type=  data_type,
            )
        if check:
            if data_type == DataType.BOOK:
                assert False
            elif data_type == DataType.TIC:
                assert False
            else:
                _Manager.delete(ID, data_type)
                return True
        return False
    # }}}
    @classmethod  #update# {{{
    def update(cls, ID: Id, data_type: Type=None) -> bool:
        assert ID.exchange == Exchange.MOEX
        assert data_type != DataType.TIC
        assert data_type != DataType.BOOK
        check = cls.__checkArgs(
            ID=         ID,
            data_type=  data_type,
            )
        if check:
            data_type = DataType(data_type)
            _Manager.update(ID, data_type)
            return True
    # }}}
    @classmethod  #updateAll# {{{
    def updateAll(cls) -> bool:
        _Manager.updateAll()
    # }}}
    @classmethod  #request# {{{
    def request(
        cls,
        ID: Id,
        data_type: DataType,
        begin: int,
        end: int,
        ) -> list[file_path]:

        check = cls.__checkArgs(
            ID=         ID,
            data_type=  data_type,
            begin=      begin,
            end=        end,
            )

        if check:
            if data_type == DataType.BOOK:
                assert False
            elif data_type == DataType.TIC:
                assert False
            else:
                bars = _Manager.request(
                    ID, data_type, begin, end
                    )
                return bars
    # }}}
    @classmethod  #__checkArgs# {{{
    def __checkArgs(
        cls,
        source= None,
        exchange = None,
        asset_type = None,
        querry = None,
        ID= None,
        data_type= None,
        year= None,
        in_type= None,
        out_type= None,
        begin= None,
        end= None,
        decoder= None,
        requester= None
        ):
        if source:
            cls.__checkSource(source)
        if exchange:
            cls.__checkExchange(exchange)
        if asset_type:
            cls.__checkAssetType(asset_type)
        if querry:
            cls.__checkQuerry(querry)
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
        if decoder or requester:
            cls.__checkDecoderRequester(decoder, requester)
        return True
    # }}}
    @classmethod  #__checkSource# {{{
    def __checkSource(cls, source):
        if not isinstance(source, Source):
            raise TypeError(
                "You stupid monkey, select the 'source' from the enum "
                "Source."
                )
    # }}}
    @classmethod  #__checkExchange# {{{
    def __checkExchange(cls, exchange):
        if not isinstance(exchange, Exchange):
            raise TypeError(
                "You stupid monkey, select the 'exchange' from the enum "
                "Exchange."
                )
    # }}}
    @classmethod  #__checkAssetType# {{{
    def __checkAssetType(cls, asset_type):
        if not isinstance(asset_type, AssetType):
            raise TypeError(
                "You stupid monkey, select the 'asset_type' from the enum "
                "AssetType."
                )
    # }}}
    @classmethod  #__checkTicker# {{{
    def __checkQuerry(cls, querry):
        if not isinstance(querry, str):
            raise TypeError(
                "You stupid monkey, use type str for argument 'querry'"
                )
    # }}}
    @classmethod  #__checkID# {{{
    def __checkID(cls, ID):
        if not isinstance(ID, Id):
            raise TypeError(
                "You stupid monkey, use type Id for argument 'ID'"
                )
    # }}}
    @classmethod  #__checkDataType# {{{
    def __checkDataType(cls, data_type):
        assert data_type != DataType.BOOK
        assert data_type != DataType.TIC
        if not isinstance(data_type, DataType):
            raise TypeError(
                "You stupid monkey, select the 'data_type' from the enum "
                "DataType."
                )
    # }}}
    @classmethod  #__checkYear# {{{
    def __checkYear(cls, year):
        if not isinstance(year, int):
            raise TypeError(
                "You stupid monkey, use type int for argument 'year'"
                )
    # }}}
    @classmethod  #__checkIOType# {{{
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
    @classmethod  #__checkBeginEnd# {{{
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
    @classmethod  #__getSource# {{{
    def __getSource(cls, source: Source) -> object:
        classes = {
            Source.MOEX:       _MoexData,
            Source.TINKOFF:    _TinkoffData
            }
        class_ = classes.get(source, None)
        obj = class_()
        return obj
    # }}}
# }}}

@dataclass  #_Bar# {{{
class _Bar():
    """ init """# {{{
    dt:     datetime | str
    open:   float
    high:   float
    low:    float
    close:  float
    vol:    int
    # }}}
    def __post_init__(self):# {{{
        if isinstance(self.dt, str):
            self.dt = datetime.fromisoformat(self.dt)
    # }}}
    @classmethod  #toCSV# {{{
    def toCSV(cls, bar):
        dt = bar.dt.isoformat()
        s = f"{dt};{bar.open};{bar.high};{bar.low};{bar.close};{bar.vol}"
        return s
    # }}}
    @classmethod  #fromCSV# {{{
    def fromCSV(cls, string, requester=None):
        DT, OPEN, HIGH, LOW, CLOSE, VOLUME = range(6)
        fields = string.split(";")
        bar = _Bar(
            dt=     datetime.fromisoformat(fields[DT]),
            open=   float(fields[OPEN]),
            high=   float(fields[HIGH]),
            low=    float(fields[LOW]),
            close=  float(fields[CLOSE]),
            vol=    int(fields[VOLUME])
            )
        return bar
    # }}}
# }}}
class _BarsDataFile():# {{{
    def __init__(# {{{
            self,
            ID: Id,
            data_type: DataType,
            bars: list[_Bar],
            source: Source,
            ):
        assert bars[0].dt.year == bars[-1].dt.year
        self.__ID = ID
        self.__data_type = data_type
        self.__bars = bars
        self.__source = source
    # }}}
    @property  #ID# {{{
    def ID(self):
        return self.__ID
    # }}}
    @property  #data_type# {{{
    def data_type(self):
        return self.__data_type
    # }}}
    @property  #bars# {{{
    def bars(self):
        return self.__bars
    # }}}
    @property  #source# {{{
    def source(self):
        return self.__source
    # }}}
    @property  #first_dt# {{{
    def first_dt(self):
        dt = self.bars[0].dt
        return dt
    # }}}
    @property  #last_dt# {{{
    def last_dt(self):
        dt = self.bars[-1].dt
        return dt
    # }}}
    @property  #year# {{{
    def year(self):
        y = self.bars[-1].dt.year
        return y
    # }}}
    @property  #dir_path# {{{
    def dir_path(self):
        dir_path = Cmd.path(self.__ID.dir_path, str(self.data_type.value))
        Cmd.makeDirs(dir_path)
        return dir_path
    # }}}
    def add(self, new_bars: list[_Bar]):# {{{
        assert new_bars[-1].dt.year == self.year
        self.__bars += new_bars
    # }}}
    @classmethod  #save# {{{
    def save(cls, data):
        logger.debug(f"{cls.__name__}.save({data.ID.ticker})")
        cls.__saveID(data)
        cls.__saveDataType(data)
        cls.__saveBars(data)
        cls.__saveSource(data)
    # }}}
    @classmethod  #load# {{{
    def load(
            cls, ID: Id, data_type: DataType, year: int
            ) -> _BarsDataFile:
        bars = cls.__loadBars(ID, data_type, year)
        source = cls.__loadSource(ID, data_type)
        data = _BarsDataFile(ID, data_type, bars, source)
        return data
    # }}}
    @classmethod  #__saveID# {{{
    def __saveID(cls, data: _BarsDataFile):
        path = Cmd.path(data.dir_path, "id")
        Id.save(data.ID, path)
    # }}}
    @classmethod  #__saveDataType# {{{
    def __saveDataType(cls, data):
        path = Cmd.path(data.dir_path, "data_type")
        Cmd.write(data.data_type.value, path)
    # }}}
    @classmethod  #__saveBars# {{{
    def __saveBars(cls, data):
        text = list()
        for bar in data.__bars:
            line = _Bar.toCSV(bar) + "\n"
            text.append(line)
        year = data.bars[0].dt.year
        file_path = Cmd.path(data.dir_path, f"{year}.csv")
        Cmd.saveText(text, file_path)
    # }}}
    @classmethod  #__saveSource# {{{
    def __saveSource(cls, data: _BarsDataFile):
        file_path = Cmd.path(data.dir_path, "source")
        Source.save(data.source, file_path)
    # }}}
    @classmethod  #__loadID# {{{
    def __loadID(cls, path, parent=None):
        ID = Id.load(path)
        return ID
    # }}}
    @classmethod  #__loadDataType# {{{
    def __loadDataType(cls, path, parent=None):
        data_type = DataType.load(path)
        return data_type
    # }}}
    @classmethod  #__loadBars# {{{
    def __loadBars(
            cls, ID: Id, data_type: DataType, year: int
            ) -> _BarsDataFile:
        file_path = Cmd.path(ID.dir_path, data_type.value, f"{year}.csv")
        if not Cmd.isExist(file_path):
            logger.error(
                f"No csv data: {ID.ticker}-{data_type.value} {year}"
                )
            return list()
        text = Cmd.loadText(file_path)
        bars = list()
        for line in text:
            bar = _Bar.fromCSV(line)
            bars.append(bar)
        return bars
    # }}}
    @classmethod  #__loadDataType# {{{
    def __loadSource(cls, ID, data_type):
        path = Cmd.path(ID.dir_path, data_type.value, "source")
        source = Source.load(path)
        return source
    # }}}
# }}}
class _BarsDataFileIterator():# {{{
    def __init__(self, ID: Id, data_type):# {{{
        self.ID = ID
        self.data_type = data_type
        self.years = _Manager.availibleYears(ID, data_type)
        self.index = 0
    # }}}
    def __next__(self):# {{{
        if self.index < len(self.years):
            year = self.years[self.index]
            data = _BarsDataFile.load(self.ID, self.data_type, year)
            self.index += 1
            return data
        else:
            raise StopIteration
    # }}}
    def __iter__(self):# {{{
        # При передаче объекта функции iter возвращает самого себя
        # тем самым в точности реализуя протокол итератора
        return self
    # }}}
# }}}
class _StockDataFile():# {{{
    ...
# }}}
class _TickDataFile():# {{{
    ...
# }}}

class _AbstractSource(metaclass=abc.ABCMeta):# {{{
    """ const """# {{{
    _SUB_DIR = None
    _CACHE_DIR = None
    _CACHE_DATE_FILE = None
    _CACHE_IS_UP_TO_DATE = None
    # }}}
    @abc.abstractmethod  #__init__# {{{
    def __init__(self): ...
    # }}}
    @abc.abstractmethod  #assets# {{{
    def assets(self, asset_type=None) -> list : ...
    # }}}
    @abc.abstractmethod  #find# {{{
    def find(self, exchange: str, asset_type: str, querry: str) -> Id: ...
    # }}}
    @abc.abstractmethod  #info# {{{
    def info(self, ID: Id) -> dict: ...
    # }}}
    @abc.abstractmethod  #firstDateTime# {{{
    def firstDateTime(self, ID: Id, data_type: DataType) -> datetime: ...
    # }}}
    @abc.abstractmethod  #download# {{{
    def download(self, ID: Id, data_type: DataType, year: int) -> bool: ...
    # }}}
    @abc.abstractmethod  #export# {{{
    def export(self) -> bool: ...
    # }}}
    @abc.abstractmethod  #clear# {{{
    def clear(self) -> bool: ...
    # }}}
    @abc.abstractmethod  #getHistoricalBars# {{{
    def getHistoricalBars(
        self, ID: Id, data_type: DataType, begin: datetime, end: datetime
        ) -> list[_Bar]: ...
    # }}}
    @classmethod  #_checkCachingDate# {{{
    def _checkCachingDate(cls):
        if Cmd.isExist(cls._CACHE_DATE_FILE):
            string = Cmd.read(cls._CACHE_DATE_FILE)
            last_update = datetime.fromisoformat(string)
            if now().date() == last_update.date():
                return True
        return False
    # }}}
    @classmethod  #_getStandartAssetTypeName# {{{
    def _getStandartAssetTypeName(cls, name):
        names = {
            "index": "Index",
            "shares": "Share",
            "bonds": "Bond",
            "futures": "Future",
            "currency": "Currency",
            "currencies": "Currency",
            "etfs": "Etf",
            }
        standart_name = names[name]
        return standart_name
    # }}}
    @classmethod  #_saveCache# {{{
    def _saveCache(cls, asset_type: str, info: dict) -> None:
        file_path = Cmd.path(cls._CACHE_DIR, f"{asset_type}.json")
        Cmd.saveJson(info, file_path, encoder=cls._encoderJson)
    # }}}
    @classmethod  #_saveCachingDate# {{{
    def _saveCachingDate(cls):
        dt = now().isoformat()
        Cmd.write(dt, cls._CACHE_DATE_FILE)
    # }}}
    @classmethod  #_selectCache# {{{
    def _selectCache(cls, asset_type: AssetType):

        if not cls._CACHE_IS_UP_TO_DATE:
            logger.error(f"{cls.__name__} assets cache unavailible")
            return None
        elif asset_type == AssetType.Index:
            cache = cls._INDEX_CACHE
        elif asset_type == AssetType.Share:
            cache = cls._SHARE_CACHE
        elif asset_type == AssetType.Bond:
            cache = cls._BONDS_CACHE
        elif asset_type == AssetType.Future:
            cache = cls._FUTURE_CACHE
        elif asset_type == AssetType.Currency:
            cache = cls._CURRENCY_CACHE
        elif asset_type == AssetType.Etf:
            cache = cls._ETF_CACHE

        if cache is None:
            cache_path = Cmd.path(cls._CACHE_DIR, f"{asset_type.name}.json")
            assets_info = Cmd.loadJson(cache_path, decoder=cls._decoderJson)
            cache = assets_info

        return cache
    # }}}
    @classmethod  #_searchBy# {{{
    def _searchBy(cls, exchange, parameter, value, cache):
        # argument 'exchenge' is not used yet, but may be needed in the future
        # now the exchange name is checked by the class Data at the input of a
        # request from the user
        for i in cache:
            if i[parameter] == value:
                return i
        logger.error(
            f"{cls.__name__}._searchBy: Asset {parameter}={value} not found"
            )
        return None
    # }}}
    @classmethod  #_parseFileName# {{{
    def _parseFileName(cls, file_name):
        exchange, asset_type, ticker, data_type, year = file_name.split("-")

        exchange = Exchange.fromStr(exchange)
        asset_type = AssetType.fromStr(asset_type)
        ID = Data.find(exchange, asset_type, ticker)

        data_type = DataType.fromStr(data_type)

        return ID, data_type
    # }}}
    @staticmethod  #_encoderJson# {{{
    def _encoderJson(obj):
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
    # }}}
    @staticmethod  #_decoderJson# {{{
    def _decoderJson(obj):
        # TODO: encoder and decoder - вынести в классы потомки ???
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
class _MoexData(_AbstractSource):# {{{
    """ const """# {{{
    SESSION_BEGIN =         time(7, 0, tzinfo=UTC)
    SESSION_END =           time(15, 39, tzinfo=UTC)
    EVENING_BEGIN =         time(16, 5, tzinfo=UTC)
    EVENING_END =           time(20, 49, tzinfo=UTC)
    MSK_TIME_DIF =          timedelta(hours=3)
    AVAILIBLE_DATA =        [DataType.BAR_1M,
                             DataType.BAR_10M,
                             DataType.BAR_1H,
                             DataType.BAR_D,
                             DataType.BAR_W,
                             DataType.BAR_M,
                             ]

    _SUB_DIR =              "moex"
    _DOWNLOAD =             Cmd.path(Usr.DOWNLOAD, _SUB_DIR)
    _CACHE_DIR =            Cmd.path(Res.CACHE, _SUB_DIR)
    _CACHE_DATE_FILE =      Cmd.path(_CACHE_DIR, "last_update")

    _LOGIN =                None
    _PASSWORD =             None
    _AUTHORIZATION =        None

    _CACHE_IS_UP_TO_DATE =  None
    _INDEX_CACHE =          None
    _SHARE_CACHE =          None
    _FUTURE_CACHE =         None
    _CURRENCY_CACHE =       None
    # }}}
    def __init__(self):# {{{
        if not self._CACHE_IS_UP_TO_DATE:
            self.__cacheAssetsInfo()
    # }}}
    def assets(self, asset_type=None) -> list :# {{{
        cache = self._selectCache(asset_type)
        if not cache:
            return list()

        if asset_type == AssetType.Index:
            return self.__getAllIndex(cache)
        elif asset_type == AssetType.Share:
            return self.__getAllShares(cache)
        elif asset_type in []:
            logger.error(
                "MOEX does not provide figi. Figi needed for unified "
                "identifier for all assets. To obtain IDs of "
                "futures, currencies, bonds, use the Tinkoff source. "
                "Recommended use Source.MOEX only for receive indexes."
                )
            return list()
    # }}}
    def find(# {{{
            self,
            exchange: Exchange,
            asset_type: AssetType,
            querry: str
            ) -> Id:

        cache = super()._selectCache(asset_type)
        info = self.__info(exchange, asset_type, querry, cache)
        if info is not None:
            ID = Id(
                exchange=   exchange,
                asset_type= asset_type,
                name=       info["NAME"],
                ticker=     info["SECID"],
                figi=       None,  # Indexes not have figi
                )
            return ID
        else:
            return None
    # }}}
    def info(self, ID: Id) -> dict:# {{{
        cache = super()._selectCache(ID.type)
        info = self.__info(ID.exchange, ID.type, ID.ticker, cache)
        return info
    # }}}
    def firstDateTime(self, ID: Id, data_type: DataType) -> datetime:# {{{
        date_start = date(1990, 1, 1)
        try:
            asset = moexalgo.Ticker(ID.ticker)
            candles = asset.candles(
                start=       date_start,
                end=         "today",
                period=      self.__convert(data_type),
                use_dataframe= False,
                )
        except LookupError as err:
            logger.warning(f"_MoexData: no market data for {ID.ticker}")
            return None
        candle = candles.send(None)
        dt = candle.begin
        return self.__toUTC(dt)
    # }}}
    def download(self, ID: Id, data_type: DataType, year: int) -> bool:# {{{
        assert data_type.value in ["1M", "10M", "1H", "D", "W", "M"]
        self.__authorizate()
        logger.info(f":: Download {ID.ticker}-{data_type.value} from {year}")
        begin, end = self.__getPeriod(year)
        candles = self.__getHistoricalCandles(ID, data_type, begin, end)
        if len(candles) == 0:
            logger.warning(
                f"No data received for {ID.ticker}-{data_type.value}-{year}"
                )
            return
        self.__saveCandles(ID, data_type, year, candles)
    # }}}
    def export(self) -> None:# {{{
        logger.info(f":: MOEX exporting data in standart format")
        files = Cmd.getFiles(
            self._DOWNLOAD, full_path=True, include_sub_dir=True
            )
        files = sorted(Cmd.select(files, extension=".csv"))
        for file in files:
            logger.info(f"  - exporting '{file}'")
            ID, data_type, bars = self.__readDataFile(file)
            data = _BarsDataFile(ID, data_type, bars, Source.MOEX)
            _BarsDataFile.save(data)
        logger.info(f"Export complete")
    # }}}
    def clear(self) -> bool:# {{{
        logger.info(f":: Clear MOEX files")
        path = self._DOWNLOAD
        if not Cmd.isExist(path):
            logger.info(f"  - no data in '{path}'")
            return
        Cmd.deleteDir(path)
        logger.info(f"  - successful complete")
    # }}}
    def getHistoricalBars(# {{{
        self, ID: Id, data_type: DataType, begin: datetime, end: datetime
        ) -> list[_Bar]:

        begin = self.__toMSK(begin)
        end = self.__toMSK(end)

        candles = self.__getHistoricalCandles(ID, data_type, begin, end)
        bars = self.__convert(candles)
        return bars
    # }}}
    @classmethod  #__authorizate# {{{
    def __authorizate(cls):
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
    @classmethod  #__cacheAssetsInfo# {{{
    def __cacheAssetsInfo(cls):
        if cls._checkCachingDate():
            cls._CACHE_IS_UP_TO_DATE = True
            return

        logger.info(f":: Caching assets info from MOEX")
        cls.__authorizate()
        if not cls._AUTHORIZATION:
            return

        types = ["index", "shares", "currency", "futures"]
        for t in types:
            logger.info(f"  - caching {t}")
            assets_info = moexalgo.Market(t).tickers(use_dataframe=False)
            asset_type = cls._getStandartAssetTypeName(t)
            cls._saveCache(asset_type, assets_info)
        cls._saveCachingDate()
        cls._CACHE_IS_UP_TO_DATE = True
    # }}}
    @classmethod  #__info# {{{
    def __info(cls, exchange, asset_type, querry, cache: str) -> dict[str]:
        if len(querry) <= 12:
            return cls._searchBy(exchange, "SECID", querry, cache)
        else:
            logger.error(
                "{cls.__name__}.__info: failed. Unknown identifier "
                f"exchange={exchange} type={asset_type} querry={querry}."
                )
            return None
    # }}}
    @classmethod  #__getAllIndex# {{{
    def __getAllIndex(cls, cache: list[dict]) -> list(Id):
        all_id = list()
        for asset in cache:
            ID = Id(
                exchange=   Exchange.MOEX,
                asset_type= AssetType.Index,
                name=       asset["NAME"],
                ticker=     asset["SECID"],
                figi=       None,  # Indexes not have figi
                )
            all_id.append(ID)
        return all_id
    # }}}
    @classmethod  #__getAllShares# {{{
    def __getAllShares(cls, cache: list[dict]) -> list(Id):
        all_id = list()
        for asset in cache:
            # MOEX does not provide figi. Figi needed for unified
            # identifier for all assets. Receiving it from Tinkoff,
            # but assets only from MOEX TQBR, and only availible
            # for trading at Tinkoff broker
            td = _TinkoffData()
            ID = td.find(Exchange.MOEX, AssetType.Share, asset["SECID"])
            if ID is not None:
                all_id.append(ID)
        return all_id
    # }}}
    @classmethod  #__convert# {{{
    def __convert(self, obj: object):
        if isinstance(obj, DataType):
            return self.__convertDataType(obj)
        elif isinstance(obj, list):
            return self.__candlesToBars(obj)
        else:
            assert False, f"unknown object type '{type(obj)}'"
    # }}}
    @classmethod  #__convertDataType# {{{
    def __convertDataType(self, data_type: DataType):
        moex_period = {
            "1M":  "1min",
            "10M": "10min",
            "1H":  "1h",
            "D":   "1d",
            "W":   "1w",
            "M":   "1m",
            }
        return moex_period[data_type.value]
    # }}}
    @classmethod  #__candlesToBars# {{{
    def __candlesToBars(cls, candles):
        bars = list()
        for i in candles:
            bar = _Bar(
                dt= cls.__toUTC(i.begin),
                open= i.open,
                high= i.high,
                low= i.low,
                close= i.close,
                vol= int(i.volume)
                )
            bars.append(bar)
        return bars
    # }}}
    @classmethod  #__getPeriod# {{{
    def __getPeriod(
            self,
            year: int
            ) -> (datetime, datetime):
        begin = datetime(year, 1, 1)
        end = datetime(year + 1, 1, 1)
        if end >= datetime.now():
            end = datetime.now().replace(microsecond=0)
        return (begin, end)
    # }}}
    @classmethod  #__requestCandles# {{{
    def __requestCandles(
        cls,
        ID: Id,
        data_type: DataType,
        begin: datetime,
        end: datetime
        ):
        period = data_type.toTimedelta()
        if period < ONE_DAY:
            return cls.__requestCandlesSmallTimeFrame(
                ID, data_type, begin, end
                )
        else:
            return cls.__requestCandlesBigTimeFrame(
                ID, data_type, begin, end
                )
    # }}}
    @classmethod  #__requestCandlesBigTimeFrame# {{{
    def __requestCandlesBigTimeFrame(
            cls,
            ID: Id,
            data_type: DataType,
            begin: datetime,
            end: datetime
            ):

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
                start= current,
                end= current.replace(year= current.year + 1),
                period= period,
                use_dataframe= False,
                )
            for i in candles:
                all_candles.append(i)
            current = current.replace(year= current.year + 1)

        # Fucking MOEX returns candles in closed interval [begin, end]
        # fix it, return [begin, end)
        if all_candles and all_candles[-1].begin == end:
            all_candles.pop(-1)

        return all_candles
    # }}}
    @classmethod  #__requestCandlesSmallTimeFrame# {{{
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
                start=          current,
                end=            datetime.combine(current.date(), time(23,59)),
                period=         period,
                use_dataframe=  False,
                )
            for i in candles:
                all_candles.append(i)
            current += ONE_DAY
        return all_candles
    # }}}
    @classmethod  #__getHistoricalCandles# {{{
    def __getHistoricalCandles(
        cls,
        ID: Id,
        data_type: DataType,
        begin: datetime,
        end: datetime
        ):

        candles = cls.__requestCandles(ID, data_type, begin, end)
        if not candles:
            return list()

        # timeframe M
        if data_type == DataType.BAR_M:
            last_candle_month = candles[-1].end.month
            now_month = date.today().month
            if last_candle_month == now_month:
                candles.pop(-1)
            return candles

        # other timeframes
        period = data_type.toTimedelta()
        if (period <= ONE_WEEK):
            last_candle_begin = candles[-1].begin
            last_candle_end = candles[-1].end
            if (last_candle_end < last_candle_begin + period):
                candles.pop(-1)
            return candles

        assert False, "Тут мы никак не должны оказаться"
    # }}}
    @classmethod  #__createFilePath# {{{
    def __createFilePath(cls, ID: Id, data_type: DataType, year: int):
        dir_path = Cmd.path(cls._DOWNLOAD, ID.type.name, ID.ticker)
        Cmd.makeDirs(dir_path)
        file_name = (
            f"{ID.exchange.name}-{ID.type.name}-{ID.ticker}-{data_type.value}"
            f"-{year}.csv"
            )
        full_path = Cmd.path(dir_path, file_name)
        return full_path
    # }}}
    @classmethod  #__saveCandles# {{{
    def __saveCandles(
        cls,
        ID: Id,
        data_type: DataType,
        year: int,
        candles: list[moexalgo.models.Candle]
        ):
        path = cls.__createFilePath(ID, data_type, year)
        df = pd.DataFrame(candles)
        df.to_csv(path, sep=";")
        logger.info(f"Saved {ID.ticker} {data_type.value} {year} in '{path}'")
    # }}}
    @classmethod  #__readDataFile# {{{
    def __readDataFile(cls, file_path: str):
        ID, data_type = cls._parseFileName(Cmd.name(file_path))
        bars = cls.__readFileText(Cmd.loadText(file_path))
        return ID, data_type, bars
    # }}}
    @classmethod  #__readFileText# {{{
    def __readFileText(cls, text):
        text.pop(0)  # skip header row
        bars = list()
        for line in text:
            bar = cls.__parseMoexLine(line)
            bars.append(bar)
        return bars
    # }}}
    @classmethod  #__parseMoexLine# {{{
    def __parseMoexLine(cls, line: str):
        NUM, OPEN, CLOSE, HIGH, LOW, VALUE, VOLUME, BEGIN, END = range(9)
        fields = line.split(";")
        open_ =     float(fields[OPEN])
        high =      float(fields[HIGH])
        low =       float(fields[LOW])
        close =     float(fields[CLOSE])
        volume =    int(float(fields[VOLUME]))
        dt =        cls.__toUTC(datetime.fromisoformat(fields[BEGIN]))
        return _Bar(dt, open_, high, low, close, volume)
    # }}}
    @classmethod  #__toUTC# {{{
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
    @classmethod  #__toMSK# {{{
    def __toMSK(cls, utc_dt: datetime) -> datetime:
        # MOEX work with Moscow time, UTC+3, and use offset-naive datetime
        if utc_dt.hour != 0:
            return (utc_dt + cls.MSK_TIME_DIF).replace(tzinfo=None)
        else:
            # timeframe >= D, msk time = 00:00, only change timezone
            return utc_dt.replace(tzinfo=None)
    # }}}
# }}}
class _TinkoffData(_AbstractSource):# {{{
    """ const """# {{{
    EXCLUDE_HOLIDAYS =      True
    AVAILIBLE_DATA =        [DataType.BAR_1M,
                             DataType.BAR_5M,
                             DataType.BAR_10M,
                             DataType.BAR_1H,
                             DataType.BAR_D,
                             DataType.BAR_W,
                             DataType.BAR_M,
                             ]

    _SUB_DIR =              "tinkoff"
    _DOWNLOAD =             Cmd.path(Usr.DOWNLOAD, _SUB_DIR)
    _CACHE_DIR =            Cmd.path(Res.CACHE, _SUB_DIR)
    _CACHE_DATE_FILE =      Cmd.path(_CACHE_DIR, "last_update")

    _TARGET =               tinkoff.invest.constants.INVEST_GRPC_API
    _TOKEN =                None

    _CACHE_IS_UP_TO_DATE =  None
    _SHARE_CACHE =          None
    _BONDS_CACHE =          None
    _FUTURE_CACHE =         None
    _CURRENCY_CACHE =       None
    _ETF_CACHE =            None
    # }}}
    def __init__(self):# {{{
        if not _TinkoffData._CACHE_IS_UP_TO_DATE:
            self.__cacheAssetsInfo()
    # }}}
    def assets(self, asset_type: AssetType) -> list[Id]:# {{{
        cache = self._selectCache(asset_type)
        if cache:
            return self.__getAllId(cache)
        else:
            return list()
    # }}}
    def find(# {{{
        self, exchange: Exchange, asset_type: AssetType, querry: str
        ) -> Id:
        cache = super()._selectCache(asset_type)
        info = self.__info(exchange, asset_type, querry, cache)
        if info is not None:
            ID = self.__getId(info)
            return ID
        else:
            return None
    # }}}
    def info(self, ID: Id) -> dict:# {{{
        cache = super()._selectCache(ID.type)
        info = self.__info(ID.exchange, ID.type, ID.ticker, cache)
        return info
    # }}}
    def firstDateTime(self, ID: Id, data_type: DataType) -> datetime:# {{{
        # assert data_type.value == "1M"
        cache = super()._selectCache(ID.type)
        info = self.__info(ID.exchange, ID.type, ID.ticker, cache)
        if data_type.value == "1M":
            return info["first_1min_candle_date"]
        elif data_type.value == "D":
            return info["first_1day_candle_date"]
    # }}}
    def download(cls, ID: Id, data_type: DataType, year: int) -> None:# {{{
        assert data_type.value == "1M"
        if not cls.__authorizate():
            return

        logger.info(f":: Download {ID.ticker}-{data_type.value} from {year}")
        cls.__requestHistoricalData(ID, year)
    # }}}
    def export(self) -> None:#{{{
        #TODO fix - not exclude holidays files
        logger.info(f":: Tinkoff exporting data in standart format")
        files = Cmd.getFiles(
            self._DOWNLOAD, full_path=True, include_sub_dir=True
            )
        archives = sorted(Cmd.select(files, extension=".zip"))

        for archive in archives:
            logger.info(f"  - exporting '{archive}'")
            tmp_dir = Cmd.path(Dir.TMP, self._SUB_DIR)
            Cmd.extract(archive, tmp_dir)

            bars = self.__loadDataDir(tmp_dir)
            ID, data_type = self._parseFileName(Cmd.name(archive))

            data = _BarsDataFile(ID, data_type, bars, Source.TINKOFF)
            _BarsDataFile.save(data)

            Cmd.deleteDir(tmp_dir)

        logger.info(f"Export complete")
    # }}}
    def clear(self) -> None:# {{{
        logger.info(f":: Clear Tinkoff files")
        path = self._DOWNLOAD
        if not Cmd.isExist(path):
            logger.info(f"  - no data in '{path}'")
            return
        Cmd.deleteDir(path)
        logger.info(f"  - successful complete")
    # }}}
    def getHistoricalBars(# {{{
        self, ID: Id, data_type: DataType, begin: datetime, end: datetime
        ) -> list[_Bar]:
        logger.info(
            f"  - request {ID.ticker}-{data_type.value} from {begin.date()}"
            )

        if not self.__authorizate():
            return

        new_bars = list()
        with tinkoff.invest.Client(self._TOKEN) as client:
            try:
                candles = client.get_all_candles(
                    figi = ID.figi,
                    from_ = begin,
                    to = end,
                    interval = _TinkoffData._CandleIntervalFrom(data_type),
                    )
                for candle in candles:
                    if candle.is_complete:
                        bar = _TinkoffData._toBar(candle)
                        new_bars.append(bar)
            except tinkoff.invest.exceptions.RequestError as err:
                logger.exception(err)
                return list()
            return new_bars
    # }}}

    @classmethod  #__authorizate# {{{
    def __authorizate(cls) -> bool:
        if cls._TOKEN is not None:
            return True

        token_path = Cmd.path(Usr.CONNECT, cls._SUB_DIR, Usr.TINKOFF_TOKEN)
        if not Cmd.isExist(token_path):
            logger.warning(
                "Tinkoff not exist token file, operations with market data "
                "and orders unavailible. Make a token and put it in a "
                f"'{token_path}'. Read more about token: "
                "https://developer.tinkoff.ru/docs/intro/"
                "manuals/self-service-auth"
                )
            return False

        token = Cmd.read(token_path).strip()
        try:
            with tinkoff.invest.Client(token) as client:
                response = client.users.get_accounts()
                if response:
                    _TinkoffData._TOKEN = token
                    logger.info("Tinkoff Authorization successful")
                    return True
        except tinkoff.invest.exceptions.UnauthenticatedError as err:
            logger.exception(err)
            logger.error(
                "Tinkoff authorization fault, check your token. "
                "Operations with market data unavailible. "
                f"Token='{token}'"
                )
            return False
    # }}}
    @classmethod  #__cacheAssetsInfo# {{{
    def __cacheAssetsInfo(cls):
        if cls._checkCachingDate():
            cls._CACHE_IS_UP_TO_DATE = True
            return

        logger.info(f":: Caching assets info from Tinkoff")
        if not cls.__authorizate():
            return

        types = ["shares", "bonds", "futures", "currencies", "etfs"]
        for t in types:
            logger.info(f"  - caching {t}")
            assets = cls.__requestAvailibleAssets(t)
            f = lambda x: x["exchange"] not in [
                "otc_ncc", "LSE_MORNING", "moex_close", "Issuance"
                ]
            assets = [i for i in filter(f, assets)]
            asset_type = cls._getStandartAssetTypeName(t)
            cls._saveCache(asset_type, assets)
        cls._saveCachingDate()
        cls._CACHE_IS_UP_TO_DATE = True
    # }}}
    @classmethod  #__requestAvailibleAssets# {{{
    def __requestAvailibleAssets(cls, asset_type: str):
        # asset_type must be availible for tinkoff invest API
        # for example: "shares", "bonds", "futures", "currencies", "etfs"...
        with tinkoff.invest.Client(cls._TOKEN) as client:
            all_info = list()
            response: list[tinkoff.invest.Instrument] = (
                getattr(client.instruments, asset_type)().instruments
                )
            for item in response:
                item_info = cls.__extractBrokerInfo(item)
                item_info["type"] = cls._getStandartAssetTypeName(asset_type)
                all_info.append(item_info)
            return all_info
    # }}}
    @classmethod  #__extractBrokerInfo# {{{
    def __extractBrokerInfo(cls, instr: tinkoff.invest.Instrument) -> dict:
        quotation_to_decimal = tinkoff.invest.utils.quotation_to_decimal
        tinkoff.invest.SecurityTradingStatus
        info = {
            "name": instr.name,
            "ticker": instr.ticker,
            "country_of_risk": instr.country_of_risk,
            "currency": instr.currency,
            "exchange": instr.exchange,
            "class_code": instr.class_code,
            "figi": instr.figi,
            "uid": instr.uid,
            "lot": instr.lot,
            "min_price_increment": float(quotation_to_decimal(
                instr.min_price_increment
                )),
            "trading_status": tinkoff.invest.SecurityTradingStatus(
                instr.trading_status
                ).name,
            "for_qual_investor_flag": instr.for_qual_investor_flag,
            "api_trade_available_flag": instr.api_trade_available_flag,
            "buy_available_flag": instr.buy_available_flag,
            "sell_available_flag": instr.sell_available_flag,
            "short_enabled_flag": instr.short_enabled_flag,
            "klong": quotation_to_decimal(instr.klong),
            "kshort": quotation_to_decimal(instr.kshort),
            "first_1min_candle_date": instr.first_1min_candle_date,
            "first_1day_candle_date": instr.first_1day_candle_date,
            }
        if hasattr(instr, "isin"):
            info["isin"] = instr.isin
        if hasattr(instr, "sector"):
            info["sector"] = instr.sector
        return info
    # }}}
    @classmethod  #__info# {{{
    def __info(cls, exchange, asset_type, querry, cache: str) -> dict[str]:
        if len(querry) == 12 and (
            querry.startswith("BBG") or querry.startswith("FUT") or
            querry.startswith("TCS")
            ):
            return cls._searchBy(exchange, "figi", querry, cache)
        elif len(querry) <= 12:
            return cls._searchBy(exchange, "ticker", querry, cache)
        elif len(querry) > 12:
            return cls._searchBy(exchange, "uid", querry, cache)
        else:
            logger.error(
                "_TinkoffData.__info: failed. Unknown identifier "
                f"exchange={exchange} type={asset_type} querry={querry}."
                )
            return None
    # }}}
    @classmethod  #__getId# {{{
    def __getId(cls, info: dict) -> Id:
        # In dictionaries received from the broker, the moex exchange is
        # designated in several ways: MOEX, MOEX_PLUS MOEX_EVENING_WEEKEND...
        if "MOEX" in info["exchange"]:
            exchange = Exchange.MOEX
        # Similar to SPB exchange: spb_close, SPB_RU_MORNING..
        elif "SPB" in info["exchange"].upper():
            exchange = Exchange.SPB
        elif info["exchange"] == "FORTS_EVENING":  # MOEX Futures
            exchange = Exchange.MOEX
        else:
            logger.critical(
                f"_TinkoffData.__getId: unknown exchange={info['exchange']}"
                )
            exit(1)

        ID = Id(
            exchange=   exchange,
            asset_type= AssetType.fromStr(info["type"]),
            name=       info["name"],
            ticker=     info["ticker"],
            figi=       info["figi"],
            )
        return ID
    # }}}
    @classmethod  #__getAllId# {{{
    def __getAllId(cls, cache: list[dict]) -> list(Id):
        all_id = list()
        for asset in cache:
            ID = cls.__getId(asset)
            all_id.append(ID)
        return all_id
    # }}}
    @classmethod  #__requestHistoricalData# {{{
    def __requestHistoricalData(cls, ID: Id, year: int):
        exchange = ID.exchange.name
        type_ = ID.type.name
        figi = ID.figi
        ticker = ID.ticker
        file_name = (f"{exchange}-{type_}-{ticker}-1M-{year}.zip")
        file_path = Cmd.path(cls._DOWNLOAD, type_, ticker, file_name)
        data_url = "https://invest-public-api.tinkoff.ru/history-data"
        command  = (
            f"curl -s --location '{data_url}?figi={figi}&year={year}' "
            f"-H 'Authorization: Bearer {cls._TOKEN}' "
            f"-o {file_name} "
            # "-w '%{http_code\\n'"
            )
        code = os.system(command)
        if Cmd.isExist(file_name):
            Cmd.replace(file_name, file_path)
            logger.info(f"  - saved {file_path}")
# }}}
    @classmethod  #__loadDataDir# {{{
    def __loadDataDir(self, dir_path):
        files = sorted(Cmd.getFiles(dir_path, full_path=True))
        if self.EXCLUDE_HOLIDAYS:
            files = self.__excludeHolidaysFiles(files)
        all_bars = list()
        for file in files:
            tinkoff_bars = self.__readTinkoffFile(file)
            all_bars += tinkoff_bars
        return all_bars
    # }}}
    @classmethod  #__excludeHolidaysFiles# {{{
    def __excludeHolidaysFiles(self, files):
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
    @classmethod # __excludeHolidaysBars# {{{
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
    @classmethod  #__readTinkoffFile# {{{
    def __readTinkoffFile(self, file_path):
        tinkoff_bars = list()
        text = Cmd.loadText(file_path)
        for line in text:
            bar = self.__parseLineTinkoff(line)
            tinkoff_bars.append(bar)
        return tinkoff_bars
    # }}}
    @classmethod  #__parseLineTinkoff# {{{
    def __parseLineTinkoff(self, line):
        fields = line.split(";")
        UID, DATETIME, OPEN, CLOSE, HIGH, LOW, VOLUME = range(7)
        opn = float(fields[OPEN])
        cls = float(fields[CLOSE])
        hgh = float(fields[HIGH])
        low = float(fields[LOW])
        vol = int(fields[VOLUME])
        dt =  fields[DATETIME]
        bar = _Bar(dt, opn, hgh, low, cls, vol)
        return bar
    # }}}
    @classmethod  #_CandleIntervalFrom# {{{
    def _CandleIntervalFrom(
        cls,
        data_type: DataType
        ) -> tinkoff.invest.CandleInterval:

        intervals = {
            "1M":  tinkoff.invest.CandleInterval.CANDLE_INTERVAL_1_MIN,
            "10M": tinkoff.invest.CandleInterval.CANDLE_INTERVAL_10_MIN,
            "5M":  tinkoff.invest.CandleInterval.CANDLE_INTERVAL_5_MIN,
            "1H":  tinkoff.invest.CandleInterval.CANDLE_INTERVAL_HOUR,
            "D":   tinkoff.invest.CandleInterval.CANDLE_INTERVAL_DAY,
            "W":   tinkoff.invest.CandleInterval.CANDLE_INTERVAL_WEEK,
            "M":   tinkoff.invest.CandleInterval.CANDLE_INTERVAL_MONTH,
            }
        return intervals[data_type.value]
    # }}}
    @classmethod  #_toBar# {{{
    def _toBar(cls, candle) -> _Bar:
        opn = float(tinkoff.invest.utils.quotation_to_decimal(candle.open))
        cls = float(tinkoff.invest.utils.quotation_to_decimal(candle.close))
        hgh = float(tinkoff.invest.utils.quotation_to_decimal(candle.high))
        low = float(tinkoff.invest.utils.quotation_to_decimal(candle.low))
        vol = candle.volume
        dt = candle.time
        bar = _Bar(dt, opn, hgh, low, cls, vol)
        return bar
    # }}}



    # DEPRICATE
    @classmethod  #__makeSharesSubgroups# {{{
    def __makeSharesSubgroups(cls) -> None:
        file_path = Cmd.path(cls._CACHE_DIR, "Share.json")
        shares = Cmd.loadJson(file_path, decoder=cls._decoderJson)

        ru = [i for i in shares if i["country_of_risk"] == "RU"]
        cls._saveCache("shares_ru", ru)

        moex = [i for i in ru if "MOEX" in i["exchange"]]
        cls._saveCache("shares_ru_moex", moex)

        moex_tqbr = [i for i in moex if i["class_code"] == "TQBR"]
        cls._saveCache("shares_ru_moex_tqbr", moex_tqbr)
    # }}}
# }}}

class _Manager():# {{{
    class VoidBar():# {{{
        """ doc# {{{
        Utility class for data conversion
        """
        # }}}
        def __init__(self, dt: datetime):# {{{
            self.dt = dt
        # }}}
# }}}
    @classmethod # allDataList{{{
    def allDataList(cls) -> list[tuple(Id, DataType, Source)]:
        logger.debug(f"Data.getAllDataDirs()")

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

                ID = Id.load(id_path)
                data_type = DataType.load(type_path)
                source = Source.load(source_path)

                all_list.append( (ID, data_type, source) )
        return all_list
    # }}}
    @classmethod  #availibleYears# {{{
    def availibleYears(cls, ID: Id, data_type: DataType):
        files = cls.__findFiles(ID, data_type)
        csv_files = Cmd.select(files, extension=".csv")
        years = [int(Cmd.name(i)) for i in (csv_files)]  # file_name == year
        if len(years) == 0:
            logger.warning(f"{ID.ticker}-{data_type.value} no data files")
        return years
    # }}}
    @classmethod  #convert# {{{
    def convert(cls, ID: Id, in_type: DataType, out_type: DataType):
        logger.info(f":: Convert {ID.ticker}-{in_type.value} to {out_type.value}")
        converter = cls.__choseConverter(out_type)
        for data in _BarsDataFileIterator(ID, in_type):
            logger.info(f"  - converting {data.year}")
            bars = converter(data.bars, in_type, out_type)
            converted = _BarsDataFile(ID, out_type, bars, data.source)
            _BarsDataFile.save(converted)
    # }}}
    @classmethod  #update# {{{
    def update(cls, ID: Id, data_type: DataType):
        data = cls.__lastBarsDataFile(ID, data_type)
        if not data:
            logger.error(
                f"No data for {Id.ticker}-{data_type.value}. "
                f"Operation canceled."
                )
            return

        # selecting the same source as the data and check availiblity data_type
        if (data.source == Source.MOEX and
            data_type in _MoexData.AVAILIBLE_DATA
            ):
            cls.__update(data, _MoexData)
        elif (data.source == Source.TINKOFF and
            data_type in _TinkoffData.AVAILIBLE_DATA
            ):
            cls.__update(data, _TinkoffData)
        else:
            logger.error(
                f"Data source '{data.source.name}' "
                f"does not provide type '{data_type.value}'. "
                f"Operation canceled."
                )
        # }}}
    @classmethod  #updateAll# {{{
    def updateAll(cls):
        data_list = cls.allDataList()
        count = len(data_list)
        for n, i in enumerate(data_list, 1):
            logger.info(f":: Updating {n}/{count}")
            ID, data_type, source = i
            cls.update(ID, data_type)
        # }}}
    @classmethod  #request# {{{
    def request(
        cls, ID: Id, data_type: DataType, begin: int, end: int
        ) -> list[file_path]:

        files = cls.__findFiles(ID, data_type)
        files = cls.__selectYear(files, begin, end)
        return files
        # }}}
    @classmethod  #delete# {{{
    def delete(cls, ID: Id, data_type: DataType):
        logger.info(f":: Delete {ID.ticker}-{data_type.value}")
        dir_path = Cmd.path(ID.dir_path, data_type.value)
        Cmd.deleteDir(dir_path)
        logger.info(f"  - complete")
        # }}}
    @classmethod  #__findFiles# {{{
    def __findFiles(cls, ID: Id, data_type: DataType) -> list[str]:
        data_dir = Cmd.path(ID.dir_path, data_type.value)
        if not Cmd.isExist(data_dir):
            return list()
        files = sorted(Cmd.getFiles(data_dir, full_path=True))
        files = Cmd.select(files, extension=".csv")
        return files
    # }}}
    @classmethod  #__selectYear# {{{
    def __selectYear(cls, files, begin: int, end: int):
        out_files = list()
        for file in files:
            # Имена файлов выглядят так: 2022.csv, 2023.csv ...
            file_year = int(Cmd.name(file))
            if begin <= file_year <= end:
                out_files.append(file)
        return out_files
    # }}}
    @classmethod  #__lastBarsDataFile# {{{
    def __lastBarsDataFile(
        cls,
        ID: Id,
        data_type: DataType
        ) -> _BarsDataFile:

        years = cls.availibleYears(ID, data_type)
        if years:
            data = _BarsDataFile.load(ID, data_type, years[-1])
            return data
        else:
            return None
        # }}}
    @classmethod  #__update# {{{
    def __update(cls, data: _BarsDataFile, source: _AbstractSource):
        begin = data.last_dt + data.data_type.toTimedelta()
        end = now().replace(microsecond=0)
        src = source()
        new_bars = src.getHistoricalBars(data.ID, data.data_type, begin, end)
        count = len(new_bars)
        if count == 0:
            logger.info(f"  - {data.ID.ticker}-{data.data_type.value} no new bars")
            return
        logger.info(
                f"  - {data.ID.ticker}-{data.data_type.value} "
                f"received {count} bars -> {new_bars[-1].dt}"
                )
        cls.__saveNewBars(data, new_bars)
        # }}}
    @classmethod  #__saveNewBars # {{{
    def __saveNewBars(cls, data: _BarsDataFile, new_bars):
        year = data.year
        bars = cls.__popYear(new_bars, year)  # extract only equal year
        data.add(bars)
        _BarsDataFile.save(data)

        # if 'new_bars' consist some more bars, create new files
        ID = data.ID
        data_type = data.data_type
        source = data.source
        while len(new_bars) > 0:
            year += 1
            bars = cls.__popYear(new_bars, year)
            new_data = _BarsDataFile(ID, data_type, bars, source)
            _BarsDataFile.save(new_data)
        # }}}
    @classmethod  #__popYear# {{{
    def __popYear(cls, bars, year):
        assert isinstance(bars, list)
        assert isinstance(year, int)
        extract = list()
        while len(bars) > 0 and bars[0].dt.year == year:
            bar = bars.pop(0)
            extract.append(bar)
        return extract
        # }}}
    @classmethod  #__fillVoid# {{{
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
    @classmethod  #__removeVoid# {{{
    def __removeVoid(cls, bars: list) -> list:
        i = 0
        while i < len(bars):
            if isinstance(bars[i], _Manager.VoidBar):
                bars.pop(i)
            else:
                i += 1
        return bars
    # }}}
    @classmethod  #__choseConverter# {{{
    def __choseConverter(cls, out_type: DataType) -> Callable:
        if out_type.toTimedelta() <= timedelta(days=1):
            conv = cls.__convertSmallTimeFrame
        elif out_type.value == "W":
            conv = cls.__convertWeekTimeFrame
        elif out_type.value == "M":
            conv = cls.__convertMonthTimeFrame
        return conv
    # }}}
    @classmethod  #__convertSmallTimeFrame# {{{
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
    @classmethod  #__convertWeekTimeFrame# {{{
    def __convertWeekTimeFrame(cls, bars, in_type, out_type):
        assert in_type.toTimedelta() == timedelta(days=1)
        bars = cls.__fillVoid(bars, in_type)
        period = out_type.toTimedelta()
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
    @classmethod  #__convertMonthTimeFrame# {{{
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
                else:
                    last += 1
            new_bar = cls.__join(bars[first:last])
            if new_bar is not None:
                converted.append(new_bar)
            first = last
            last += 1
        return converted
    # }}}
    @classmethod  #__join# {{{
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
            opn =       bars[0].open
            hgh =       max([bar.high for bar in bars])
            low =       min([bar.low for bar in bars])
            close =     bars[-1].close
            volume =    sum([bar.vol for bar in bars])
            join_bar =  _Bar(dt_first_bar, opn, hgh, low, close, volume)
            return join_bar
        else:
            return None  # возвращаем None, если не было баров с данными
    # }}}
# }}}


if __name__ == "__main__":
    ...

