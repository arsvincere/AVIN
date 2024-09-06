#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

"""doc"""

from __future__ import annotations

import enum

# TODO: Event - abc.class, -> NewBarEvent, OrderExecEvent,


class Event:  # {{{
    class Type(enum.Enum):  # {{{
        UNDEFINE = 0
        NEW_BAR = 1
        ORDER = 2
        OPERATION = 3
        LAST_PRICE = 4
        INFO = 5
        PING = 6
        UPDATED_ASSET = 7

    # }}}
    class NewBar:  # {{{
        def __init__(self, figi, timeframe, bar):
            self.figi = figi
            self.timeframe = timeframe
            self.bar = bar
            self.type = Event.Type.NEW_BAR

        def __str__(self):
            s = f"{self.type.name} {self.figi}, {self.timeframe}, {self.bar}"
            return s

    # }}}
    class Order:  # {{{
        ...

    # }}}
    class Operation:  # {{{
        ...

    # }}}
    class Transaction:  # {{{
        def __init__(self, account_name, figi, direction, order_id):
            self.figi = figi
            self.timeframe = timeframe
            self.bar = bar
            self.type = Event.Type.NEW_BAR

        def __str__(self):
            s = f"{self.type.name} {self.figi}, {self.timeframe}, {self.bar}"
            return s

        ...
        """
        order_id
        direction
        figi
        list[trades]: (dt, price, quantity, id)
        account_id
        """

    # }}}
    class LastPrice:  # {{{
        ...

    # }}}
    class Info:  # {{{
        ...

    # }}}
    class Ping:  # {{{
        ...

    # }}}


# }}}


class BarEvent(Event): ...


class TransactionEvent(Event): ...
