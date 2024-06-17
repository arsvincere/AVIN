#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

import abc
import enum

class Uid(metaclass=abc.ABCMeta):
    class Type(enum.Enum):
        UNDEFINE =      1
        SIGNAL =        1
        ORDER =         2
        OPERATIONT =    3
        POSITION =      4

    @classmethod  #newUid# {{{
    def newUid(cls, obj: Signal | Order | Operation | Position):
        assert False
        # ???? подумать
        uid = f"{obj.__class__.__name__}-{date(today())}-{counter}???"

    # }}}
