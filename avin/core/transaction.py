#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

from __future__ import annotations

from datetime import datetime

from avin.keeper import Keeper


class Transaction:
    def __init__(  # {{{
        self,
        order_id: str,
        dt: datetime,
        price: float,
        quantity: int,
        broker_id: str,
    ):
        self.order_id = order_id
        self.dt = dt
        self.quantity = quantity
        self.price = price
        self.broker_id = broker_id

    # }}}
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
