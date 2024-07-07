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

class GId():# {{{
    # {{{-- doc
    """GId - Globa Identifier for trades, orders, operations, positions.

    Note
    ----
    Don't use class constructor. Create new class object by call member
    newGId()

    Attributes
    ----------
    type: GId.Type
    time: float
        Value returned by call time.time(), current time in seconds since
        the Epoch.

    Subclass
    --------
    Type: enum.Enum
        Enum the type of valid objects
    """ # }}}

    class Type(enum.Enum):# {{{
        """Enum the type of valid objects"""

        UNDEFINE =  0
        TRADE =     1
        ORDER =     2
        OPERATION = 3
        POSITION =  4
    # }}}
    def __init__(self, timestamp: float):# {{{
        self.__val = timestamp
    # }}}
    def __str__(self):# {{{
        return f"{self.__val}"
    # }}}
    def __eq__(self, other: GId):# {{{
        return self.__val == other.__val
    # }}}
    @classmethod  #fromStr# {{{
    def fromStr(cls, string: str) -> GId:
        """Create GId from string

        Valid string looks like '2-1720197988.3066797'
        Consist of two parts, splited by symbol '-'.
        Firts part - type of global identifier (from enum GId.Type)
        Second part - current time in seconds since the Epoch.

        Parameters
        ----------
        object : Order
            Any core object like trade, order, operation, position.
            Any core object like trade, order, operation, position.

        Returns
        -------
        GId
            New global identifier

        """

        gid = GId(float(string))
        return gid
    # }}}
    @classmethod  #newGId# {{{
    def newGId(cls, obj: Trade | Order | Operation | Position) -> GId:
        """Generate new global identifier

        Parameters
        ----------
        obj:
            Any core object like trade, order, operation, position.

        Returns
        -------
        GId
            New global identifier

        """

        gid = GId(timer.time())
        return gid
    # }}}
# }}}

