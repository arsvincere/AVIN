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
from typing import Optional

from avin.core.id import Id
from avin.core.operation import Operation
from avin.core.transaction import Transaction
from avin.data import InstrumentId
from avin.keeper import Keeper
from avin.utils import AsyncSignal

# TODO: а может сюда транзакции подключить.


class Order(metaclass=abc.ABCMeta):  # {{{
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

    @abc.abstractmethod  # __init__# {{{
    def __init__(
        self,
        order_type,
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
        transactions,
    ):
        self.type = order_type
        self.account_name = account_name
        self.direction = direction
        self.asset_id = asset_id
        self.lots = lots
        self.quantity = quantity
        self.status = status

        self.order_id = order_id
        self.trade_id = trade_id
        self.exec_lots = exec_lots
        self.exec_quantity = exec_quantity

        self.meta = meta
        self.broker_id = broker_id
        self.transactions = transactions if transactions else list()

        # Signals
        self.statusChanged = AsyncSignal(Order)
        self.posted = AsyncSignal(Order)
        self.partial = AsyncSignal(Order)
        self.filled = AsyncSignal(Order)
        self.executed = AsyncSignal(Order, Operation)
        self.rejected = AsyncSignal(Order)
        self.canceled = AsyncSignal(Order)

    # }}}
    def __str__(self):  # {{{
        string = (
            f"{self.type.name} "
            f"status={self.status.name} "
            f"acc={self.account_name} "
            f"{self.direction.name} "
            f"{self.asset_id.ticker} "
            f"{self.exec_lots}/{self.lots} lot"
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
            await self.rejected.async_emit(self)
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
    async def attachTransaction(self, transaction: Transaction):  # {{{
        assert transaction.order_id == self.order_id
        self.transactions.append(transaction)

        # TODO: пересчитать на основе транзакций количество
        # выполненных лотов? или у брокера это все таки
        # из ордер стэйта просто получать?
        assert False

        await super().update(self)

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
        order = MarketOrder(
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
        order = LimitOrder(
            account_name=record["account"],
            direction=Order.Direction.fromStr(record["direction"]),
            asset_id=ID,
            lots=record["lots"],
            quantity=record["quantity"],
            price=record["price"],
            status=Order.Status.fromStr(record["status"]),
            order_id=Id.fromStr(record["order_id"]),
            trade_id=Id.fromStr(record["trade_id"]),
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
        order = StopOrder(
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


class MarketOrder(Order):  # {{{
    def __init__(
        self,
        account_name: str,
        direction: Order.Direction,
        asset_id: InstrumentId,
        lots: int,
        quantity: int,
        status: Order.Status = Order.Status.NEW,
        order_id: Optional[Id] = None,
        trade_id: Optional[Id] = None,
        exec_lots: int = 0,
        exec_quantity: int = 0,
        meta: str = "",
        broker_id: str = "",
        transactions=Optional[list],
    ):
        super().__init__(
            Order.Type.MARKET,
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
            transactions=transactions,
        )


# }}}
class LimitOrder(Order):  # {{{
    def __init__(
        self,
        account_name: str,
        direction: Order.Direction,
        asset_id: InstrumentId,
        lots: int,
        quantity: int,
        price: float,
        status: Order.Status = Order.Status.NEW,
        order_id: Optional[Id] = None,
        trade_id: Optional[Id] = None,
        exec_lots: int = 0,
        exec_quantity: int = 0,
        meta: str = "",
        broker_id: str = "",
        transactions=Optional[list],
    ):
        super().__init__(
            Order.Type.LIMIT,
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
            transactions=transactions,
        )
        self.price = price


# }}}
class StopOrder(Order):  # {{{
    def __init__(
        self,
        account_name: str,
        direction: Order.Direction,
        asset_id: InstrumentId,
        lots: int,
        quantity: int,
        stop_price: float,
        exec_price: float,
        status: Order.Status = Order.Status.NEW,
        order_id: Optional[Id] = None,
        trade_id: Optional[Id] = None,
        exec_lots: int = 0,
        exec_quantity: int = 0,
        meta: str = "",
        broker_id: str = "",
        transactions=Optional[list],
    ):
        super().__init__(
            Order.Type.STOP,
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
            transactions=transactions,
        )
        self.stop_price = stop_price
        self.exec_price = exec_price


# }}}
class WaitOrder(Order):  # {{{
    ...


# }}}
class TrailingOrder(Order):  # {{{
    ...


# }}}


# class StopLoss(Order):  # {{{
#     def __init__(
#         self,
#         position: Position,  # ??? XXX: подумай еще раз
#         stop_price: float,
#         exec_price: float,
#         trade_id: Id = None,
#         status: Order.Status = None,
#     ):
#         assert False
#
#
# # }}}
# class TakeProfit(Order):  # {{{
#     def __init__(
#         self,
#         position: Position,  # ??? XXX: подумай еще раз
#         stop_price: float,
#         exec_price: float,
#         trade_id: Id = None,
#         status: Order.Status = None,
#     ):
#         assert False
#
#
# # }}}
