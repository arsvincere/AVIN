#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

from __future__ import annotations

import abc
import enum

from avin.core.id import Id
from avin.core.operation import Operation
from avin.data import InstrumentId
from avin.keeper import Keeper
from avin.utils import AsyncSignal

# TODO: в жопу это мракобесие с классом неймспейсом
# делай его абстракным и наследуй от него все ордера
# иначе потом в коде невозможно проверять типы
# не на закрытый же класс _BaseOrder ссылаться
# в трейде тогда можно будет обойтись одним методом - сет селф ид
# который сможет клеить свое ИД и ордеру и операции...
# а блять... это сделать по другому.
# и у ордера и у операции должен быть метод - типо setParentTrade...


class Order(metaclass=abc.ABCMeta):  # {{{
    """doc# {{{
    This class is used only as a namespace

    To get syntax like Order.Market, Order.Limit, Order.StopLoss
    I think it looks better than MarketOrder, LimitOrder, StopLossOrder...

    In addition, this simplifies imports, it is enough to import one
    class Order for get access to all order types.
    """

    # }}}
    @abc.abstractmethod  # __init__# {{{
    def __init__(self): ...

    # }}}
    class Type(enum.Enum):  # {{{
        UNDEFINE = 0
        MARKET = 1
        LIMIT = 2
        STOP = 3
        WAIT = 4
        TRAILING = 5
        STOP_LOSS = 6
        TAKE_PROFIT = 7

    # }}}
    class Status(enum.Enum):  # {{{
        UNDEFINE = enum.auto()
        NEW = enum.auto()
        PENDING = enum.auto()
        TIMEOUT = enum.auto()
        TRIGGERED = enum.auto()

        SUBMIT = enum.auto()
        POSTED = enum.auto()
        PARTIAL = enum.auto()
        OFF = enum.auto()
        FILLED = enum.auto()
        EXECUTED = enum.auto()

        CANCELED = enum.auto()
        BLOCKED = enum.auto()
        REJECTED = enum.auto()
        EXPIRED = enum.auto()

        ARCHIVE = enum.auto()

        @classmethod  # fromStr
        def fromStr(cls, string: str) -> Order.Status:
            statuses = {
                "NEW": Order.Status.NEW,
                "PENDING": Order.Status.PENDING,
                "TIMEOUT": Order.Status.TIMEOUT,
                "TRIGGERED": Order.Status.TRIGGERED,
                "SUBMIT": Order.Status.SUBMIT,
                "POSTED": Order.Status.POSTED,
                "PARTIAL": Order.Status.PARTIAL,
                "OFF": Order.Status.OFF,
                "FILLED": Order.Status.FILLED,
                "EXECUTED": Order.Status.EXECUTED,
                "CANCELED": Order.Status.CANCELED,
                "REJECTED": Order.Status.REJECTED,
                "EXPIRED": Order.Status.EXPIRED,
                "ARCHIVE": Order.Status.ARCHIVE,
            }
            return statuses[string]

    # }}}
    class Direction(enum.Enum):  # {{{
        UNDEFINE = 0
        BUY = 1
        SELL = 2

        @classmethod  # fromStr
        def fromStr(cls, string: str) -> Order.Direction:
            directions = {
                "BUY": Order.Direction.BUY,
                "SELL": Order.Direction.SELL,
            }
            return directions[string]

    # }}}

    class _BaseOrder(metaclass=abc.ABCMeta):  # {{{
        @abc.abstractmethod  # __init__# {{{
        def __init__(
            self,
            account_name,
            direction,
            asset_id,
            lots,
            quantity,
            status,
            order_id,
            trade_id,
            exec_lots,
            exec_quantity,
            meta,
            broker_id,
        ):
            self.direction = direction
            self.asset_id = asset_id
            self.lots = lots
            self.quantity = quantity

            self.account_name = account_name
            self.status = status if status else Order.Status.NEW
            self.order_id = order_id if order_id else Id.newId(self)
            self.trade_id = trade_id
            self.exec_lots = exec_lots if exec_lots else 0
            self.exec_quantity = exec_quantity if exec_quantity else 0

            self.meta = meta
            self.broker_id = broker_id

            # Signals
            self.posted = AsyncSignal(Order._BaseOrder)
            self.filled = AsyncSignal(Order._BaseOrder)
            self.reqected = AsyncSignal(Order._BaseOrder)
            self.canceled = AsyncSignal(Order._BaseOrder)
            self.executed = AsyncSignal(Order._BaseOrder, Operation)
            # XXX: а нахуй вообще нужна эта проверка типов у сигналов?
            # как то это не по питонячи, даешь свободное число аргументов
            # и свободные типы?

            self.statusChanged = AsyncSignal(Order._BaseOrder)

        # }}}
        def __str__(self):  # {{{
            string = (
                f"Order.{self.type.name} "
                f"{self.direction.name} "
                f"{self.asset_id.ticker} "
                f"{self.lots} lot"
            )

            if self.type == Order.Type.MARKET:
                pass
            elif self.type == Order.Type.LIMIT:
                string += f", {self.quantity}x{self.price}"
            elif self.type == Order.Type.STOP:
                string += f", stop={self.stop_price}, exec={self.exec_price}"

            return string

        # }}}
        async def setStatus(self, status: Order.Status):  # {{{
            self.status = status
            await Order.update(self)

            # emitting special signal for this status
            if status == Order.Status.POSTED:
                await self.posted.async_emit(self)
            if status == Order.Status.FILLED:
                await self.filled.async_emit(self)
            if status == Order.Status.REJECTED:
                await self.reqected.async_emit(self)
            if status == Order.Status.CANCELED:
                await self.canceled.async_emit(self)

            # emiting common signal
            await self.statusChanged.async_emit(self)

        # }}}
        async def setParentTrade(self, trade):  # {{{
            self.trade_id = trade.trade_id
            await Order.update(self)

        # }}}
        async def setMeta(self, broker_response: str):  # {{{
            self.meta = broker_response
            await Order.update(self)

        # }}}

    # }}}
    class Market(_BaseOrder):  # {{{
        def __init__(
            self,
            account_name: str,
            direction: Order.Direction,
            asset_id: InstrumentId,
            lots: int,
            quantity: int,
            status: Order.Status = None,
            order_id: Id = None,
            trade_id: Id = None,
            exec_lots: int = None,
            exec_quantity: int = None,
            meta=None,
            broker_id=None,
        ):
            super().__init__(
                account_name,
                direction,
                asset_id,
                lots,
                quantity,
                status,
                order_id,
                trade_id,
                exec_lots,
                exec_quantity,
                meta=meta,
                broker_id=broker_id,
            )
            self.type = Order.Type.MARKET

    # }}}
    class Limit(_BaseOrder):  # {{{
        def __init__(
            self,
            account_name: str,
            direction: Order.Direction,
            asset_id: InstrumentId,
            lots: int,
            quantity: int,
            price: float,
            status: Order.Status = None,
            order_id: Id = None,
            trade_id: Id = None,
            exec_lots: int = None,
            exec_quantity: int = None,
            meta=None,
            broker_id=None,
        ):
            super().__init__(
                account_name,
                direction,
                asset_id,
                lots,
                quantity,
                status,
                order_id,
                trade_id,
                exec_lots,
                exec_quantity,
                meta=meta,
                broker_id=broker_id,
            )
            self.type = Order.Type.LIMIT
            self.price = price

    # }}}
    class Stop(_BaseOrder):  # {{{
        def __init__(
            self,
            account_name: str,
            direction: Order.Direction,
            asset_id: InstrumentId,
            lots: int,
            quantity: int,
            stop_price: float,
            exec_price: float,
            status: Order.Status = None,
            order_id: Id = None,
            trade_id: Id = None,
            exec_lots: int = None,
            exec_quantity: int = None,
            meta=None,
            broker_id=None,
        ):
            super().__init__(
                account_name,
                direction,
                asset_id,
                lots,
                quantity,
                status,
                order_id,
                trade_id,
                exec_lots,
                exec_quantity,
                meta=meta,
                broker_id=broker_id,
            )
            self.type = Order.Type.STOP
            self.stop_price = stop_price
            self.exec_price = exec_price

    # }}}
    class StopLoss(_BaseOrder):  # {{{
        def __init__(
            self,
            position: Position,  # ??? XXX: подумай еще раз
            stop_price: float,
            exec_price: float,
            trade_id: Id = None,
            status: Order.Status = None,
        ):
            assert False

    # }}}
    class TakeProfit(_BaseOrder):  # {{{
        def __init__(
            self,
            position: Position,  # ??? XXX: подумай еще раз
            stop_price: float,
            exec_price: float,
            trade_id: Id = None,
            status: Order.Status = None,
        ):
            assert False

    # }}}
    class Wait(_BaseOrder):  # {{{
        ...

    # }}}
    class Trailing(_BaseOrder):  # {{{
        ...

    # }}}

    @classmethod  # save  # {{{
    async def save(cls, order) -> None:
        await Keeper.add(order)

    # }}}
    @classmethod  # load  # {{{
    async def load(cls, order_id: Id):
        order_list = await Keeper.get(cls, order_id=order_id)
        assert len(order_list) == 1
        order = order_list[0]
        return order

    # }}}
    @classmethod  # delete  # {{{
    async def delete(cls, order) -> None:
        await Keeper.delete(order)

    # }}}
    @classmethod  # update  # {{{
    async def update(cls, order) -> None:
        await Keeper.update(order)

    # }}}
    @classmethod  # fromRecord{{{
    async def fromRecord(cls, record):
        methods = {
            "MARKET": Order.__marketOrderFromRecord,
            "LIMIT": Order.__limitOrderFromRecord,
            "STOP": Order.__stopOrderFromRecord,
        }
        method = methods[record["type"]]
        order = await method(record)
        return order

    # }}}
    @classmethod  # __marketOrderFromRecord{{{
    async def __marketOrderFromRecord(cls, record):
        ID = await InstrumentId.byFigi(figi=record["figi"])
        order = Order.Market(
            account_name=record["account"],
            direction=Order.Direction.fromStr(record["direction"]),
            asset_id=ID,
            lots=record["lots"],
            quantity=record["quantity"],
            status=Order.Status.fromStr(record["status"]),
            order_id=record["order_id"],
            trade_id=record["trade_id"],
            exec_lots=record["exec_lots"],
            exec_quantity=record["exec_quantity"],
            meta=record["meta"],
            broker_id=record["broker_id"],
        )
        return order

    # }}}
    @classmethod  # __limitOrderFromRecord{{{
    async def __limitOrderFromRecord(cls, record):
        ID = await InstrumentId.byFigi(figi=record["figi"])
        order = Order.Limit(
            account_name=record["account"],
            direction=Order.Direction.fromStr(record["direction"]),
            asset_id=ID,
            lots=record["lots"],
            quantity=record["quantity"],
            price=record["price"],
            status=Order.Status.fromStr(record["status"]),
            order_id=record["order_id"],
            trade_id=record["trade_id"],
            exec_lots=record["exec_lots"],
            exec_quantity=record["exec_quantity"],
            meta=record["meta"],
            broker_id=record["broker_id"],
        )
        return order

    # }}}
    @classmethod  # __stopOrderFromRecord{{{
    async def __stopOrderFromRecord(cls, record):
        ID = await InstrumentId.byFigi(figi=record["figi"])
        order = Order.Stop(
            account_name=record["account"],
            direction=Order.Direction.fromStr(record["direction"]),
            asset_id=ID,
            lots=record["lots"],
            quantity=record["quantity"],
            stop_price=record["stop_price"],
            exec_price=record["exec_price"],
            status=Order.Status.fromStr(record["status"]),
            order_id=record["order_id"],
            trade_id=record["trade_id"],
            exec_lots=record["exec_lots"],
            exec_quantity=record["exec_quantity"],
            meta=record["meta"],
            broker_id=record["broker_id"],
        )
        return order


# }}}

# }}}
