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
from avin.core.gid import GId

class Operation():# {{{
    class Direction(enum.Enum):# {{{
        UNDEFINE =     0
        BUY =          1
        SELL =         2

        @classmethod  #fromStr# {{{
        def fromStr(cls, string):
            directions = {
                "UNDEFINE": Operation.Direction.UNDEFINE,
                "BUY":      Operation.Direction.BUY,
                "SELL":     Operation.Direction.SELL,
                }
            return directions[string]
        # }}}
    # }}}

    def __init__(# {{{
        self,
        account:    account,
        dt:         datetime,
        direction:  Direction,
        asset:      Asset,
        lots:       int,
        quantity:   int,
        price:      float,
        amount:     float,
        commission: float,
        trade_ID:   GId=None,
        meta:       object=None,
        ):

        self.dt = dt
        self.direction = direction
        self.asset = asset
        self.price = price
        self.lots = lots
        self.quantity = quantity
        self.amount = amount
        self.commission = commission
        self.trade_ID = trade_ID
        self.meta = meta
    # }}}
    def __str__(self):# {{{
        usr_dt = self.dt + Usr.TIME_DIF
        str_dt = usr_dt.strftime("%Y-%m-%d %H:%M")
        string = (
            f"{str_dt} {self.direction.name} {self.asset.ticker} "
            f"{self.quantity} * {self.price} = {self.amount} "
            f"+ {self.commission}"
            )
        return string
    # }}}
    @classmethod  # toJson{{{
    def toJson(cls, op: Operation) -> dict:
        obj = {
            "dt":         str(op.dt),
            "direction":  op.direction.name,
            "asset":      Asset.toJson(op.asset),
            "lots":       op.lots,
            "quantity":   op.quantity,
            "price":      op.price,
            "amount":     op.amount,
            "commission": op.commission,
            }
        return obj
    # }}}
    @classmethod  # fromJson{{{
    def fromJson(cls, obj):
        o = Operation(
            dt=         datetime.fromisoformat(obj["dt"]),
            direction=  Operation.Direction.fromStr(obj["direction"]),
            asset=      Asset.fromJson(obj["asset"]),
            lots=       obj["lots"],
            quantity=   obj["quantity"],
            price=      obj["price"],
            amount=     obj["amount"],
            commission= obj["commission"],
            )
        return o
    # }}}
# }}}

