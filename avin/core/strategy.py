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
from datetime import datetime

from avin.config import Usr
from avin.core.account import Account
from avin.core.asset import AssetList
from avin.core.id import Id
from avin.core.order import MarketOrder, Order, StopLoss, TakeProfit
from avin.core.trade import Trade, TradeList
from avin.utils import AsyncSignal, Cmd, logger, round_price


class Strategy(metaclass=abc.ABCMeta):
    """Signal"""  # {{{

    tradeOpened = AsyncSignal(Trade)
    tradeClosed = AsyncSignal(Trade)

    # }}}
    @abc.abstractmethod  # __init__  # {{{
    def __init__(self, name: str, version: str):
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
        # TODO: здесь нужно преобразование в таймфреймы делать
        # а не в трейдере. Манипулировать данными - Чем ближе к источнику
        # тем лучше.
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
        logger.info(f":: {self} set account={account.name}")
        self.__account = account

    # }}}
    async def setLongList(self, asset_list: AssetList):  # {{{
        asset_list.name = str(self) + "-long"
        self.__long_list = asset_list
        await AssetList.save(asset_list)

    # }}}
    async def setShortList(self, asset_list: AssetList):  # {{{
        asset_list.name = str(self) + "-short"
        self.__short_list = asset_list
        await AssetList.save(asset_list)

    # }}}
    async def createTrade(  # {{{
        self, dt: datetime, trade_type: Trade.Type, asset_id: InstrumentId
    ):
        logger.debug("Strategy.createTrade()")

        trade = Trade(
            dt=dt,
            strategy=self.name,
            version=self.version,
            trade_type=trade_type,
            asset_id=asset_id,
            status=Trade.Status.INITIAL,
            trade_id=Id.newId(),
        )
        await self.__connectTradeSignals(trade)
        self.__active_trades.add(trade)
        logger.info(f":: Created trade {trade}")

        # update db
        await Trade.save(trade)
        await TradeList.save(self.__active_trades)

        return trade

    # }}}
    async def createMarketOrder(  # {{{
        self, direction: Order.Direction, asset_id: InstrumentId, lots: int
    ) -> MarketOrder:
        logger.debug("Strategy.createMarketOrder()")

        if not asset_id.info:
            await asset_id.cacheInfo()

        order = MarketOrder(
            account_name=self.account.name,
            direction=direction,
            asset_id=asset_id,
            lots=lots,
            quantity=lots * asset_id.lot,
            status=Order.Status.NEW,
            order_id=Id.newId(),
        )
        logger.info(f"{self} create order {order}")

        await Order.save(order)
        return order

    # }}}
    async def createStopLoss(  # {{{
        self, trade: Trade, stop_percent: float
    ) -> StopLoss:
        logger.debug("Strategy.createStopLoss()")

        # TODO:
        # блять надо с этим что то делать
        if not trade.asset_id.info:
            await trade.asset_id.cacheInfo()

        if trade.type == Trade.Type.LONG:
            direction = Order.Direction.SELL
        else:
            direction = Order.Direction.BUY

        if trade.type == Trade.Type.LONG:
            stop = trade.average() * (1 - stop_percent / 100)
            stop = round_price(stop, trade.asset_id.min_price_step)
        else:
            stop = trade.average() * (1 + stop_percent / 100)
            stop = round_price(stop, trade.asset_id.min_price_step)

        stop_loss = StopLoss(
            account_name=self.account.name,
            direction=direction,
            asset_id=trade.asset_id,
            lots=trade.lots(),
            quantity=trade.quantity(),
            stop_price=stop,
            exec_price=None,
            status=Order.Status.NEW,
            order_id=Id.newId(),
            trade_id=trade.trade_id,
        )
        logger.info(f"{self} create order {stop_loss}")

        await Order.save(stop_loss)
        await trade.attachOrder(stop_loss)
        return stop_loss

    # }}}
    async def createTakeProfit(  # {{{
        self, trade: Trade, take_percent: float
    ) -> TakeProfit:
        logger.debug("Strategy.createStopLoss()")

        if not trade.asset_id.info:
            await trade.asset_id.cacheInfo()

        if trade.type == Trade.Type.LONG:
            direction = Order.Direction.SELL
        else:
            direction = Order.Direction.BUY

        if trade.type == Trade.Type.LONG:
            take = trade.average() * (1 + take_percent / 100)
            take = round_price(take, trade.asset_id.min_price_step)
        else:
            take = trade.average() * (1 - take_percent / 100)
            take = round_price(take, trade.asset_id.min_price_step)

        take_profit = TakeProfit(
            account_name=self.account.name,
            direction=direction,
            asset_id=trade.asset_id,
            lots=trade.lots(),
            quantity=trade.quantity(),
            stop_price=take,
            exec_price=take,
            status=Order.Status.NEW,
            order_id=Id.newId(),
            trade_id=trade.trade_id,
        )
        logger.info(f"{self} create order {take_profit}")

        await Order.save(take_profit)
        await trade.attachOrder(take_profit)
        return take_profit

    # }}}
    async def postOrder(self, order: Order):  # {{{
        logger.debug(f"Strategy.postOrder({order})")
        trade = self.active_trades.find(order.trade_id)
        await trade.setStatus(Trade.Status.POST_ORDER)

        result = await self.account.post(order)

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
        if not result:
            assert False, "ордер не выставился"

        # TODO:  ДА! на будущее - нужна возможность ручного управления
        # трейдами их ордерами и операциями. Гибко. Так чтобы и в реалтайме
        # можно было все разрулить и потом в базе поправить если какой то
        # косяк. А там уже когда наработаются ситуации, можно будет делать
        # автоматическое поведение для частых случаев.

    # }}}
    async def closeTrade(self, trade: Trade):  # {{{
        logger.debug(f"Strategy.closeTrade({trade})")
        await trade.setStatus(Trade.Status.CLOSING)

        # TODO: здесь еще надо проверять оставшиеся лимитные и
        # стоп ордера по этому трейду и их тоже отменять

        # create order
        lots = abs(trade.lots())
        d = Order.Direction.SELL if trade.lots() > 0 else Order.Direction.BUY
        order = await self.createMarketOrder(
            direction=d, asset_id=trade.asset_id, lots=lots
        )

        # attach & post this order
        await trade.attachOrder(order)
        await self.postOrder(order)

    # }}}

    @abc.abstractmethod  # start  # {{{
    async def start(self):
        logger.info(f":: Strategy {self} started")

    # }}}
    @abc.abstractmethod  # finish  # {{{
    async def finish(self):
        logger.info(f":: Strategy {self} finished")

    # }}}
    @abc.abstractmethod  # connect  # {{{
    async def connect(self, asset_list: AssetList):
        logger.info(f":: Strategy {self} connecting")

    # }}}
    @abc.abstractmethod  # onTradeOpened  # {{{
    async def onTradeOpened(self, trade: Trade):
        logger.info(f"Trade opened: '{trade}'")
        logger.info(f"Trade open dt: '{trade.openDatetime()}'")

    # }}}
    @abc.abstractmethod  # onTradeClosed  # {{{
    async def onTradeClosed(self, trade: Trade):
        logger.info(f"Trade closed: '{trade}'")
        logger.info(f"Trade closed result: {trade.result()}")

    # }}}

    @classmethod  # load# {{{
    async def load(cls, name: str, version: str) -> Strategy:
        path = f"usr.strategy.{name}.{version}"
        modul = importlib.import_module(path)
        UStrategy = modul.__getattribute__("UStrategy")
        strategy = UStrategy()

        await strategy.__loadConfig()
        await strategy.__loadLongList()
        await strategy.__loadShortList()
        await strategy.__loadTradeList()

        return strategy

    # }}}
    @classmethod  # versions# {{{
    def versions(cls, strategy_name: str):
        path = Cmd.path(Usr.STRATEGY, strategy_name)
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


if __name__ == "__main__":
    ...
