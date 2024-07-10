#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

from avin.core.asset import Asset, Share
from avin.core.cash import Cash
from avin.core.position import Position
from avin.data.asset_type import AssetType

class Portfolio():# {{{
    def __init__(# {{{
        self,
        cash: list[Cash]=list(),
        positions: list[Position]=list()
        ):

        self.__cash = cash
        self.__positions = {
                AssetType.SHARE: list(),
                AssetType.BOND: list(),
                AssetType.FUTURE: list(),
                AssetType.CURRENCY: list(),
                AssetType.OPTION: list(),
                AssetType.ETF: list(),
            }
        for pos in positions:
            asset_type = pos.asset.type
            self.__positions[asset_type].append(pos)
    # }}}
    def add(self, pos: Position) -> None:# {{{
        asset_type = pos.asset.type
        self.__positions[pos.asset.type].append(pos)
    # }}}
    def remove(self, pos: Position) -> None:# {{{
        asset_type = pos.asset.type
        assert pos.status == Position.Status.CLOSE
        self.__positions[asset_type].remove(pos)
    # }}}
    def get(self, asset_type: AssetType) -> list[Position]:# {{{
        assert asset_type in self.__positions
        return self.__positions[asset_type]
    # }}}
    def getAll(self) -> dict:# {{{
        return self.__positions
    # }}}
    def cash(self, t: Cash.Type) -> Cash:# {{{
        assert t == Cash.Type.RUB
        assert len(self.__cash) == 1  # So far, it works only with rubles
        rub_cash = self.__cash[0]
        return rub_cash
    # }}}
    def inputCash(self, cash: Cash) -> None:# {{{
        assert cash.type == Cash.Type.RUB
        for i in self.__cash:
            if i.type == Cash.Type.RUB:
                i.value = i.value + cur.value
                return

        # There is no this cash_type in the portfolio, add it
        self.__cash.append(cash)
        return
    # }}}
    def outputCash(self, cash: Cash) -> None:# {{{
        assert cash.type == Cash.Type.RUB
        for i in self.__cash:
            if i.type == Cash.Type.RUB:
                assert i.value - cash.value
                i.value = i.value - cash.value
                return

        assert False, f"There is no this {cash.type} in the portfolio"
    # }}}
# }}}

