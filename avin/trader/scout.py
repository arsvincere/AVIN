#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

from __future__ import annotations

from avin.logger import logger


class Scout:  # {{{
    def __init__(self, broker, trader=None):  # {{{
        self.__broker = broker
        self.__trader = trader

    @property  # trader
    def trader(self):
        return self.__trader

    # }}}
    def setBroker(self, broker):  # {{{
        logger.debug(f"Scout.setBroker()")

    # }}}
    def updateAllData(self, asset):  # {{{
        for timeframe in TimeFrame.ALL:
            result = self.updateData(asset, timeframe)
            if not result:
                return False
        return True

    # }}}
    def makeStream(self, alist, timeframes):  # {{{
        self.stream = self.__broker.createDataStream()
        for asset in alist:
            for timeframe in timeframes:
                self.__broker.addSubscription(self.stream, asset, timeframe)
                logger.info(f"Scout add subscription {asset.ticker}-{timeframe}")
        self.__broker.checkStream(self.stream)

    # }}}
    def observe(self) -> Event:  # {{{
        event = self.__broker.waitEvent(self.stream)
        return event
        # if event.type == Event.Type.BAR:
        #     asset = self.trader.alist.find(figi=event.figi)
        #     asset.chart(timeframe).update(new_bars=[event.bar, ])
        #     last_time = (event.bar.dt + MSK_TIME_DIF).time()
        #     logger.info(
        #         f"Scout new bar {asset.ticker}-{timeframe} {last_time}"
        #         )
        #     event.updated_asset = asset
        #     e = Event.UpdateAsset(asset)
        #     return asset
        #     ...
        #     # тут бы разное выцепать из респонса и отправлять тупо
        #     # новое событие, это может быть свеча, ордер, операция...
        # else:
        #     return None

    # }}}


# }}}
