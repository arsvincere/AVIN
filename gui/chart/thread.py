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

from avin.analytic import Analytic
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
    @classmethod  # addMark  # {{{
    def addMark(cls, gchart: GChart, mark: Mark) -> None:
        logger.debug(f"{cls.__name__}.addGMarker()")

        thread = _TAddMarker(gchart, mark)
        thread.start()
        awaitQThread(thread)

    # }}}
    @classmethod  # getMaxVol  # {{{
    def getMaxVol(cls, instrument, timeframe) -> int:
        logger.debug(f"{cls.__name__}.getMaxVol()")

        thread = _TGetMaxVol(instrument, timeframe)
        thread.start()
        awaitQThread(thread)

        return thread.result

    # }}}
    @classmethod  # getVolSizes  # {{{
    def getVolSizes(cls, instrument, timeframe) -> int:
        logger.debug(f"{cls.__name__}.getVolSizes()")

        thread = _TGetVolSizes(instrument, timeframe)
        thread.start()
        awaitQThread(thread)

        return thread.result

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
    def __init__(self, gchart: GChart, mark: Mark, parent=None):  # {{{
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtCore.QThread.__init__(self, parent)

        self.__gchart = gchart
        self.__mark = mark

    # }}}
    def run(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.run()")

        asyncio.run(self.__arun())

    # }}}
    async def __arun(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__arun()")

        gchart = self.__gchart
        mark = self.__mark
        chart = self.__gchart.chart
        f = self.__mark.filter

        chart.setHeadIndex(0)
        while chart.nextHead():
            result = await f.acheck(chart)
            if result:
                dt = chart.now.dt
                gbar = gchart.barFromDatetime(dt)
                gbar.addGShape(mark.shape)

    # }}}


# }}}
class _TGetMaxVol(QtCore.QThread):  # {{{
    def __init__(  # {{{
        self,
        instrument: Instrument,
        timeframe: TimeFrame,
        parent=None,
    ):
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtCore.QThread.__init__(self, parent)

        self.__instrument = instrument
        self.__timeframe = timeframe

        self.result = None

    # }}}
    def run(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.run()")

        asyncio.run(self.__arun())

    # }}}
    async def __arun(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__arun()")

        analytic = await Analytic.load("volume")
        self.result = await analytic.maxVol(
            self.__instrument, self.__timeframe
        )

    # }}}


# }}}
class _TGetVolSizes(QtCore.QThread):  # {{{
    def __init__(  # {{{
        self,
        instrument: Instrument,
        timeframe: TimeFrame,
        parent=None,
    ):
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtCore.QThread.__init__(self, parent)

        self.__instrument = instrument
        self.__timeframe = timeframe

        self.result = None

    # }}}
    def run(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.run()")

        asyncio.run(self.__arun())

    # }}}
    async def __arun(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__arun()")

        analytic = await Analytic.load("volume")
        self.result = await analytic.sizes(
            self.__instrument, self.__timeframe
        )

    # }}}


# }}}


if __name__ == "__main__":
    ...
