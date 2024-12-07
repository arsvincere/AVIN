#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

import asyncio

from PyQt6 import QtCore

from avin.core import Strategy, StrategyList, StrategySet
from avin.utils import logger
from gui.custom import awaitQThread


class Thread:
    """Fasade class"""

    @classmethod  # new  # {{{
    def new(cls, name: str) -> Strategy | None:
        logger.debug(f"{cls.__name__}.new()")

        thread = _TNew(name)
        thread.start()
        awaitQThread(thread)

        return thread.strategy

    # }}}
    @classmethod  # copy  # {{{
    def copy(cls, strategy: Strategy, new_name: str) -> Strategy | None:
        logger.debug(f"{cls.__name__}.copy()")

        thread = _TCopy(strategy, new_name)
        thread.start()
        awaitQThread(thread)

        return thread.copy

    # }}}
    @classmethod  # renameStrategy  # {{{
    def renameStrategy(cls, old_name: str, new_name: str) -> str | None:
        logger.debug(f"{cls.__name__}.renameStrategy()")

        thread = _TRenameStrategy(old_name, new_name)
        thread.start()
        awaitQThread(thread)

        return thread.renamed

    # }}}
    @classmethod  # renameVersion  # {{{
    def renameVersion(
        cls, strategy: Strategy, new_name: str
    ) -> Strategy | None:
        logger.debug(f"{cls.__name__}.renameVersion()")

        thread = _TRenameVersion(strategy, new_name)
        thread.start()
        awaitQThread(thread)

        return thread.renamed

    # }}}
    @classmethod  # deleteStrategy  # {{{
    def deleteStrategy(cls, strategy_name: str) -> None:
        logger.debug(f"{cls.__name__}.deleteStrategy()")

        thread = _TDeleteStrategy(strategy_name)
        thread.start()
        awaitQThread(thread)

    # }}}
    @classmethod  # deleteVersion  # {{{
    def deleteVersion(cls, strategy: Strategy) -> None:
        logger.debug(f"{cls.__name__}.deleteVersion()")

        thread = _TDeleteVersion(strategy)
        thread.start()
        awaitQThread(thread)

    # }}}
    @classmethod  # load  # {{{
    def load(cls, name: str, version: str) -> Strategy:
        logger.debug(f"{cls.__name__}.load()")

        thread = _TLoad(name, version)
        thread.start()
        awaitQThread(thread)

        return thread.strategy

    # }}}

    @classmethod  # createLists  # {{{
    def createLists(cls, strategy_set: StrategySet) -> StrategyList:
        logger.debug(f"{cls.__name__}.createLists()")

        thread = _TCreateAListSList(strategy_set)
        thread.start()
        awaitQThread(thread)

        return thread.alist, thread.slist


# }}}


class _TNew(QtCore.QThread):  # {{{
    def __init__(self, name: str, parent=None):  # {{{
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
    def __init__(self, strategy: Strategy, new_name: str, parent=None):  # {{{
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtCore.QThread.__init__(self, parent)

        self.__strategy = strategy
        self.__new_name = new_name
        self.copy = None

    # }}}
    def run(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.run()")

        asyncio.run(self.__acopy())

    # }}}
    async def __acopy(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__acopy()")

        self.copy = await Strategy.copy(self.__strategy, self.__new_name)

    # }}}


# }}}
class _TRenameStrategy(QtCore.QThread):  # {{{
    def __init__(self, old_name: str, new_name: str, parent=None):  # {{{
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtCore.QThread.__init__(self, parent)

        self.__old_name = old_name
        self.__new_name = new_name
        self.renamed = None

    # }}}
    def run(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.run()")

        asyncio.run(self.__arename())

    # }}}
    async def __arename(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__arename()")

        self.renamed = await Strategy.renameStrategy(
            self.__old_name,
            self.__new_name,
        )

    # }}}


# }}}
class _TRenameVersion(QtCore.QThread):  # {{{
    def __init__(self, strategy: Strategy, new_name: str, parent=None):  # {{{
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtCore.QThread.__init__(self, parent)

        self.__strategy = strategy
        self.__new_name = new_name
        self.renamed = None

    # }}}
    def run(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.run()")

        asyncio.run(self.__arename())

    # }}}
    async def __arename(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__arename()")

        self.renamed = await Strategy.renameVersion(
            self.__strategy,
            self.__new_name,
        )

    # }}}


# }}}
class _TDeleteStrategy(QtCore.QThread):  # {{{
    def __init__(self, strategy_name: str, parent=None):  # {{{
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtCore.QThread.__init__(self, parent)

        self.__strategy_name = strategy_name

    # }}}
    def run(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.run()")

        asyncio.run(self.__adelete())

    # }}}
    async def __adelete(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__adelete()")

        await Strategy.deleteStrategy(self.__strategy_name)

    # }}}


# }}}
class _TDeleteVersion(QtCore.QThread):  # {{{
    def __init__(self, strategy: Strategy, parent=None):  # {{{
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtCore.QThread.__init__(self, parent)

        self.__strategy = strategy

    # }}}
    def run(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.run()")

        asyncio.run(self.__adelete())

    # }}}
    async def __adelete(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__adelete()")

        await Strategy.deleteVersion(self.__strategy)

    # }}}


# }}}
class _TLoad(QtCore.QThread):  # {{{
    def __init__(self, name: str, version: str, parent=None):  # {{{
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
class _TCreateAListSList(QtCore.QThread):  # {{{
    def __init__(self, strategy_set: StrategySet, parent=None):  # {{{
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtCore.QThread.__init__(self, parent)

        self.__sset = strategy_set
        self.alist = None
        self.slist = None

    # }}}
    def run(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.run()")

        asyncio.run(self.__acreate())

    # }}}
    async def __acreate(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__acreate()")

        # before create StrategyList need create AssetList
        self.alist = await self.__sset.createAssetList()

        # create StrategyList and save as self.result
        self.slist = await self.__sset.createStrategyList()

    # }}}


# }}}

if __name__ == "__main__":
    ...
