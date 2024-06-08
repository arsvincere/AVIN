#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

import enum

class Exchange(enum.Enum):# {{{
    UNDEFINE    = 0
    MOEX        = 1
    SPB         = 2

    @staticmethod  #fromStr# {{{
    def fromStr(string):
        types = {
            "UNDEFINE": Exchange.UNDEFINE,
            "MOEX":     Exchange.MOEX,
            "SPB":      Exchange.SPB,
            }
        return types[string]
    # }}}
# }}}
