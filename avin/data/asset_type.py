#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

import enum


class AssetType(enum.Enum):  # {{{
    UNDEFINE = 0
    CASH = 1
    INDEX = 2
    SHARE = 3
    BOND = 4
    FUTURE = 5
    OPTION = 6
    CURRENCY = 7
    ETF = 8

    @classmethod  # fromStr# {{{
    def fromStr(cls, string):
        types = {
            "CASH": AssetType.CASH,
            "INDEX": AssetType.INDEX,
            "SHARE": AssetType.SHARE,
            "BOND": AssetType.BOND,
            "FUTURE": AssetType.FUTURE,
            "CURRENCY": AssetType.CURRENCY,
            "ETF": AssetType.ETF,
        }
        return types[string]

    # }}}


# }}}
