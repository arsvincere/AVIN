#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

from __future__ import annotations

import enum
from datetime import datetime

from avin.config import Usr
from avin.core.id import Id
from avin.data import InstrumentId
from avin.keeper import Keeper

# TODO: ID = сделай явными их установку а то пиздец потом...
# когда брокер получает операцию по ордеру - присваивается
# это операции каждый раз новое ИД...
# надо еще раз подумать и решить кто где когда будет присваивать
# операциям ИД, точно не брокер.
# не факт что аккаунт.
# возможно вообще стратегия, и стратегия же будет запрашивать операцию
# по своему трейду!!!!!!! Получится так?
# ну смотри ордер filled - этот сигнал же может и стратегия ловить и трейд
# трейд не может запросить свою операцию, он тупой должен быть.
# а вот стратегия вполне...
# может вообще все это гавно от трейда отвязать с подключением ордеров и
# операций, может пусть этим базовый класс стратегии занимается?
# если так получится было бы хорошо.
# Нет, не получится. Ордер привязан к трейду. Если ордер привязать
# к стратегии то придется разбираться к какому трейду это добро приехало.


class Transaction:
    def __init__(
        self,
        dt: datetime,
        price: float,
        quantity: int,
        broker_id: str,
        order_id: str,
    ):
        self.dt = dt
        self.quantity = quantity
        self.price = price
        self.broker_id = broker_id
        self.order_id = order_id

    @classmethod  # save  # {{{
    async def save(cls, transaction: Transaction) -> None:
        await Keeper.add(transaction)

    # }}}
    @classmethod  # load  # {{{
    async def load(cls, order_id: str) -> list[Transaction]:
        transactions = await Keeper.get(cls, order_id=order_id)
        return transactions

    # }}}
    @classmethod  # delete  # {{{
    async def delete(cls, transaction: Transaction) -> None:
        await Keeper.delete(transaction)

    # }}}


class Operation:  # {{{
    class Direction(enum.Enum):  # {{{
        UNDEFINE = 0
        BUY = 1
        SELL = 2

        @classmethod  # fromStr# {{{
        def fromStr(cls, string):
            directions = {
                "UNDEFINE": Operation.Direction.UNDEFINE,
                "BUY": Operation.Direction.BUY,
                "SELL": Operation.Direction.SELL,
            }
            return directions[string]

        # }}}

    # }}}

    def __init__(  # {{{
        self,
        account_name: str,
        dt: datetime,
        direction: Direction,
        asset_id: InstrumentId,
        lots: int,
        quantity: int,
        price: float,
        amount: float,
        commission: float,
        operation_id: Id = None,
        order_id: Id = None,  # XXX: а что если это обязательный аргумент?
        trade_id: Id = None,
        meta: object = None,
    ):
        self.account_name = account_name
        self.dt = dt
        self.direction = direction
        self.asset_id = asset_id
        self.price = price
        self.lots = lots
        self.quantity = quantity
        self.amount = amount
        self.commission = commission
        self.operation_id = operation_id if operation_id else Id.newId(self)
        self.order_id = order_id
        self.trade_id = trade_id
        self.meta = meta

    # }}}
    def __str__(self):  # {{{
        usr_dt = self.dt + Usr.TIME_DIF
        str_dt = usr_dt.strftime("%Y-%m-%d %H:%M")
        string = (
            f"{str_dt} {self.direction.name} {self.asset_id.ticker} "
            f"{self.quantity} * {self.price} = {self.amount} "
            f"+ {self.commission}"
        )
        return string

    # }}}
    async def setParentTrade(self, trade):  # {{{
        # FIX: тиньков при создании операции уже присваивает трейд_ид
        # копирует его из ордера, так что этот метод и еще одно
        # обновление в БД бессмысленны, подумай как бы это все сделать
        # более очевидным и прозрачным...
        # может у тинькова убрать заполнение этого поля?
        # а смысл?
        # а зачем тогда аттачить операцию к трейду?
        # а стоп
        self.trade_id = trade.trade_id
        await Operation.update(self)

    # }}}
    @classmethod  # fromRecord{{{
    async def fromRecord(cls, record):
        ID = await InstrumentId.byFigi(record["figi"])

        op = Operation(
            account_name=record["account"],
            dt=record["dt"],
            direction=Operation.Direction.fromStr(record["direction"]),
            asset_id=ID,
            lots=record["lots"],
            quantity=record["quantity"],
            price=record["price"],
            amount=record["amount"],
            commission=record["commission"],
            operation_id=Id.fromFloat(record["operation_id"]),
            order_id=Id.fromFloat(record["order_id"]),
            trade_id=Id.fromFloat(record["trade_id"]),
            meta=record["meta"],
        )
        return op

    # }}}
    @classmethod  # save{{{
    async def save(cls, operation):
        # XXX: а может тут перезапись в кипере делать?
        # сейчас будет исключение если операция уже добавлена в бд
        await Keeper.add(operation)

    # }}}
    @classmethod  # load{{{
    async def load(cls, operation_id):
        op = await Keeper.get(cls, operation_id=operation_id)
        return op

    # }}}
    @classmethod  # delete{{{
    async def delete(cls, operation):
        await Keeper.delete(operation)

    # }}}
    @classmethod  # update{{{
    async def update(cls, operation):
        await Keeper.update(operation)

    # }}}


# }}}
