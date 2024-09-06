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

# TODO: Event - abc.class, -> NewBarEvent, OrderExecEvent,


class Event:  # {{{
    class Type(enum.Enum):
        UNDEFINE = 0
        NEW_BAR = 1
        TRANSACTION = 2
        OPERATION = 3
        POSITION = 4

    @abc.abstractmethod
    def __init__(self): ...


# }}}


class NewBarEvent(Event):  # {{{
    def __init__(self, figi, timeframe, bar):
        self.figi = figi
        self.timeframe = timeframe
        self.bar = bar
        self.type = Event.Type.NEW_BAR

    def __str__(self):
        s = f"{self.type.name} {self.figi}, {self.timeframe}, {self.bar}"
        return s


# }}}
class TransactionEvent(Event):  # {{{
    def __init__(self, order: Order, transactions: list[Transaction]):
        self.order = order
        self.transactions = transactions
        self.type = Event.Type.TRANSACTION

        """ Tinkoff TradeStream
        order_id
        direction
        figi
        list[trades]: (dt, price, quantity, id)
        account_id
        """

    def __str__(self): ...

    ...


# }}}
