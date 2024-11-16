#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

from avin.core import Asset, Strategy, TimeFrame, TimeFrameList, Trade
from avin.utils import Cmd


class UStrategy(Strategy):
    def __init__(self):
        name = Cmd.dirName(__file__)
        version = Cmd.name(__file__)
        Strategy.__init__(self, name, version)

    @property  # timeframe_list{{{
    def timeframe_list(self):
        tflist = TimeFrameList(
            [
                TimeFrame("1M"),
            ]
        )
        return tflist

    # }}}
    async def start(self):  # {{{
        await super().start()

    # }}}
    async def finish(self):  # {{{
        await super().finish()

    # }}}
    async def connect(self, asset: Asset, long: bool, short: bool):  # {{{
        await super().connect(asset, long, short)

    # }}}
    async def onTradeOpened(self, trade: Trade):  # {{{
        await super().onTradeOpened(trade)

    # }}}
    async def onTradeClosed(self, trade: Trade):  # {{{
        await super().onTradeClosed(trade)

    # }}}
