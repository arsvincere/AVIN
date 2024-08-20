#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

from __future__ import annotations

import abc
from datetime import UTC, date, datetime

from avin.const import DAY_BEGIN, Usr
from avin.core.chart import Chart
from avin.core.timeframe import TimeFrame
from avin.data import AssetType, DataSource, Exchange, InstrumentId
from avin.keeper import Keeper
from avin.logger import logger
from avin.utils import Cmd, now


class Asset(metaclass=abc.ABCMeta):  # {{{
    @abc.abstractmethod  # __init__# {{{
    def __init__(self, ID: Id, parent=None):
        self.__ID = ID
        self.__charts = dict()
        self.__parent = parent
        self.__info = None

    # }}}
    def __str__(self):  # {{{
        return str(self.__ID)

    # }}}
    def __eq__(self, other):  # {{{
        return self.__ID == other.__ID

    # }}}
    @property  # ID# {{{
    def ID(self):
        return self.__ID

    # }}}
    @property  # exchange# {{{
    def exchange(self):
        return self.__ID.exchange

    # }}}
    @property  # type# {{{
    def type(self):
        return self.__ID.type

    # }}}
    @property  # ticker# {{{
    def ticker(self):
        return self.__ID.ticker

    # }}}
    @property  # figi# {{{
    def figi(self):
        return self.__ID.figi

    # }}}
    @property  # name# {{{
    def name(self):
        return self.__ID.name

    # }}}
    @property  # info# {{{
    def info(self):
        if not self.__info:
            logger.error(f"Info not loaded, asset={self}")
            return None

        return self.__info

    # }}}
    def chart(self, timeframe: TimeFrame | str) -> Chart:  # {{{
        if isinstance(timeframe, str):
            timeframe = TimeFrame(timeframe)

        return self.__charts.get(timeframe, None)

    # }}}
    async def cacheChart(  # {{{
        self,
        timeframe: TimeFrame | str,
        begin: date | str = None,
        end: date | str = None,
    ) -> None:
        logger.debug(f"{self.__class__.__name__}.cacheChart()")

        # check args
        timeframe, begin, end = self.__checkArgs(timeframe, begin, end)

        # load chart and keep it
        chart = await Chart.load(self, timeframe, begin, end)
        self.__charts[timeframe] = chart

    # }}}
    async def loadChart(  # {{{
        self,
        timeframe: Timeframe | str,
        begin: datetime | str = None,
        end: datetime | str = None,
    ) -> Chart:
        logger.debug(f"{self.__class__.__name__}.loadChart()")

        # check args
        timeframe, begin, end = self.__checkArgs(timeframe, begin, end)

        # load chart and return it
        chart = await Chart.load(self, timeframe, begin, end)
        return chart

    # }}}
    async def loadInfo(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.loadInfo()")

        info = await Keeper.info(
            DataSource.TINKOFF, self.type, figi=self.figi
        )
        assert len(info) == 1
        self.__info = info[0]

    # }}}
    def parent(self):  # {{{
        return self.__parent

    # }}}
    def setParent(self, parent):  # {{{
        self.__parent = parent

    # }}}
    def data(  # {{{
        self,
        timeframe: TimeFrame | str,
        begin: datetime,
        end: datetime,
    ) -> DataFrame:
        # TODO: return dataframe
        assert False

    # }}}
    def clearCache(self):  # {{{
        self.__charts.clear()

    # }}}
    @classmethod  # byId #{{{
    def byId(cls, ID: Id) -> Asset:
        logger.debug(f"{cls.__name__}.byId()")

        asset = cls.__getCertainTypeAsset(ID)
        return asset

    # }}}
    @classmethod  # byTicker# {{{
    async def byTicker(
        cls, asset_type: AssetType, exchange: Exchange, ticker: str
    ) -> Asset:
        logger.debug(f"{cls.__name__}.byTicker()")

        asset = await Keeper.get(
            Asset, asset_type=asset_type, exchange=exchange, ticker=ticker
        )
        return asset

    # }}}
    @classmethod  # byFigi# {{{
    async def byFigi(cls, figi: str) -> Asset:
        logger.debug(f"{cls.__name__}.byFigi()")

        asset = await Keeper.get(Asset, figi=figi)
        return asset

    # }}}
    @classmethod  # fromRecord# {{{
    def fromRecord(cls, record):
        exchange = Exchange.fromStr(record["exchange"])
        asset_type = AssetType.fromStr(record["type"])
        ticker = record["ticker"]
        figi = record["figi"]
        name = record["name"]
        ID = InstrumentId(asset_type, exchange, ticker, figi, name)
        asset = Asset.byId(ID)
        return asset

    # }}}
    @classmethod  # __checkArgs# {{{
    def __checkArgs(cls, timeframe, begin, end):
        # check timeframe
        if isinstance(timeframe, TimeFrame):
            pass
        elif isinstance(timeframe, str):
            timeframe = TimeFrame(timeframe)
        else:
            logger.critical(
                f"Wrong timeframe='{timeframe}', use valid 'str' "
                "or class TimeFrame"
            )
            raise TypeError(timeframe)

        # check begin
        if isinstance(begin, str):
            begin = datetime.combine(
                date.fromisoformat(begin),
                Exchange.MOEX.SESSION_BEGIN,
                tzinfo=UTC,
            )

        # check end
        if isinstance(end, str):
            end = datetime.combine(
                date.fromisoformat(end),
                DAY_BEGIN,
                tzinfo=UTC,
            )

        # when begin & end == None, load DEFAULT_BARS_COUNT
        if begin is None and end is None:
            period = timeframe * Chart.DEFAULT_BARS_COUNT
            begin = now().replace(microsecond=0) - period
            end = now()

        if not isinstance(begin, datetime):
            logger.critical(f"Invalid begin='{begin}'")
            raise TypeError(begin)
        if not isinstance(end, datetime):
            logger.critical(f"Invalid end='{end}'")
            raise TypeError(end)

        return timeframe, begin, end

    # }}}
    @classmethod  # __getCertainTypeAsset# {{{
    def __getCertainTypeAsset(cls, ID: Id):
        if ID.type == AssetType.INDEX:
            index = Index(ID)
            return index
        elif ID.type == AssetType.SHARE:
            share = Share(ID)
            return share

        logger.critical(f"Unknown asset type={ID.type}")
        assert False

    # }}}


# }}}
class Index(Asset):  # {{{
    def __init__(self, ID: Id, parent=None):  # {{{
        assert ID.type == AssetType.INDEX
        super().__init__(ID, parent)
        self.__parent = parent

    # }}}


# }}}
class Share(Asset):  # {{{
    # {{{-- doc
    """ """

    # }}}

    def __init__(self, ID: Id, parent=None):  # {{{
        assert ID.type == AssetType.SHARE
        super().__init__(ID, parent)
        self.__book = None
        self.__tic = None

    # }}}
    @property  # uid{{{
    def uid(self):
        return self.info["uid"]

    # }}}
    @property  # lot{{{
    def lot(self):
        return int(self.info["lot"])

    # }}}
    @property  # min_price_step{{{
    def min_price_step(self):
        return float(self.info["min_price_increment"])

    # }}}


# }}}


class AssetList:  # {{{
    def __init__(self, name: str = "unnamed", parent=None):  # {{{
        logger.debug(f"AssetList.__init__({name})")
        self.__name = name
        self.__assets = list()
        self.__parent = parent

    # }}}
    def __getitem__(self, index: int) -> Asset:  # {{{
        assert index < len(self.__assets)
        return self.__assets[index]

    # }}}
    def __iter__(self):  # {{{
        return iter(self.__assets)

    # }}}
    def __contains__(self, asset: Asset) -> bool:  # {{{
        return any(i.ID == asset.ID for i in self.__assets)

    # }}}
    @property  # name{{{
    def name(self) -> str:
        return self.__name

    @name.setter
    def name(self, name: str):
        assert isinstance(name, str)
        self.__name = name

    # }}}
    @property  # assets{{{
    def assets(self) -> list[Asset]:
        return self.__assets

    @assets.setter
    def assets(self, assets):
        assert isinstance(assets, list)
        for i in assets:
            assert isinstance(i, Asset)
        self.__assets = assets

    # }}}
    @property  # count{{{
    def count(self) -> int:
        return len(self.__assets)

    # }}}
    @property  # path{{{
    def path(self) -> str:
        path = Cmd.path(self.dir_path, f"{self.__name}.al")
        return path

    # }}}
    @property  # dir_path{{{
    def dir_path(self) -> str:
        if self.__parent:
            return self.__parent.dir_path
        else:
            return Usr.ASSET

    # }}}
    def add(self, asset: Asset) -> None:  # {{{
        assert isinstance(asset, Asset)
        if asset not in self:
            self.__assets.append(asset)
            asset.setParent(self)
            return

        logger.warning(f"{asset} already in list '{self.name}'")

    # }}}
    def remove(self, asset: Asset) -> None:  # {{{
        logger.debug(f"AssetList.remove({asset.ticker})")
        try:
            self.__assets.remove(asset)
            return True
        except ValueError:
            logger.exception(
                f"AssetList.remove(asset): Fail: "
                f"инструмент '{asset.ticker}' нет в списке '{self.name}'",
            )
            return False

    # }}}
    def clear(self) -> None:  # {{{
        self.__assets.clear()

    # }}}
    def find(self, ID: Id):  # {{{
        for i in self.__assets:
            if i.ID == ID:
                return i
        return None

    # }}}
    @classmethod  # save# {{{
    def save(cls, asset_list, path=None) -> None:
        if path is None:
            path = asset_list.path
        obj = AssetList.toJson(asset_list)
        Cmd.saveJson(obj, path)

    # }}}
    @classmethod  # load# {{{
    def load(cls, file_path, parent=None) -> AssetList:
        name = Cmd.name(file_path)
        alist = AssetList(name, parent=parent)
        list_obj = Cmd.loadJson(file_path)
        for id_obj in list_obj:
            ID = Id.fromJson(id_obj)
            asset = Asset.byId(ID)
            alist.add(asset)
        return alist

    # }}}
    @classmethod  # rename# {{{
    def rename(cls, asset_list, new_name) -> None:
        if Cmd.isExist(asset_list.path):
            new_path = Cmd.path(asset_list.dir_path, f"{new_name}.al")
            Cmd.replace(asset_list.path, new_path)
        asset_list.__name = new_name

    # }}}
    @classmethod  # copy# {{{
    def copy(cls, asset_list: AssetList, new_name: str) -> None:
        new_list = AssetList(new_name)
        new_list.assets = asset_list.assets
        new_path = Cmd.path(asset_list.dir_path, f"{new_name}.al")
        AssetList.save(new_list, new_path)

    # }}}
    @classmethod  # delete# {{{
    def delete(cls, asset_list) -> None:
        file_path = asset_list.path
        if not Cmd.isExist(file_path):
            logger.error(
                f"Fail delete asset list, file not exist '{file_path}'"
            )
        Cmd.delete(file_path)

    # }}}
    @classmethod  # request# {{{
    def request(cls, name) -> str:
        """If AssetList with name='{name}' exist, return his file_path"""
        path = Cmd.path(Usr.ASSET, f"{name}.al")
        if Cmd.isExist(path):
            return path
        else:
            return None

    # }}}
    @classmethod  # requestAll# {{{
    def requestAll(cls) -> list[str]:
        """Return list[file_path] all exist AssetList"""
        files = Cmd.getFiles(Usr.ASSET, full_path=True)
        return files

    # }}}
    @classmethod  # toJson# {{{
    def toJson(cls, asset_list):
        obj = list()
        for asset in asset_list:
            json_id = Id.toJson(asset.ID)
            obj.append(json_id)
        return obj

    # }}}


# }}}
