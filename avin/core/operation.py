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

from avin.const import Usr
from avin.core.asset import Asset
from avin.core.id import Id
from avin.data import InstrumentId


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
        order_id: Id = None,
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
    @classmethod  # toJson{{{
    def toJson(cls, op: Operation) -> dict:
        obj = {
            "account": op.account_name,
            "dt": str(op.dt),
            "direction": op.direction.name,
            "asset": Asset.toJson(op.asset),
            "lots": op.lots,
            "quantity": op.quantity,
            "price": op.price,
            "amount": op.amount,
            "commission": op.commission,
        }
        return obj

    # }}}
    @classmethod  # fromJson{{{
    def fromJson(cls, obj):
        o = Operation(
            account_name=obj["account"],
            dt=datetime.fromisoformat(obj["dt"]),
            direction=Operation.Direction.fromStr(obj["direction"]),
            asset=Asset.fromJson(obj["asset"]),
            lots=obj["lots"],
            quantity=obj["quantity"],
            price=obj["price"],
            amount=obj["amount"],
            commission=obj["commission"],
        )
        return o

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
            operation_id=record["operation_id"],
            order_id=record["order_id"],
            trade_id=record["trade_id"],
            meta=record["meta"],
        )
        return op

    # }}}


# }}}
