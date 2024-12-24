#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

from __future__ import annotations

import asyncio
from datetime import datetime

from PyQt6 import QtCore

from avin.core import Chart, TimeFrame
from avin.data import Instrument
from avin.utils import logger
from gui.custom import awaitQThread


class Thread:  # {{{
    """Fasade class"""

    @classmethod  # loadChart  # {{{
    def loadChart(cls, instrument, timeframe, begin, end) -> Chart:
        logger.debug(f"{cls.__name__}.loadChart()")

        thread = _TLoadChart(instrument, timeframe, begin, end)
        thread.start()
        awaitQThread(thread)

        return thread.result

    # }}}
    @classmethod  # addGMarker  # {{{
    def addGMarker(cls, gchart: GChart, gmarker: GMarker) -> None:
        logger.debug(f"{cls.__name__}.addGMarker()")

        thread = _TAddMarker(gchart, gmarker)
        thread.start()
        awaitQThread(thread)

    # }}}


# }}}
class _TLoadChart(QtCore.QThread):  # {{{
    def __init__(
        self,
        instrument: Instrument,
        timeframe: TimeFrame,
        begin: datetime,
        end: datetime,
        parent=None,
    ):  # {{{
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtCore.QThread.__init__(self, parent)

        self.__instrument = instrument
        self.__timeframe = timeframe
        self.__begin = begin
        self.__end = end

        self.result = None

    # }}}
    def run(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.run()")

        asyncio.run(self.__arun())

    # }}}
    async def __arun(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__arun()")

        self.result = await Chart.load(
            self.__instrument,
            self.__timeframe,
            self.__begin,
            self.__end,
        )

    # }}}


# }}}
class _TAddMarker(QtCore.QThread):  # {{{
    def __init__(self, gchart: GChart, marker: Marker, parent=None):  # {{{
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtCore.QThread.__init__(self, parent)

        self.__gchart = gchart
        self.__marker = marker

    # }}}
    def run(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.run()")

        asyncio.run(self.__arun())

    # }}}
    async def __arun(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__arun()")

        gchart = self.__gchart
        marker = self.__marker
        chart = self.__gchart.chart
        f = self.__marker.filter

        chart.setHeadIndex(0)
        while chart.nextHead():
            result = await f.acheck(chart)
            if result:
                dt = chart.now.dt
                gbar = gchart.barFromDatetime(dt)
                gbar.addShape(marker.shape)

    # }}}


# }}}


if __name__ == "__main__":
    ...
