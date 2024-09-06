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
import importlib

from avin.const import Usr
from avin.core.asset import AssetList
from avin.core.order import Order
from avin.core.trade import Trade, TradeList
from avin.utils import Cmd, Signal, logger

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

# TODO: сделай для тестов отдельную специальную стратегию,
# хуй знает там _Unit_test_strategy
# а этот класс надо сделать нормально - абстрактным


class Strategy(metaclass=abc.ABCMeta):  # {{{
    """Signal"""  # {{{

    tradeOpened = Signal(Trade)
    tradeClosed = Signal(Trade)

    # }}}
    def __init__(self, name, version):  # {{{
        self.__name = name
        self.__version = version
        self.__account = None
        self.__cfg = None
        self.__long_list = None
        self.__short_list = None
        self.__active_trades = None

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
    @property  # account  # {{{
    def account(self):
        return self.__account

    # }}}
    @property  # config  # {{{
    def config(self):
        return self.__cfg

    # }}}
    @property  # timeframe_list  # {{{
    def timeframe_list(self):
        return self.__cfg["timeframe_list"]

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
        logger.info(f":: Set account {self}={account.name}")
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

    async def start(self):  # {{{
        raise NotImplementedError()

    # }}}
    async def finish(self):  # {{{
        raise NotImplementedError()

    # }}}
    async def connect(self, asset_list: AssetList):  # {{{
        raise NotImplementedError()

    # }}}
    async def onTradeOpened(self, trade: Trade):  # {{{
        logger.info(f"Trade opened: '{trade}'")
        logger.info(f"Trade open dt: '{trade.openDatetime()}'")

    # }}}
    async def onTradeClosed(self, trade: Trade):  # {{{
        logger.info(f"Trade closed: '{trade}'")
        logger.info(f"Trade closed result: {trade.result()}")

    # }}}

    async def createTrade(  # {{{
        self, dt: datetime, trade_type: Trade.Type, asset: Asset
    ):
        trade = Trade(
            dt=dt,
            strategy=self.name,
            version=self.version,
            trade_type=trade_type,
            asset_id=asset.ID,
        )
        await self.__connectTradeSignals(trade)
        self.__active_trades.add(trade)

        # update db
        await Trade.save(trade)
        await TradeList.save(self.__active_trades)

        logger.info(f":: Created trade {trade}")
        return trade

    # }}}
    async def createMarketOrder(  # {{{
        self, direction: Order.Direction, asset_id: InstrumentId, lots: int
    ):
        # FIX:  надо как то через ИД добывать кол-во лотов
        # ассет сюда передавать тоже не удобно, хотя возможно...
        # во время процесс опенед трэйдес ассет то мы активный имеем...
        # но вообще конечно бред это все, количество лотов вообще
        # нужно включить в общие поля, не через json, а из json
        # как раз их выпилить на уровне модуля Data
        # и min_price_step тоже
        order = Order.Market(
            account_name=self.account.name,
            direction=direction,
            asset_id=asset_id,
            lots=lots,
            quantity=lots * 100,  # FIX:
        )
        await Order.save(order)

        logger.info(f"{self} create order {order}")
        return order

    # }}}
    async def postOrder(self, order: Order):  # {{{
        trade = self.active_trades.find(order.trade_id)
        # TODO: еще раз подумать, название статуса, может
        # OPENING???
        # POST_OPEN_ORDER???
        await trade.setStatus(Trade.Status.POST_ORDER)
        # FIX: а когда другой ордер будешь постить, на закрытие, тоже
        # статус окажется пост ордер, надо в другом месте статс ставить
        # или все таки заводить отдельную хуйню типо - открыть трейд
        # и внутри трейда ордера хранить не просто листом а
        # опен ордер, стоп ордер, тэйк ордер...
        # но это рождает геморой с БД... отдельный подтип ордера еще
        # добавлять..

        order = await self.account.post(order)

        # TODO: что делать если ордер не прошел???
        # может попробовать еще раз... добавить настройку в аккаунт
        # типо количество попыток выставить ордер, и если ордер все таки
        # не выставлен, то надо будет думать какая логика будет. В зависимости
        # от того на каком этапе трейд. На вскидку
        # - если трейд не открыт - просто проинформировать и хуй забить на
        #   на этот трейд, установить ему какой-нибудь статус типо не удалось
        #   и убрать его нахуй из активных трейдов
        # - если трейд открыт и он в убытке... срочно закрывать по маркету
        #   например..
        # - если трейд открыт и он в плюсе... ну пробовать снова закрывать
        #   по рынку закрывать, частями закрывать... ситуативно это все...
        #   может в такие моменты как раз и нужно ручное управление???
        # assert order.status == Order.Status.POSTED

        # TODO:  ДА! на будущее - нужна возможность ручного управления
        # трейдами их ордерами и операциями. Гибко. Так чтобы и в реалтайме
        # можно было все разрулить и потом в базе поправить если какой то
        # косяк. А там уже когда наработаются ситуации, можно будет делать
        # автоматическое поведение для частых случаев.

    # }}}
    async def closeTrade(self, trade: Trade):  # {{{
        await trade.setStatus(Trade.Status.CLOSING)

        # create order
        lots = abs(trade.lots())
        d = Order.Direction.SELL if trade.lots() > 0 else Order.Direction.BUY
        order = await self.createMarketOrder(
            direction=d, asset_id=trade.asset_id, lots=lots
        )

        # attach & post this order
        await trade.attachOrder(order)

        # постим этот ордер
        await self.postOrder(order)

    # }}}

    @classmethod  # load# {{{
    async def load(cls, name: str, version: str):
        module = name.lower()
        path = f"usr.strategy.{name}.{version}"
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
    async def __loadConfig(self):  # {{{
        path = Cmd.path(self.dir_path, "config.cfg")
        if Cmd.isExist(path):
            self.__cfg = Cmd.loadJson(path)
            return

        self.__cfg = None

    # }}}
    async def __loadLongList(self):  # {{{
        list_name = str(self) + "-long"
        asset_list = await AssetList.load(list_name)

        if asset_list:
            self.__long_list = asset_list
        else:
            self.__long_list = AssetList(list_name)
            await AssetList.save(self.__long_list)

    # }}}
    async def __loadShortList(self):  # {{{
        list_name = str(self) + "-short"
        asset_list = await AssetList.load(list_name)

        if asset_list:
            self.__short_list = asset_list
        else:
            self.__short_list = AssetList(list_name)
            await AssetList.save(self.__short_list)

    # }}}
    async def __loadTradeList(self):  # {{{
        # try load trade list or create new empty list
        list_name = str(self)
        trade_list = await TradeList.load(list_name)

        if trade_list:
            self.__active_trades = trade_list
        else:
            self.__active_trades = TradeList(list_name)
            await TradeList.save(self.__active_trades)

        # connect signals
        for trade in self.__active_trades:
            await self.__connectTradeSignals(trade)

    # }}}
    async def __connectTradeSignals(self, trade: Trade):  # {{{
        await trade.opened.async_connect(self.onTradeOpened)
        await trade.closed.async_connect(self.onTradeClosed)

    # }}}


# }}}

if __name__ == "__main__":
    ...
