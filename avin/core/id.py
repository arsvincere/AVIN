#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

from __future__ import annotations

import enum
import time as timer

# TODO: Изменить на два поля?
# - type - enum типов (trade, operation, alist, tlist........)
# - str - time().time() но преобразованное в строку.
# - в таблице может хранится как    1-484843.4545
#   а в рантайме уже как два поля


class Id:  # {{{
    # {{{-- doc
    """Id - Identifier for trades, orders, operations, positions.

    Note
    ----
    Don't use class constructor. Create new class object by call member
    newId()

    Attributes
    ----------
    type: Id.Type
    time: float
        Value returned by call time.time(), current time in seconds since
        the Epoch.

    Subclass
    --------
    Type: enum.Enum
        Enum the type of valid objects
    """  # }}}

    class Type(enum.Enum):  # {{{
        """Enum the type of valid objects"""

        UNDEFINE = 0
        TRADE = 1
        ORDER = 2
        OPERATION = 3
        POSITION = 4

    # }}}
    def __init__(self, timestamp: float):  # {{{
        self.__val = timestamp

    # }}}
    def __str__(self):  # {{{
        return f"{self.__val}"

    # }}}
    def __eq__(self, other: GId):  # {{{
        return self.__val == other.__val

    # }}}
    @classmethod  # newId# {{{
    def newId(cls, obj: Trade | Order | Operation | Position) -> Id:
        """Generate new global identifier

        Parameters
        ----------
        obj:
            Any core object like trade, order, operation, position.

        Returns
        -------
        Id:
            New global identifier

        """

        ID = Id(timer.time())
        return ID

    # }}}
    # }}}
