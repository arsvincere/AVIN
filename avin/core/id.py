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


class Id:  # {{{
    # {{{-- doc
    """Id - Identifier for trades, orders, operations.

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

    # }}}
    def __init__(self, id_value: str):  # {{{
        self.__val = id_value

    # }}}
    def __str__(self):  # {{{
        return f"{self.__val}"

    # }}}
    def __eq__(self, other: GId):  # {{{
        return self.__val == other.__val

    # }}}
    @classmethod  # newId# {{{
    def newId(cls, obj: Trade | Order | Operation) -> Id:
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

        val = str(timer.time())
        ID = Id(val)
        return ID

    # }}}
    @classmethod  # fromStr# {{{
    def fromFloat(cls, id_value: str) -> Id:
        ID = Id(id_value)
        return ID

    # }}}
    # }}}
