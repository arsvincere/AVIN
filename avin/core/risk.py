#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

from __future__ import annotations

from avin.utils import logger


class Risk:  # {{{
    @classmethod  # maxLotsByRisk  # {{{
    def maxLotsByRisk(
        cls,
        r_trade: float,
        open_price: float,
        stop_price: float,
        lotX: int,
    ) -> int:
        logger.debug(f"{cls.__name__}.maxLotsByRisk()")

        r_share = abs(open_price - stop_price)
        max_shares = int(r_trade / r_share)
        max_lots = int(max_shares / lotX)

        return max_lots

    # }}}
    @classmethod  # maxLotsByDeposit  # {{{
    def maxLotsByDeposit(
        cls,
        deposit: float,
        open_price: float,
        lotX: int,
    ) -> int:
        logger.debug(f"{cls.__name__}.maxLotsByDeposit()")

        max_shares = int(deposit / open_price)
        max_lots = int(max_shares / lotX)

        return max_lots

    # }}}
    @classmethod  # pr  # {{{
    def pr(cls, open_price, stop_price, take_price) -> float:
        logger.debug(f"{cls.__name__}.pr()")

        risk = abs(open_price - stop_price)
        profit = abs(open_price - take_price)
        pr = round(profit / risk, 2)

        return pr

    # }}}


# }}}

# def __processStopTake(self, signal: Signal):
#     R = signal.info["strategy"]["r"]
#     risk = abs(signal.open_price - signal.stop_price)
#     max_shares = int(R / risk)
#     profit = abs(signal.open_price - signal.take_price)
#     pr = round(profit / risk, 2)
#     self.info.setdefault("max shares", max_shares)
#     self.info.setdefault("p/r", pr)
#
# def __setMaxLots(self, signal):
#     max_shares = self.info["max shares"]
#     lotX = signal.asset.lot
#     amount = signal.open_price * max_shares
#     free = 1_000_000
#     self.info.setdefault("free", free)
#     if amount <= free:
#         self.info.setdefault("status", "ALLOW")
#     else:
#         self.info.setdefault("status", "DEPRICATE")
#         max_shares = int(free / signal.open_price)
#         self.info.setdefault("change max shares", max_shares)
#     max_lots = int(max_shares / lotX)
#     self.info.setdefault("max lots", max_lots)
#
# @property  # general
# def general(self):
#     return self.__general
#
# def process(self, signal):
#     self.info = dict()
#     self.__setMaxShares(signal)
#     self.__setMaxLots(signal)
#     signal.info.setdefault("risk", self.info)


if __name__ == "__main__":
    ...
