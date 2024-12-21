#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

from __future__ import annotations

import importlib
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Iterator, Optional, TypeVar

from avin.config import Usr
from avin.const import Res
from avin.core.account import Account
from avin.core.asset import Asset, AssetList
from avin.core.direction import Direction
from avin.core.id import Id
from avin.core.order import (
    LimitOrder,
    MarketOrder,
    Order,
    StopLoss,
    TakeProfit,
)
from avin.core.risk import Risk
from avin.core.timeframe import TimeFrameList
from avin.core.trade import Trade, TradeList
from avin.data import Instrument
from avin.keeper import Keeper
from avin.utils import AsyncSignal, Cmd, logger, round_price

# all user strategys must have class name UStrategy for dynamic import
# see method Strategy.load(name, version)
# TypeVar declarate only for 'mypy' type checker
UStrategy = TypeVar("UStrategy")


class Strategy(ABC):  # {{{
    """Signal"""  # {{{

    tradeOpened = AsyncSignal(Trade)
    tradeClosed = AsyncSignal(Trade)

    # }}}

    # Abstract
    @abstractmethod  # __init__  # {{{
    def __init__(self, name: str, version: str):
        self.__name = name
        self.__version = version
        self.__cfg = None
        self.__account: Optional[Account] = None
        self.__active_trades = TradeList(name="")

    # }}}
    @abstractmethod  # timeframes  # {{{
    def timeframes(self) -> TimeFrameList:
        pass

    # }}}
    @abstractmethod  # start  # {{{
    async def start(self):
        logger.info(f":: Strategy {self} started")

    # }}}
    @abstractmethod  # finish  # {{{
    async def finish(self):
        logger.info(f":: Strategy {self} finished")

    # }}}
    @abstractmethod  # connect  # {{{
    async def connect(self, asset: Asset, long: bool, short: bool):
        logger.info(
            f":: Strategy {self} connect {asset.ticker} "
            f"long={long} short={short}"
        )

    # }}}
    @abstractmethod  # onTradeOpened  # {{{
    async def onTradeOpened(self, trade: Trade):
        # TODO: похоже эта пара методов
        # вообще не нужна абстрактной, она как и создание
        # ордеров просто общая для всех стратегий... но если
        # уж очень надо то можно и переопределить, а так то
        # херли, пусть будет не абстрактной

        dt = Usr.localTime(trade.openDateTime())
        string = (
            f"Trade="
            f"{dt} [{trade.status.name}] {trade.strategy}-{trade.version} "
            f"{trade.instrument.ticker} {trade.type.name.lower()}"
        )

        logger.info(f"   {string}")

        await Trade.update(trade)

    # }}}
    @abstractmethod  # onTradeClosed  # {{{
    async def onTradeClosed(self, trade: Trade):
        logger.info(f"   {trade} result: {trade.result()}")

        await self.__cancelActiveOrders(trade)

    # }}}

    def __str__(self):  # {{{
        return f"Strategy={self.name}-{self.version}"

    # }}}
    def __eq__(self, other):  # {{{
        assert isinstance(other, Strategy)
        return self.name == other.name and self.version == other.version

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
    @property  # active_trades  # {{{
    def active_trades(self):
        return self.__active_trades

    # }}}
    @property  # r_trade  # {{{
    def r_trade(self):
        """Риск на одну сделку из конфига"""
        return self.__cfg["r_trade"]

    # }}}
    @property  # r_strategy  # {{{
    def r_strategy(self):
        """Максимальный риск на всю стратегию до отключения"""
        return self.__cfg["r_strategy"]

    # }}}

    def setAccount(self, account: Account) -> None:  # {{{
        logger.info(f":: {self} set account={account.name}")
        self.__account = account

    # }}}
    def setTradeList(self, tlist: TradeList) -> None:  # {{{
        logger.info(f":: {self} set {tlist}")
        self.__active_trades = tlist
        # TODO: active trades - а самое ли это удачное название
        # что вообще делает эта переменная?
        # Трейды - должны иметь трейд лист куда они сохраняются
        # для этого стратегии нужно знать название трейд листа
        # с которым она работает, но допустим пусть она вообще
        # сам трейд лист принимает как аргрумент, аналогично как
        # и аккаунт.. хотя использует только имя трейд листа
        # ок.
        # Стратегия должна иметь доступ к своим активным трейдам...
        #

    # }}}

    async def createTrade(  # {{{
        self, dt: datetime, trade_type: Trade.Type, instrument: Instrument
    ):
        logger.debug("Strategy.createTrade()")

        trade = Trade(
            dt=dt,
            strategy=self.name,
            version=self.version,
            trade_type=trade_type,
            instrument=instrument,
            status=Trade.Status.INITIAL,
            trade_id=Id.newId(),
        )
        await self.__connectTradeSignals(trade)
        self.__active_trades.add(trade)
        logger.info(f"   {trade}")

        # update db
        await Trade.save(trade)

        return trade

    # }}}
    async def createMarketOrder(  # {{{
        self, direction: Direction, instrument: Instrument, lots: int
    ) -> MarketOrder:
        logger.debug("Strategy.createMarketOrder()")

        # TODO:
        # идея - передавать сюда trade, direction, lots
        # из них можно достать всю информацию, а во вторых
        # тут можно будет сразу связывание ордера с трейдом
        # сделать и в юзер стратегии не надо будет думать
        # об этих деталях реализации

        order = MarketOrder(
            account_name=self.account.name,
            direction=direction,
            instrument=instrument,
            lots=lots,
            quantity=lots * instrument.lot,
            status=Order.Status.NEW,
            order_id=Id.newId(),
        )
        # logger.info(f"  {self} create order {order}")

        await Order.save(order)
        return order

    # }}}
    async def createLimitOrder(  # {{{
        self,
        direction: Direction,
        instrument: Instrument,
        lots: int,
        price: float,
    ) -> LimitOrder:
        logger.debug("Strategy.createMarketOrder()")

        order = LimitOrder(
            account_name=self.account.name,
            direction=direction,
            instrument=instrument,
            lots=lots,
            quantity=lots * instrument.lot,
            price=price,
            status=Order.Status.NEW,
            order_id=Id.newId(),
        )
        # logger.info(f"  {self} create order {order}")

        await Order.save(order)
        return order

    # }}}
    async def createStopLoss(  # {{{
        self,
        trade: Trade,
        stop_percent: Optional[float] = None,
        stop_price: Optional[float] = None,
    ) -> StopLoss:
        logger.debug("Strategy.createStopLoss()")

        if stop_percent is not None:
            order = await self.__createStopLossByPercent(trade, stop_percent)
            return order

        if stop_price is not None:
            order = await self.__createStopLossByPrice(trade, stop_price)
            return order

        assert False, "stop_percent or stop_price must be not None"

    # }}}
    async def createTakeProfit(  # {{{
        self,
        trade: Trade,
        take_percent: Optional[float] = None,
        take_price: Optional[float] = None,
    ) -> TakeProfit:
        logger.debug("Strategy.createStopLoss()")

        if take_percent is not None:
            order = await self.__createTakeProfitByPercent(
                trade, take_percent
            )
            return order

        if take_price is not None:
            order = await self.__createTakeProfitByPrice(trade, take_price)
            return order

        assert False, "take_percent or take_price must be not None"

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
    async def cancelOrder(self, order: Order):  # {{{
        logger.debug(f"Strategy.cancelOrder({order})")

        result = await self.account.cancel(order)

        # TODO: что делать если ордер не отменился???
        if not result:
            assert False, "ордер не отменился"

    # }}}
    async def closeTrade(self, trade: Trade):  # {{{
        logger.debug(f"Strategy.closeTrade({trade})")

        if trade.status == Trade.Status.CLOSED:
            # FIX: не понимаю как и почему сюда прилетают иногда
            # закрытые уже трейды
            return

        await trade.setStatus(Trade.Status.CLOSING)

        # TODO: здесь еще надо проверять оставшиеся лимитные и
        # стоп ордера по этому трейду и их тоже отменять

        # create order
        lots = trade.lots()
        d = Direction.SELL if lots > 0 else Direction.BUY
        order = await self.createMarketOrder(
            direction=d, instrument=trade.instrument, lots=abs(lots)
        )

        # attach & post this order
        await trade.attachOrder(order)
        await self.postOrder(order)

    # }}}
    async def cancelTrade(self, trade: Trade):  # {{{
        logger.debug(f"Strategy.cancelTrade({trade})")

        assert trade.status.value < Trade.Status.OPENED.value

        # TODO: здесь еще надо проверять оставшиеся лимитные и
        # стоп ордера по этому трейду и их тоже отменять
        # лучше на аккаунт это переложить, там он пусть
        # разбирается с наличием активных ордеров по этому
        # трейду, ему там проще от брокера статус актуальный
        # запросить, чем отсюда ориентироваться на статусы
        # ордеров в runtime, лучше уж наверняка - у брокера узнать
        # for order in trade.orders:
        #     await self.account.cancelOrdersOf(trade)

        await trade.setStatus(Trade.Status.CANCELED)
        logger.info(f"   {trade}")

    # }}}

    def maxLots(self, trade: Trade) -> int:  # {{{
        logger.debug("Strategy.max_lots()")

        max_lots = Risk.maxLotsByRisk(
            r_trade=self.r_trade,
            open_price=trade.info["open_price"],
            stop_price=trade.info["stop_price"],
            lotX=trade.instrument.lot,
        )

        return max_lots

    # }}}

    @classmethod  # new  # {{{
    async def new(cls, name: str) -> UStrategy | None:
        logger.debug(f"{cls.__name__}.new()")

        # check name
        if not cls.checkStrategyName(name):
            return None

        # copy template to user directory
        template_path = Cmd.path(Res.TEMPLATE, "strategy")
        user_path = Cmd.path(Usr.STRATEGY, name)
        Cmd.copyDir(template_path, user_path)

        # load modul
        modul_path = f"usr.strategy.{name}.v1"
        modul = importlib.import_module(modul_path)
        UStrategy = modul.__getattribute__("UStrategy")

        # create
        strategy = UStrategy()
        strategy.__loadConfig()

        # save in db
        await Keeper.add(strategy)

        return strategy

    # }}}
    @classmethod  # copyVersion  # {{{
    async def copy(cls, strategy: Strategy, new_ver: str) -> UStrategy | None:
        # TODO: copy -> copyVersion
        logger.debug(f"{cls.__name__}.copy()")

        # check new name
        if not cls.checkVersionName(strategy, new_ver):
            return None

        # copy version
        old_path = Strategy.path(strategy)
        new_path = Cmd.path(Strategy.dirPath(strategy.name), f"{new_ver}.py")
        Cmd.copy(old_path, new_path)

        # load modul
        modul_path = f"usr.strategy.{strategy.name}.{new_ver}"
        modul = importlib.import_module(modul_path)
        UStrategy = modul.__getattribute__("UStrategy")

        # create
        strategy_copy = UStrategy()
        strategy_copy.__loadConfig()

        # save in db
        await Keeper.add(strategy_copy)

        return strategy_copy

    # }}}
    @classmethod  # renameStrategy  # {{{
    async def renameStrategy(cls, old_name: str, new_name: str) -> str | None:
        logger.debug(f"{cls.__name__}.renameVersion()")

        # check names
        existed_names = cls.requestAll()
        assert old_name in existed_names
        if not cls.checkStrategyName(new_name):
            return None

        # rename dir
        old_dir = Strategy.dirPath(old_name)
        new_dir = Strategy.dirPath(new_name)
        Cmd.rename(old_dir, new_dir)

        # update database
        await Keeper.update(
            cls,
            old_strategy_name=old_name,
            new_strategy_name=new_name,
        )
        return new_name

    # }}}
    @classmethod  # renameVersion  # {{{
    async def renameVersion(
        cls, strategy: Strategy, new_name: str
    ) -> Strategy | None:
        logger.debug(f"{cls.__name__}.renameVersion()")

        # check new name
        if not cls.checkVersionName(strategy, new_name):
            return None

        # rename verion file
        old_path = cls.path(strategy)
        new_path = Cmd.path(Strategy.dirPath(strategy.name), f"{new_name}.py")
        Cmd.rename(old_path, new_path)

        # update database
        await Keeper.update(cls, strategy=strategy, new_version_name=new_name)

        # rename object
        strategy.__version = new_name

        return strategy

    # }}}
    @classmethod  # load  # {{{
    async def load(cls, name: str, version: str) -> UStrategy:
        logger.debug(f"{cls.__name__}.load()")

        # TODO: проверка существования файла
        # ? сделать ли возврат None если нет такого?

        path = f"usr.strategy.{name}.{version}"
        modul = importlib.import_module(path)
        UStrategy = modul.__getattribute__("UStrategy")
        strategy = UStrategy()

        strategy.__loadConfig()

        return strategy

    # }}}
    @classmethod  # deleteStrategy  # {{{
    async def deleteStrategy(cls, strategy_name: str) -> None:
        logger.debug(f"{cls.__name__}.deleteStrategy()")

        # delete dir
        dir_path = Strategy.dirPath(strategy_name)
        Cmd.deleteDir(dir_path)

        # delete in db
        await Keeper.delete(cls, name=strategy_name)

    # }}}
    @classmethod  # deleteVersion  # {{{
    async def deleteVersion(cls, strategy: Strategy) -> None:
        logger.debug(f"{cls.__name__}.deleteVersion()")

        # delete file
        file_path = Strategy.path(strategy)
        Cmd.delete(file_path)

        # delete in db
        await Keeper.delete(cls, name=strategy.name, version=strategy.version)

    # }}}

    @classmethod  # path  # {{{
    def path(cls, strategy: Strategy) -> str:
        logger.debug(f"{cls.__name__}.path()")

        path = Cmd.path(
            Strategy.dirPath(strategy.name),
            f"{strategy.version}.py",
        )
        return path

    # }}}
    @classmethod  # dirPath  # {{{
    def dirPath(cls, strategy_name: str) -> str:
        logger.debug(f"{cls.__name__}.dirPath()")

        path = Cmd.path(Usr.STRATEGY, strategy_name)
        return path

    # }}}
    @classmethod  # cfgPath  # {{{
    def cfgPath(cls, strategy_name: str) -> str:
        logger.debug(f"{cls.__name__}.cfgPath()")

        path = Cmd.path(Usr.STRATEGY, strategy_name, "config.cfg")
        return path

    # }}}
    @classmethod  # versions  # {{{
    def versions(cls, strategy_name: str) -> list[str]:
        logger.debug(f"{cls.__name__}.versions()")

        path = Cmd.path(Usr.STRATEGY, strategy_name)
        files = Cmd.getFiles(path)
        files = Cmd.select(files, extension=".py")

        ver_list = list()
        for file in files:
            ver = file.replace(".py", "")
            ver_list.append(ver)

        return ver_list

    # }}}
    @classmethod  # requestAll # {{{
    def requestAll(cls) -> list[str]:
        logger.debug(f"{cls.__name__}.requestAll()")

        dir_names = Cmd.getDirs(Usr.STRATEGY)
        strategy_names = [i for i in dir_names if not i.startswith(".")]
        return strategy_names

    # }}}
    @classmethod  # checkStrategyName  # {{{
    def checkStrategyName(cls, name) -> bool:
        logger.debug(f"{cls.__name__}.checkStrategyName()")

        existed_names = cls.requestAll()
        return name not in existed_names

    # }}}
    @classmethod  # checkVersionName  # {{{
    def checkVersionName(cls, strategy: Strategy, new_name: str) -> bool:
        logger.debug(f"{cls.__name__}.checkVersionName()")

        existed_versions = cls.versions(strategy.name)
        return new_name not in existed_versions

    # }}}

    def __loadConfig(self):  # {{{
        path = Strategy.cfgPath(self.__name)
        if not Cmd.isExist(path):
            assert False

        self.__cfg = Cmd.loadJson(path)

    # }}}
    async def __connectTradeSignals(self, trade: Trade):  # {{{
        trade.opened.aconnect(self.onTradeOpened)
        trade.closed.aconnect(self.onTradeClosed)

    # }}}
    async def __createStopLossByPercent(  # {{{
        self, trade: Trade, stop_percent: float
    ) -> StopLoss:
        logger.debug("Strategy.__createStopLossByPercent()")

        if trade.type == Trade.Type.LONG:
            direction = Direction.SELL
        else:
            direction = Direction.BUY

        if trade.type == Trade.Type.LONG:
            stop = trade.average() * (1 - stop_percent / 100)
            stop = round_price(stop, trade.instrument.min_price_step)
        else:
            stop = trade.average() * (1 + stop_percent / 100)
            stop = round_price(stop, trade.instrument.min_price_step)

        stop_loss = StopLoss(
            account_name=self.account.name,
            direction=direction,
            instrument=trade.instrument,
            lots=abs(trade.lots()),  # lots may be < 0 if short trade
            quantity=abs(trade.quantity()),
            stop_price=stop,
            exec_price=None,
            status=Order.Status.NEW,
            order_id=Id.newId(),
            trade_id=trade.trade_id,
        )
        # logger.info(f"  {self} create order {stop_loss}")

        await Order.save(stop_loss)
        await trade.attachOrder(stop_loss)
        return stop_loss

    # }}}
    async def __createStopLossByPrice(  # {{{
        self, trade: Trade, stop_price: float
    ) -> StopLoss:
        logger.debug("Strategy.__createStopLossByPrice()")

        if trade.type == Trade.Type.LONG:
            direction = Direction.SELL
        else:
            direction = Direction.BUY

        stop_loss = StopLoss(
            account_name=self.account.name,
            direction=direction,
            instrument=trade.instrument,
            lots=abs(trade.lots()),  # lots may be < 0 if short trade
            quantity=abs(trade.quantity()),
            stop_price=stop_price,
            exec_price=None,
            status=Order.Status.NEW,
            order_id=Id.newId(),
            trade_id=trade.trade_id,
        )
        # logger.info(f"  {self} create order {stop_loss}")

        await Order.save(stop_loss)
        await trade.attachOrder(stop_loss)
        return stop_loss

    # }}}
    async def __createTakeProfitByPercent(  # {{{
        self,
        trade: Trade,
        take_percent: float,
    ) -> TakeProfit:
        logger.debug("Strategy.__createTakeProfitByPercent()")

        if trade.type == Trade.Type.LONG:
            direction = Direction.SELL
        else:
            direction = Direction.BUY

        if trade.type == Trade.Type.LONG:
            take = trade.average() * (1 + take_percent / 100)
            take = round_price(take, trade.instrument.min_price_step)
        else:
            take = trade.average() * (1 - take_percent / 100)
            take = round_price(take, trade.instrument.min_price_step)

        take_profit = TakeProfit(
            account_name=self.account.name,
            direction=direction,
            instrument=trade.instrument,
            lots=abs(trade.lots()),  # lots may be < 0 if short trade
            quantity=abs(trade.quantity()),
            stop_price=take,
            exec_price=take,
            status=Order.Status.NEW,
            order_id=Id.newId(),
            trade_id=trade.trade_id,
        )
        # logger.info(f"  {self} create order {take_profit}")

        await Order.save(take_profit)
        await trade.attachOrder(take_profit)
        return take_profit

    # }}}
    async def __createTakeProfitByPrice(  # {{{
        self,
        trade: Trade,
        take_price: float,
    ) -> TakeProfit:
        logger.debug("Strategy.__createTakeProfitByPrice()")

        if trade.type == Trade.Type.LONG:
            direction = Direction.SELL
        else:
            direction = Direction.BUY

        take_profit = TakeProfit(
            account_name=self.account.name,
            direction=direction,
            instrument=trade.instrument,
            lots=abs(trade.lots()),  # lots may be < 0 if short trade
            quantity=abs(trade.quantity()),
            stop_price=take_price,
            exec_price=take_price,
            status=Order.Status.NEW,
            order_id=Id.newId(),
            trade_id=trade.trade_id,
        )
        # logger.info(f"  {self} create order {take_profit}")

        await Order.save(take_profit)
        await trade.attachOrder(take_profit)
        return take_profit

    # }}}
    async def __cancelActiveOrders(self, trade: Trade):  # {{{
        logger.debug("Strategy.__cancelActiveOrders()")

        # проверить не осталось ли активных ордеров:
        for order in trade.orders:
            if order.isActive():
                await self.cancelOrder(order)

    # }}}


# }}}
class StrategyList:  # {{{
    def __init__(self, name: str):  # {{{
        logger.debug(f"StrategyList.__init__({name})")

        self.__name = name
        self.__strategys: list[Strategy] = list()

    # }}}
    def __iter__(self) -> Iterator:  # {{{
        return iter(self.__strategys)

    # }}}
    def __contains__(self, strategy: Strategy) -> bool:  # {{{
        assert isinstance(strategy, Strategy)

        return strategy in self.__strategys

    # }}}
    def __len__(self) -> int:  # {{{
        return len(self.__strategys)

    # }}}
    @property  # name  # {{{
    def name(self) -> str:
        return self.__name

    @name.setter
    def name(self, name: str):
        assert isinstance(name, str)
        self.__name = name

    # }}}
    @property  # strategys  # {{{
    def strategys(self) -> list[Strategy]:
        return self.__strategys

    @strategys.setter
    def strategys(self, strategys):
        assert isinstance(strategys, list)
        for i in strategys:
            assert isinstance(i, Strategy)
        self.__strategys = strategys

    # }}}
    def add(self, strategy: Strategy) -> None:  # {{{
        logger.debug(
            f"{self.__class__.__name__}.add"
            f"({strategy.name}-{strategy.version})"
        )
        assert isinstance(strategy, Strategy)

        if strategy not in self:
            self.__strategys.append(strategy)
            return

        logger.warning(f"{strategy} already in list '{self.name}'")

    # }}}
    def remove(self, strategy: Strategy) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.remove({strategy})")

        try:
            self.__strategys.remove(strategy)
        except ValueError as err:
            logger.exception(err)

    # }}}
    def clear(self) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.clear()")

        self.__strategys.clear()

    # }}}
    def find(self, name: str, version: str) -> Strategy | None:  # {{{
        logger.debug(f"{self.__class__.__name__}.find({name}, {version})")

        for i in self.__strategys:
            if i.name == name and i.version == version:
                return i

        return None

    # }}}
    def createTimeFrameList(self) -> TimeFrameList:  # {{{
        logger.debug(f"{self.__class__.__name__}.createTimeFrameList()")

        all_timeframe_list = TimeFrameList()
        for i in self:
            all_timeframe_list += i.timeframe_list

        return all_timeframe_list

    # }}}


# }}}


@dataclass  # StrategySetNode  # {{{
class StrategySetNode:
    strategy: str
    version: str
    figi: str
    long: bool
    short: bool

    @classmethod  # fromRecord{{{
    def fromRecord(cls, record: asyncpg.Record) -> StrategySetNode:
        logger.debug(f"{cls.__name__}.fromRecord()")

        node = cls(
            record["strategy"],
            record["version"],
            record["figi"],
            record["long"],
            record["short"],
        )
        return node

    # }}}


# }}}
class StrategySet:  # {{{
    def __init__(self, name: str, items: Optional[list] = None):  # {{{
        logger.debug(f"{self.__class__.__name__}.__init__({name}, {items})")

        self.__name: str = name
        self.__nodes: list[StrategySetNode] = items if items else list()
        self.__asset_list: Optional[AssetList] = None
        self.__strategy_list: Optional[StrategyList] = None

    # }}}
    def __getitem__(self, strategy: Strategy) -> list[StrategySetNode]:  # {{{
        selected = list()
        for i in self.__nodes:
            if i.strategy == strategy.name and i.version == strategy.version:
                selected.append(i)

        return selected

    # }}}
    def __iter__(self) -> Iterator:  # {{{
        return iter(self.__nodes)

    # }}}
    def __len__(self):  # {{{
        return len(self.__nodes)

    # }}}
    @property  # name  # {{{
    def name(self):
        return self.__name

    @name.setter
    def name(self, name: str):
        assert isinstance(name, str)
        self.__name = name

    # }}}
    def add(self, node: StrategySetNode) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.add({node})")
        assert isinstance(node, StrategySetNode)

        self.__nodes.append(node)

    # }}}
    def remove(self, node: StrategySetNode) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.remove({node})")
        assert isinstance(node, StrategySetNode)

        try:
            self.__nodes.remove(node)
        except ValueError as err:
            logger.exception(err)

    # }}}
    def clear(self) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.clear()")
        self.__nodes.clear()

    # }}}
    async def createAssetList(self) -> AssetList:  # {{{
        logger.debug(f"{self.__class__.__name__}.getAssetList()")

        self.__asset_list = AssetList(name="")
        for i in self.__nodes:
            figi = i.figi
            asset = self.__asset_list.find(figi=figi)
            if not asset:
                asset = await Asset.fromFigi(figi)
                self.__asset_list.add(asset)

        return self.__asset_list

    # }}}
    async def createStrategyList(self) -> StrategyList:  # {{{
        logger.debug(f"{self.__class__.__name__}.getStrategyList()")

        # ensure self.__asset_list availible
        if self.__asset_list is None:
            logger.critical(
                "StrategySet can't create StrategyList, "
                "need create common asset list before."
            )
            exit(4)

        # create StrategyList
        self.__strategy_list = StrategyList(name="")
        for node in self.__nodes:
            strategy = self.__strategy_list.find(node.strategy, node.version)
            if not strategy:
                strategy = await Strategy.load(node.strategy, node.version)
                assert strategy is not None
                self.__strategy_list.add(strategy)

        return self.__strategy_list

    # }}}
    @classmethod  # fromRecord{{{
    def fromRecord(cls, name: str, records: asyncpg.Record) -> StrategySet:
        logger.debug(f"{cls.__name__}.fromRecord()")

        s_set = cls(name)
        for i in records:
            node = StrategySetNode.fromRecord(i)
            s_set.add(node)

        return s_set

    # }}}
    @classmethod  # save{{{
    async def save(cls, strategy_set: StrategySet) -> None:
        logger.debug(f"{cls.__name__}.save()")
        assert isinstance(strategy_set, StrategySet)

        await Keeper.delete(strategy_set)
        await Keeper.add(strategy_set)

    # }}}
    @classmethod  # load  # {{{
    async def load(cls, name: str) -> StrategySet | None:
        logger.debug(f"{cls.__name__}.load()")

        s_set = await Keeper.get(cls, name=name)
        return s_set

    # }}}
    @classmethod  # delete  # {{{
    async def delete(cls, strategy_set: StrategySet) -> None:
        logger.debug(f"{cls.__name__}.delete()")
        assert isinstance(strategy_set, StrategySet)
        await Keeper.delete(strategy_set)

    # }}}


# }}}


if __name__ == "__main__":
    ...
