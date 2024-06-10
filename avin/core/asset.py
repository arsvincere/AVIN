#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

from __future__ import annotations
from avin.data import Id, Exchange, AssetType, Data
from avin.core.chart import Chart
from avin.core.timeframe import TimeFrame
from avin.logger import logger
from avin.utils import Cmd, now
import abc

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
    def chart(self, timeframe: TimeFrame | str,):# {{{
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
    @classmethod  #load# {{{
    def load(cls, file_path: str):
        ID = Id.load(file_path)
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
    @classmethod  #__checkArgs# {{{
    def __checkArgs(cls, timeframe, begin, end):
        # TODO сделать реальную проверку аргументов, а не только
        # форматирование
        if isinstance(timeframe, str):
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
                MOEX.SESSION_BEGIN,
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
    def __getitem__(self, index):# {{{
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
    def name(self):
        return self.__name
    @name.setter
    def name(self, name):
        assert isinstance(name, str)
        self.__name = name
    # }}}
    @property  #assets{{{
    def assets(self):
        return self.__assets
    @assets.setter
    def assets(self, assets):
        assert isinstance(assets, list)
        for i in assets:
            assert isinstance(i, (Share, Index))
        self.__assets = assets
    # }}}
    @property  #count{{{
    def count(self):
        return len(self.__assets)
    # }}}
    @property  #path{{{
    def path(self):
        path = Cmd.path(self.dir_path, f"{self.__name}.al")
        return path
    # }}}
    @property  #dir_path{{{
    def dir_path(self):
        if self.__parent:
            return self.__parent.dir_path
        else:
            return ASSET_DIR
    # }}}
    def add(self, asset):# {{{
        assert isinstance(asset, Asset)
        self.__assets.append(asset)
        asset.setParent(self)
    # }}}
    def remove(self, asset):# {{{
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
    def clear(self):# {{{
        self.__assets.clear()
    # }}}
    def find(self, figi=None, uid=None, ticker=None):# {{{
        for i in self.__assets:
            if i.figi == figi:
                return i
        return None
    # }}}
    def receive(self, event_bar):# {{{
        asset = self.find(figi=event_bar.figi)
        timeframe = event_bar.timeframe
        asset.chart(timeframe).update(new_bars=[event_bar.bar, ])
        bar_time = (event_bar.bar.dt + MSK_TIME_DIF).time().strftime("%H:%M")
        logger.info(
            f"AssetList receive new bar "
            f"{asset.ticker}-{timeframe} {bar_time}"
            )
    # }}}
    @classmethod  #toJSON# {{{
    def toJSON(asset_list):
        obj = list()
        for asset in asset_list:
            ID = Asset.toJSON(asset)
            obj.append(ID)
        return obj
    # }}}
    @classmethod  #save# {{{
    def save(asset_list, path=None):
        if path is None:
            path = asset_list.path
        obj = AssetList.toJSON(asset_list)
        Cmd.saveJSON(obj, path)
    # }}}
    @classmethod  #load# {{{
    def load(path=None, name=None, parent=None):
        if path:
            assert name is None
            name = Cmd.name(path, extension=False)
        elif name:
            assert path is None
            path = Cmd.path(ASSET_DIR, f"{name}.al")
        alist = AssetList(name, parent=parent)
        obj = Cmd.loadJSON(path)
        for ID in obj:
            assert eval(ID["type"]) == AssetType.Share
            share = Share(ID["ticker"])
            alist.add(share)
        return alist
    # }}}
    @classmethod  #rename# {{{
    def rename(asset_list, new_name):
        if Cmd.isExist(asset_list.path):
            new_path = Cmd.path(asset_list.dir_path, f"{new_name}.al")
            Cmd.replace(asset_list.path, new_path)
        asset_list.__name = new_name
    # }}}
    @classmethod  #copy# {{{
    def copy(asset_list, new_name):
        if Cmd.isExist(asset_list.path):
            new_path = Cmd.path(asset_list.dir_path, f"{new_name}.al")
            Cmd.copyFile(asset_list.path, new_path)
            copy = AssetList.load(name=new_name)
            return copy
    # }}}
    @classmethod  #delete# {{{
    def delete(asset_list):
        file_path = asset_list.path
        if not Cmd.isExist(file_path):
            raise AssetError(
                f"AssetList.delete: список '{asset_list.name}' не найден"
                )
        Cmd.delete(file_path)
        return True
    # }}}
# }}}

