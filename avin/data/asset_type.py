#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

import enum

class AssetType(enum.Enum):# {{{
    # TODO rename in upper case
    UNDEFINE    = 0
    Index       = 1
    Share       = 2
    Bond        = 3
    Future      = 4
    Option      = 5
    Currency    = 6
    Etf         = 7

    @classmethod  #fromStr# {{{
    def fromStr(cls, string):
        types = {
            "UNDEFINE": AssetType.UNDEFINE,
            "Index":    AssetType.Index,
            "Share":    AssetType.Share,
            "Bond":     AssetType.Bond,
            "Future":   AssetType.Future,
            "Currency": AssetType.Currency,
            "Etf":      AssetType.Etf,
            }
        return types[string]
    # }}}
# }}}
