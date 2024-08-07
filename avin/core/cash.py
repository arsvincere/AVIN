#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

from __future__ import annotations

import abc
import enum
from datetime import datetime

from avin.const import Usr
from avin.core.chart import Chart
from avin.core.timeframe import TimeFrame
from avin.data import AssetType, Data, Exchange, InstrumentId
from avin.logger import logger
from avin.utils import Cmd, now


class Cash:  # {{{
    class Type(enum.Enum):  # {{{
        UNDEFINE = 0
        RUB = 1

    # }}}
    def __init__(self, cash_type: Cash.Type, value: float):  # {{{
        self.__type = cash_type
        self.__value = value

    # }}}
    @property  # type#{{{
    def type(self) -> Cash.Type:
        return self.__type

    # }}}
    @property  # value#{{{
    def value(self) -> float:
        return self.__value

    @value.setter
    def value(self, value: float):
        self.__value = value

    # }}}


# }}}
