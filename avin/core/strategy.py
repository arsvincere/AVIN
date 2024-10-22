#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

"""Doc"""

from __future__ import annotations

import importlib
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Iterator, Optional

from avin.config import Usr
from avin.core.account import Account
from avin.core.asset import Asset, AssetList
from avin.core.id import Id
from avin.core.order import MarketOrder, Order, StopLoss, TakeProfit
from avin.core.trade import Trade, TradeList
from avin.keeper import Keeper
from avin.utils import AsyncSignal, Cmd, logger, round_price

# TODO: load active TradeList
# это должна делать все таки сама стратегия, но не автоматом
# при создании, а просто метод в интерфейсе
# и когда надо - трейдер его вызывает
# а когда не надо - в тестере его и не трогают
# метод обращается к Киперу и делает селект трейдов по статусу
# ...
# однако при этом еще надо знать к какому трейдеру мы сейчас
# относимся...
# может все таки трейдер будет грузить общий трейд лист
# а дальше из него селект по стратегиям делать и крепить их к
# к стратегиям?


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

    # }}}
    @property  # @abstractmethod timeframe_list  # {{{
    @abstractmethod
    def timeframe_list() -> list[TimeFrame]:
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
        logger.info(f"Trade opened: '{trade}'")
        logger.info(f"Trade open dt: '{trade.openDatetime()}'")

    # }}}
    @abstractmethod  # onTradeClosed  # {{{
    async def onTradeClosed(self, trade: Trade):
        logger.info(f"Trade closed: '{trade}'")
        logger.info(f"Trade closed result: {trade.result()}")

    # }}}

    def __str__(self):  # {{{
        return f"{self.name}-{self.version}"

    # }}}
    def __eq__(self, other: Strategy):  # {{{
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
    @property  # timeframe_list  # {{{
    def timeframe_list(self):
        # TODO: здесь нужно преобразование в таймфреймы делать
        # а не в трейдере. Манипулировать данными - Чем ближе к источнику
        # тем лучше.
        return self.__cfg["timeframe_list"]

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

    def setAccount(self, account: Account) -> None:  # {{{
        logger.info(f":: {self} set account={account.name}")
        self.__account = account

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

    @classmethod  # load# {{{
    async def load(cls, name: str, version: str) -> UStrategy:
        path = f"usr.strategy.{name}.{version}"
        modul = importlib.import_module(path)
        UStrategy = modul.__getattribute__("UStrategy")
        strategy = UStrategy()

        await strategy.__loadConfig()

        return strategy

    # }}}
    @classmethod  # versions# {{{
    def versions(cls, strategy_name: str) -> list[str]:
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
        if not Cmd.isExist(path):
            assert False

        self.__cfg = Cmd.loadJson(path)

    # }}}
    async def __connectTradeSignals(self, trade: Trade):  # {{{
        await trade.opened.async_connect(self.onTradeOpened)
        await trade.closed.async_connect(self.onTradeClosed)

    # }}}


# }}}
class StrategyList:  # {{{
    def __init__(self, name: str):  # {{{
        logger.debug(f"StrategyList.__init__({name})")

        self.__name = name
        self.__strategys = list()

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

        logger.warning(f"{asset} already in list '{self.name}'")

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


# }}}
@dataclass  # StrategySetItem{{{
class StrategySetItem:
    strategy: str
    version: str
    figi: str
    long: bool
    short: bool


# }}}
class StrategySet:  # {{{
    def __init__(self, name: str, items: Optional[list] = None):  # {{{
        logger.debug(f"{self.__class__.__name__}.__init__({name}, {items})")

        self.__name: str = name
        self.__items: list[StrategySetItem] = items if items else list()
        self.__asset_list = None
        self.__strategy_list = None

    # }}}
    def __len__(self):  # {{{
        return len(self.__items)

    # }}}
    @property  # name{{{
    def name(self):
        return self.__name

    # }}}
    def add(self, item: StrategySetItem) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.add({item})")
        assert isinstance(item, StrategySetItem)

        self.__items.append(item)

    # }}}
    def remove(self, item: StrategySetItem) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.remove({item})")
        assert isinstance(item, StrategySetItem)

        try:
            self.__items.remove(item)
        except ValueError as err:
            logger.exception(err)

    # }}}
    def clear(self) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.clear()")
        self.__items.clear()

    # }}}
    async def createCommonAssetList(self) -> AssetList:  # {{{
        logger.debug(f"{self.__class__.__name__}.getCommonAssetList()")

        # create set of figi without dublicate
        figis = set()
        for i in self.__items:
            figis.add(i.figi)

        # create AssetList
        self.__asset_list = AssetList(name="")
        for figi in figis:
            asset = await Asset.byFigi(figi)
            asset_list.add(asset)

        return self.__asset_list

    # }}}
    async def createActiveStrategyList(self) -> StrategyList:  # {{{
        logger.debug(f"{self.__class__.__name__}.getActiveStrategyList()")

        # ensure self.__asset_list availible
        if not self.__asset_list:
            logger.critical(
                "StrategySet can't create StrategyList, "
                "need create common asset list before."
            )
            exit(4)

        # create StrategyList
        self.strategy_list = StrategyList(name="")
        for item in self.__items:
            strategy = strategy_list.find(item.name, item.version)
            if not strategy:
                strategy = await Strategy.load(item.name, item.version)
                strategy_list.add(strategy)

        return self.strategy_list

    # }}}
    @classmethod  # fromRecord{{{
    def fromRecord(cls, record):
        logger.debug(f"{cls.__name__}.fromRecord()")

        assert False

    # }}}
    @classmethod  # save{{{
    async def save(cls, strategy_set: StrategySet):
        logger.debug(f"{cls.__name__}.save()")
        assert isinstance(strategy_set, StrategySet)
        await Keeper.add(strategy_set)

    # }}}
    @classmethod  # load  # {{{
    async def load(cls, name: str) -> StrategySet | None:
        logger.debug(f"{cls.__name__}.load()")

        response = await Keeper.get(cls, name=name)
        if len(response) == 1:  # response == [ StrategySet, ]
            return response[0]

        # else: error, asset list not found
        logger.error(f"Strategy set '{name}' not found!")
        return None

    # }}}
    @classmethod  # delete  # {{{
    async def delete(cls, strategy_set: StrategySet) -> None:
        logger.debug(f"{cls.__name__}.delete()")
        assert isinstance(strategy_set, StrategySet)
        await Keeper.delete(strategy_set)

    # }}}


# }}}
