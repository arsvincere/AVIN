#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

import asyncio

from PyQt6 import QtCore

from avin.core import Strategy
from avin.utils import logger
from gui.custom import awaitQThread


class Thread:
    """Fasade class"""

    @classmethod  # new  # {{{
    def new(cls, name: str) -> Strategy:
        logger.debug(f"{cls.__name__}.new()")

        thread = _TNew(name)
        thread.start()
        awaitQThread(thread)

        return thread.strategy

    # }}}
    @classmethod  # copy  # {{{
    def copy(cls, strategy: Strategy, new_name: str) -> Strategy:
        logger.debug(f"{cls.__name__}.copy()")

        thread = _TCopy(strategy, new_name)
        thread.start()
        awaitQThread(thread)

        return thread.copy

    # }}}
    @classmethod  # load  # {{{
    def load(cls, name: str, version: str) -> Strategy:
        logger.debug(f"{cls.__name__}.load()")

        thread = _TLoad(name, version)
        thread.start()
        awaitQThread(thread)

        return thread.strategy

    # }}}


class _TNew(QtCore.QThread):  # {{{
    def __init__(self, name, parent=None):  # {{{
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtCore.QThread.__init__(self, parent)

        self.__name = name
        self.strategy = None

    # }}}
    def run(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.run()")

        asyncio.run(self.__anew())

    # }}}
    async def __anew(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__anew()")

        self.strategy = await Strategy.new(self.__name)

    # }}}


# }}}
class _TCopy(QtCore.QThread):  # {{{
    def __init__(self, strategy, name, parent=None):  # {{{
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtCore.QThread.__init__(self, parent)

        self.__strategy = strategy
        self.__name = name
        self.copy = None

    # }}}
    def run(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.run()")

        asyncio.run(self.__acopy())

    # }}}
    async def __acopy(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__acopy()")

        self.copy = await Strategy.copy(self.__strategy, self.__name)

    # }}}


# }}}
class _TLoad(QtCore.QThread):  # {{{
    def __init__(self, name, version, parent=None):  # {{{
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtCore.QThread.__init__(self, parent)

        self.__name = name
        self.__ver = version
        self.strategy = None

    # }}}
    def run(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.run()")

        asyncio.run(self.__aload())

    # }}}
    async def __aload(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__aload()")

        self.strategy = await Strategy.load(self.__name, self.__ver)

    # }}}


# }}}

if __name__ == "__main__":
    ...
