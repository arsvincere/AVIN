#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

from __future__ import annotations
import abc
from datetime import datetime, date, UTC
from avin.const import Usr, DAY_BEGIN
from avin.data import Id, Exchange, AssetType, Data
from avin.core.chart import Chart
from avin.core.timeframe import TimeFrame
from avin.utils import Cmd, now
from avin.logger import logger


class Asset(metaclass=abc.ABCMeta):# {{{
    @abc.abstractmethod  #__init__# {{{
    def __init__(self, ID: Id, parent=None):
        self._ID = ID
        self._charts = dict()
        self.__parent = parent
    # }}}
    def __str__(self):# {{{
        return str(self._ID)
    # }}}
    def __eq__(self, other):# {{{
        return self._ID == other._ID
    # }}}
    @property  #ID# {{{
    def ID(self):
        return self._ID
    # }}}
    @property  #exchange# {{{
    def exchange(self):
        return self._ID.exchange
    # }}}
    @property  #type# {{{
    def type(self):
        return self._ID.type
    # }}}
    @property  #ticker# {{{
    def ticker(self):
        return self._ID.ticker
    # }}}
    @property  #name# {{{
    def name(self):
        return self._ID.name
    # }}}
    @property  #figi# {{{
    def figi(self):
        return self._ID.figi
    # }}}
    @property  #dir_path# {{{
    def dir_path(self):
        return self._ID.dir_path
        # }}}
    @property  #analytic_dir# {{{
    def analytic_dir(self):
        return Cmd.path(self._ID.dir_path, "analytic")
    # }}}
    @property  #broker_info# {{{
    def brocker_info(self):
        return Data.info(self._ID)
    # }}}
    def chart(self, timeframe: TimeFrame | str) -> Chart:# {{{
        if isinstance(timeframe, str):
            timeframe = TimeFrame(timeframe)
        return self._charts.get(timeframe, None)
    # }}}
    def cacheChart(# {{{
        self,
        timeframe: TimeFrame | str,
        begin: date | str=None,
        end: date | str=None,
        ):

        timeframe, begin, end = self.__checkArgs(timeframe, begin, end)
        chart = Chart(self, timeframe, begin, end)
        self._charts[timeframe] = chart
        return True
    # }}}
    def clearCache(self):# {{{
        self._charts.clear()
    # }}}
    def loadChart(# {{{
        self,
        timeframe: Timeframe | str,
        begin: datetime | str=None,
        end: datetime | str=None,
        ):
        logger.debug(
            f"{self.__class__.__name__}.loadChart "
            "{self.ticker}-{timeframe}"
            )
        timeframe, begin, end = self.__checkArgs(timeframe, begin, end)
        return Chart(self, timeframe, begin, end)
    # }}}
    def parent(self):# {{{
        return self.__parent
    # }}}
    def setParent(self, parent):# {{{
        self.__parent = parent
    # }}}
    def data(# {{{
        self,
        timeframe: TimeFrame | str,
        begin: datetime,
        end: datetime
        ) -> DataFrame:

        """ Return DataFrame """
        assert False
    # }}}
    @classmethod  #load# {{{
    def load(cls, file_path: str):
        ID = Id.load(file_path)
    # }}}
    @classmethod  #byId #{{{
    def byId(cls, ID: Id):
        asset = cls.__getCertainTypeAsset(ID)
        return asset
    # }}}
    @classmethod  #byTicker# {{{
    def byTicker(cls, exchange: Exchange, asset_type: AssetType, ticker: str):
        ID = Data.find(exchange, asset_type, ticker)
        return Asset.__getCertainTypeAsset(ID)
    # }}}
    @classmethod  #byFigi# {{{
    def byFigi(cls, exchange: Exchange, asset_type: AssetType, figi: str):
        ID = Data.find(exchange, asset_type, figi)
        return Asset.__getCertainTypeAsset(ID)
    # }}}
    @classmethod  #byUid# {{{
    def byUid(cls, exchange: Exchange, asset_type: AssetType, uid: str):
        ID = Data.find(exchange, asset_type, uid)
        return Asset.__getCertainTypeAsset(ID)
    # }}}
    @classmethod  #toJson# {{{
    def toJson(cls, asset):
        return Id.toJson(asset.ID)
    # }}}
    @classmethod  #fromJson# {{{
    def fromJson(cls, obj):
        ID = Id.fromJson(obj)
        asset = Asset.byId(ID)
        return asset
    # }}}
    @classmethod  #__checkArgs# {{{
    def __checkArgs(cls, timeframe, begin, end):
        # TODO сделать реальную проверку аргументов, а не только
        # форматирование
        if isinstance(timeframe, TimeFrame):
            pass
        elif isinstance(timeframe, str):
            timeframe = TimeFrame(timeframe)
        else:
            logger.critical(
                f"Wrong timeframe='{timeframe}', use valid 'str' "
                "or class TimeFrame"
                )
            exit(1)
        if isinstance(begin, str):
            begin = datetime.combine(
                date.fromisoformat(begin),
                Exchange.MOEX.SESSION_BEGIN,
                tzinfo=UTC
                )
        if isinstance(end, str):
            end = datetime.combine(
                date.fromisoformat(end),
                DAY_BEGIN,
                tzinfo=UTC
                )
        if begin is None and end is None:
            period = timeframe * Chart.DEFAULT_BARS_COUNT
            begin = now() - period
            end = now()

        return timeframe, begin, end

    # }}}
    @classmethod  #__getCertainTypeAsset# {{{
    def __getCertainTypeAsset(cls, ID: Id):
        if ID.type == AssetType.Index:
            return Index(ID)
        elif ID.type == AssetType.Share:
            return Share(ID)
    # }}}
# }}}
class Index(Asset):# {{{
    def __init__(self, ID: Id, parent=None):# {{{
        assert ID.type == AssetType.Index
        super().__init__(ID, parent)
        self.__parent = parent
    # }}}
# }}}
class Share(Asset):# {{{
    """ doc# {{{
    ...
    """
    # }}}
    def __init__(self, ID: Id, parent=None):# {{{
        assert ID.type == AssetType.Share
        super().__init__(ID, parent)
        self.__book = None
        self.__tic = None
    # }}}
    @property  # uid{{{
    def uid(self):
        return self.brocker_info["uid"]
    # }}}
    @property  # lot{{{
    def lot(self):
        return int(self.brocker_info["lot"])
    # }}}
    @property  # min_price_step{{{
    def min_price_step(self):
        return float(self.brocker_info["min_price_increment"])
    # }}}
# }}}

class AssetList():# {{{
    def __init__(self, name="unnamed", parent=None):# {{{
        logger.debug(f"AssetList.__init__({name})")
        self.__name = name
        self.__assets = list()
        self.__parent = parent
    # }}}
    def __getitem__(self, index) -> Asset:# {{{
        assert index < len(self.__assets)
        return self.__assets[index]
    # }}}
    def __iter__(self):# {{{
        return iter(self.__assets)
    # }}}
    def __contains__(self, asset: Asset) -> bool:# {{{
        for i in self.__assets:
            if i.ID == asset.ID:
                return True
        return False
    # }}}
    @property  #name{{{
    def name(self) -> str:
        return self.__name
    @name.setter
    def name(self, name):
        assert isinstance(name, str)
        self.__name = name
    # }}}
    @property  #assets{{{
    def assets(self) -> list[Asset]:
        return self.__assets
    @assets.setter
    def assets(self, assets):
        assert isinstance(assets, list)
        for i in assets:
            assert isinstance(i, Asset)
        self.__assets = assets
    # }}}
    @property  #count{{{
    def count(self) -> int:
        return len(self.__assets)
    # }}}
    @property  #path{{{
    def path(self) -> str:
        path = Cmd.path(self.dir_path, f"{self.__name}.al")
        return path
    # }}}
    @property  #dir_path{{{
    def dir_path(self) -> str:
        if self.__parent:
            return self.__parent.dir_path
        else:
            return Usr.ASSET
    # }}}
    def add(self, asset: Asset) -> None:# {{{
        assert isinstance(asset, Asset)
        if asset not in self:
            self.__assets.append(asset)
            asset.setParent(self)
            return

        logger.warning(f"{asset} already in list '{self.name}'")
    # }}}
    def remove(self, asset: Asset) -> None:# {{{
        logger.debug(f"AssetList.remove({asset.ticker})")
        try:
            self.__assets.remove(asset)
            return True
        except ValueError as err:
            logger.exception(
                f"AssetList.remove(asset): Fail: "
                f"инструмент '{asset.ticker}' нет в списке '{self.name}'",
                )
            return False
    # }}}
    def clear(self) -> None:# {{{
        self.__assets.clear()
    # }}}
    def find(self, ID: Id):# {{{
        for i in self.__assets:
            if i.ID == ID:
                return i
        return None
    # }}}
    @classmethod  #save# {{{
    def save(cls, asset_list, path=None) -> None:
        if path is None:
            path = asset_list.path
        obj = AssetList.toJson(asset_list)
        Cmd.saveJson(obj, path)
    # }}}
    @classmethod  #load# {{{
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
    @classmethod  #rename# {{{
    def rename(cls, asset_list, new_name) -> None:
        if Cmd.isExist(asset_list.path):
            new_path = Cmd.path(asset_list.dir_path, f"{new_name}.al")
            Cmd.replace(asset_list.path, new_path)
        asset_list.__name = new_name
    # }}}
    @classmethod  #copy# {{{
    def copy(cls, asset_list: AssetList, new_name: str) -> None:
        new_list = AssetList(new_name)
        new_list.assets = asset_list.assets
        new_path = Cmd.path(asset_list.dir_path, f"{new_name}.al")
        AssetList.save(new_list, new_path)
    # }}}
    @classmethod  #delete# {{{
    def delete(cls, asset_list) -> None:
        file_path = asset_list.path
        if not Cmd.isExist(file_path):
            logger.error(
                f"Fail delete asset list, file not exist '{file_path}'"
                )
        Cmd.delete(file_path)
    # }}}
    @classmethod  #request# {{{
    def request(cls, name) -> str:
        """If AssetList with name='{name}' exist, return his file_path"""
        path = Cmd.path(Usr.ASSET, f"{name}.al")
        if Cmd.isExist(path):
            return path
        else:
            return None
    # }}}
    @classmethod  #requestAll# {{{
    def requestAll(cls) -> list[str]:
        """Return list[file_path] all exist AssetList"""
        files = Cmd.getFiles(Usr.ASSET, full_path=True)
        return files
    # }}}
    @classmethod  #toJson# {{{
    def toJson(cls, asset_list):
        obj = list()
        for asset in asset_list:
            json_id = Id.toJson(asset.ID)
            obj.append(json_id)
        return obj
    # }}}
# }}}

