#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

from datetime import UTC, time


class Exchange:  # {{{
    class MOEX:
        name = "MOEX"
        SESSION_BEGIN = time(7, 0, tzinfo=UTC)
        SESSION_END = time(15, 39, tzinfo=UTC)
        EVENING_BEGIN = time(16, 5, tzinfo=UTC)
        EVENING_END = time(20, 49, tzinfo=UTC)

    class SPB:
        name = "SPB"

    class _TEST_EXCHANGE:
        name = "_TEST_EXCHANGE"

    @classmethod  # fromStr {{{
    def fromStr(cls, string):
        types = {
            "MOEX": Exchange.MOEX,
            "SPB": Exchange.SPB,
            "_TEST_EXCHANGE": Exchange._TEST_EXCHANGE,
        }
        return types[string]


# }}}


# }}}
