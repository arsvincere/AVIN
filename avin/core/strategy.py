#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

"""Doc"""

from __future__ import annotations

import abc

from avin.const import Usr
from avin.core.asset import AssetList
from avin.core.order import Order
from avin.core.trade import Trade, TradeList
from avin.utils import Cmd, Signal

# XXX: а что если код юзерских стратегий тоже хранить в базе данных...
# удобно же... или нихуя не удобно? Зато его можно будет не импортить,
# а делать eval, или че там для нескольких строк кода...
# можно из БД загружать текст, создавать временный файл с кодом, и оттуда
# его импортить, но сохранять потом снова в БД.
# - вопрос?
#   нахер этот геморой нужен?
#   ну например чтобы дампнул базу - и точно уверен что у тебя все есть
#   а исходный код на гитхабе, а все ресурсы в БД.
#   подумать


class Strategy(metaclass=abc.ABCMeta):  # {{{
    """Signal"""  # {{{

    tradeOpened = Signal(Trade)
    tradeClosed = Signal(Trade)

    # }}}
    def __init__(self, name, version):  # {{{
        self.__name = name
        self.__version = version

    # }}}
    def __str__(self):  # {{{
        return f"{self.name}-{self.version}"

    # }}}
    @property  # name  # {{{
    def name(self):
        return self.__name

    # }}}
    @property  # version  # {{{
    def version(self):
        return self.__version

    # }}}
    @property  # config  # {{{
    def config(self):
        return self.__cfg

    # }}}
    @property  # timeframe_list  # {{{
    def timeframe_list(self):
        return self.__cfg["timeframe_list"]

    # }}}
    @property  # account  # {{{
    def account(self):
        return self.__account

    # }}}
    @property  # long_list  # {{{
    def long_list(self):
        return self.__long_list

    # }}}
    @property  # short_list  # {{{
    def short_list(self):
        return self.__short_list

    # }}}
    @property  # active_trades  # {{{
    def active_trades(self):
        return self.__active_trades

    # }}}
    @property  # path  # {{{
    def path(self):
        path = Cmd.path(self.dir_path, f"{self.version}.py")
        return path

    # }}}
    @property  # dir_path  # {{{
    def dir_path(self):
        path = Cmd.path(Usr.STRATEGY, self.name)
        return path

    # }}}
    def setAccount(self, account: Account):  # {{{
        self.__account = account

    # }}}
    async def setLongList(self, asset_list: AssetList):  # {{{
        asset_list.name = str(self) + "-long"
        self.__long_list = asset_list
        AssetList.save(asset_list)

    # }}}
    async def setShortList(self, asset_list: AssetList):  # {{{
        asset_list.name = str(self) + "-short"
        self.__short_list = asset_list
        AssetList.save(asset_list)

    # }}}
    async def start(self):
        raise NotImplementedError()

    # }}}
    async def finish(self):
        raise NotImplementedError()

    # }}}
    async def connect(self, asset_list: AssetList):
        raise NotImplementedError()

    # }}}
    async def onTradeOpened(self, trade: Trade):
        logger.info(str(trade))

    # }}}
    async def onTradeClosed(self, trade: Trade):
        logger.info(f"Trade closed: {trade.result()}")

    # }}}
    @classmethod  # load# {{{
    async def load(cls, name: str, version: str):
        module = name.lower()
        path = f"user.strategy.{name}.{version}"
        modul = importlib.import_module(path)
        UStrategy = modul.__getattribute__("UStrategy")
        strategy = UStrategy(name, version)

        await strategy.__loadConfig()
        await strategy.__loadLongList()
        await strategy.__loadShortList()
        await strategy.__loadTradeList()

        return strategy

    # }}}
    @classmethod  # versions# {{{
    def versions(cls, strategy_name: str):
        path = Cmd.path(STRATEGY_DIR, strategy_name)
        files = Cmd.getFiles(path)
        files = Cmd.select(files, extension=".py")
        ver_list = list()
        for file in files:
            ver = file.replace(".py", "")
            ver_list.append(ver)
        return ver_list

    # }}}
    async def saveNewTrade(self, trade: Trade):  # {{{
        await trade.opened.async_connect(self.onTradeOpened)
        await trade.closed.async_connect(self.onTradeClosed)
        self.active_trades.add(trade)

        await Trade.save(trade)
        await TradeList.save(self.active_trades)

    # }}}
    async def postOrder(self, trade: Trade, order: Order):  # {{{
        await self.account.post(order)
        assert order.status == Order.Status.POSTED

        await trade.setStatus(Trade.Status.POSTED)

    # }}}
    async def __loadConfig(self):  # {{{
        path = Cmd.path(self.dir_path, "config.cfg")
        if Cmd.isExist(path):
            self.__cfg = Cmd.loadJson(path)
            return

        self.__cfg = None

    # }}}
    async def __loadLongList(self):  # {{{
        list_name = str(self) + "-long"
        self.__long_list = await AssetList.load(list_name)

    # }}}
    async def __loadShortList(self):  # {{{
        list_name = str(self) + "-short"
        self.__short_list = await AssetList.load(list_name)

    # }}}
    async def __loadTradeList(self):  # {{{
        list_name = str(self)
        self.__active_trades = await TradeList.load(list_name)

    # }}}


# }}}

if __name__ == "__main__":
    ...
