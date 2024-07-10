#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

import enum

class AssetType(enum.Enum):# {{{
    CASH        = 0
    INDEX       = 1
    SHARE       = 2
    BOND        = 3
    FUTURE      = 4
    OPTION      = 5
    CURRENCY    = 6
    ETF         = 7


    @classmethod  #fromStr# {{{
    def fromStr(cls, string):
        types = {
            "CASH":     AssetType.CASH,
            "INDEX":    AssetType.INDEX,
            "SHARE":    AssetType.SHARE,
            "BOND":     AssetType.BOND,
            "FUTURE":   AssetType.FUTURE,
            "CURRENCY": AssetType.CURRENCY,
            "ETF":      AssetType.ETF,
            }
        return types[string]
    # }}}
# }}}
