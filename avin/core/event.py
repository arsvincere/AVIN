#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

"""doc"""

from __future__ import annotations

import abc
import enum

from avin.core.bar import Bar
from avin.core.order import Order
from avin.core.timeframe import TimeFrame
from avin.core.transaction import Transaction


class Event(metaclass=abc.ABCMeta):  # {{{
    class Type(enum.Enum):  # {{{
        UNDEFINE = 0
        NEW_BAR = 1
        TRANSACTION = 2
        OPERATION = 3
        POSITION = 4

    # }}}
    @abc.abstractmethod
    def __init__(self): ...


# }}}
class NewBarEvent(Event):  # {{{
    def __init__(self, figi: str, timeframe: TimeFrame, bar: Bar):  # {{{
        self.figi = figi
        self.timeframe = timeframe
        self.bar = bar
        self.type = Event.Type.NEW_BAR

    # }}}
    def __str__(self):  # {{{
        s = f"{self.type.name} {self.figi}, {self.timeframe}, {self.bar}"
        return s


# }}}


# }}}
class TransactionEvent(Event):  # {{{
    def __init__(  # {{{
        self,
        account: Account,
        figi: str,
        direction: Order.Direction,
        order_broker_id: str,
        transactions: list[Transaction],
    ):
        self.account = account
        self.figi = figi
        self.direction = direction
        self.order_broker_id = order_broker_id
        self.transactions = transactions
        self.type = Event.Type.TRANSACTION

    # }}}
    def __str__(self):  # {{{
        count = len(self.transactions)
        string = (
            f"{self.type.name} {self.account.name} {self.direction.name} "
            f"figi={self.figi} order_broker_id={self.order_broker_id} "
            f"{count} transactions"
        )
        return string

    # }}}


# }}}
