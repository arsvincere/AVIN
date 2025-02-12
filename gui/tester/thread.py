#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

import asyncio

from PyQt6 import QtCore

from avin import Filter, FilterList, Test, Tester, TestList, TradeList, logger
from gui.custom import awaitQThread


class Thread:  # {{{
    """Fasade class"""

    @classmethod  # saveTest  # {{{
    def saveTest(cls, test: Test) -> None:
        logger.debug(f"{cls.__name__}.saveTest()")

        thread = _TSaveTest(test)
        thread.start()
        awaitQThread(thread)

    # }}}
    @classmethod  # loadTest  # {{{
    def loadTest(cls, name: str) -> Test | None:
        logger.debug(f"{cls.__name__}.loadTest()")

        thread = _TLoadTest(name)
        thread.start()
        awaitQThread(thread)

        return thread.result

    # }}}
    @classmethod  # loadTestList  # {{{
    def loadTestList(cls, name: str) -> Test | None:
        logger.debug(f"{cls.__name__}.loadTestList()")

        thread = _TLoadTestList(name)
        thread.start()
        awaitQThread(thread)

        return thread.result

    # }}}
    @classmethod  # deleteTest  # {{{
    def deleteTest(cls, test: Test) -> None:
        logger.debug(f"{cls.__name__}.deleteTest()")

        thread = _TDeleteTest(test)
        thread.start()
        awaitQThread(thread)

    # }}}
    @classmethod  # renameTest  # {{{
    def renameTest(cls, test: Test, new_name: str) -> Test | None:
        logger.debug(f"{cls.__name__}.renameTest()")

        thread = _TRenameTest(test, new_name)
        thread.start()
        awaitQThread(thread)

        return thread.result

    # }}}
    @classmethod  # copyTest  # {{{
    def copyTest(cls, test: Test, new_name: str) -> Test | None:
        logger.debug(f"{cls.__name__}.copyTest()")

        thread = _TCopyTest(test, new_name)
        thread.start()
        awaitQThread(thread)

        return thread.result

    # }}}
    @classmethod  # requestAllTest  # {{{
    def requestAllTest(cls) -> None:
        logger.debug(f"{cls.__name__}.requestAllTest()")

        thread = _TRequestAllTest()
        thread.start()
        awaitQThread(thread)

        return thread.result

    # }}}
    @classmethod  # requestAllTestList  # {{{
    def requestAllTest(cls) -> None:
        logger.debug(f"{cls.__name__}.requestAllTestList()")

        thread = _TRequestAllTestList()
        thread.start()
        awaitQThread(thread)

        return thread.result

    # }}}
    @classmethod  # fromJson  # {{{
    def fromJson(cls, obj) -> Test:
        logger.debug(f"{cls.__name__}.fromJson()")

        thread = _TFromJson(obj)
        thread.start()
        awaitQThread(thread)

        return thread.result

    # }}}

    @classmethod  # selectFilter  # {{{
    def selectFilter(cls, trade_list: TradeList, filter: Filter) -> Test:
        logger.debug(f"{cls.__name__}.selectFilter()")

        thread = _TSelectFilter(trade_list, filter)
        thread.start()
        awaitQThread(thread)

        return thread.result

    # }}}
    @classmethod  # selectFilterList  # {{{
    def selectFilterList(
        cls, trade_list: TradeList, filter_list: FilterList
    ) -> Test:
        logger.debug(f"{cls.__name__}.selectFilterList()")

        thread = _TSelectFilterList(trade_list, filter_list)
        thread.start()
        awaitQThread(thread)

        return thread.result

    # }}}
    @classmethod  # anyOfFilterList  # {{{
    def anyOfFilterList(
        cls, trade_list: TradeList, filter_list: FilterList
    ) -> Test:
        logger.debug(f"{cls.__name__}.anyOfFilterList()")

        thread = _TAnyOfFilterList(trade_list, filter_list)
        thread.start()
        awaitQThread(thread)

        return thread.result

    # }}}


# }}}
class _TSaveTest(QtCore.QThread):  # {{{
    def __init__(self, test: Test, parent=None):  # {{{
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtCore.QThread.__init__(self, parent)

        self.__test = test

    # }}}
    def run(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.run()")

        asyncio.run(self.__arun())

    # }}}
    async def __arun(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__arun()")

        await Test.save(self.__test)

    # }}}


# }}}
class _TLoadTest(QtCore.QThread):  # {{{
    def __init__(self, name: str, parent=None):  # {{{
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtCore.QThread.__init__(self, parent)

        self.__name = name
        self.result = None

    # }}}
    def run(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.run()")

        asyncio.run(self.__arun())

    # }}}
    async def __arun(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__arun()")

        self.result = await Test.load(self.__name)

    # }}}


# }}}
class _TLoadTestList(QtCore.QThread):  # {{{
    def __init__(self, name: str, parent=None):  # {{{
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtCore.QThread.__init__(self, parent)

        self.__name = name
        self.result = None

    # }}}
    def run(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.run()")

        asyncio.run(self.__arun())

    # }}}
    async def __arun(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__arun()")

        self.result = await TestList.load(self.__name)

    # }}}


# }}}
class _TDeleteTest(QtCore.QThread):  # {{{
    def __init__(self, test: Test, parent=None):  # {{{
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtCore.QThread.__init__(self, parent)

        self.__test = test

    # }}}
    def run(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.run()")

        asyncio.run(self.__arun())

    # }}}
    async def __arun(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__arun()")

        await Test.delete(self.__test)

    # }}}


# }}}
class _TRenameTest(QtCore.QThread):  # {{{
    def __init__(self, test: Test, new_name: str, parent=None):  # {{{
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtCore.QThread.__init__(self, parent)

        self.__test = test
        self.__new_name = new_name
        self.result = None

    # }}}
    def run(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.run()")

        asyncio.run(self.__arun())

    # }}}
    async def __arun(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__arun()")

        self.result = await Test.rename(self.__test, self.__new_name)

    # }}}


# }}}
class _TCopyTest(QtCore.QThread):  # {{{
    def __init__(self, test: Test, new_name: str, parent=None):  # {{{
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtCore.QThread.__init__(self, parent)

        self.__test = test
        self.__new_name = new_name
        self.result = None

    # }}}
    def run(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.run()")

        asyncio.run(self.__arun())

    # }}}
    async def __arun(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__arun()")

        self.result = await Test.copy(self.__test, self.__new_name)

    # }}}


# }}}
class _TRequestAllTest(QtCore.QThread):  # {{{
    def __init__(self, parent=None):  # {{{
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtCore.QThread.__init__(self, parent)

        self.result = None

    # }}}
    def run(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.run()")

        asyncio.run(self.__arun())

    # }}}
    async def __arun(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__arun()")

        self.result = await Test.requestAll()

    # }}}


# }}}
class _TRequestAllTestList(QtCore.QThread):  # {{{
    def __init__(self, parent=None):  # {{{
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtCore.QThread.__init__(self, parent)

        self.result = None

    # }}}
    def run(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.run()")

        asyncio.run(self.__arun())

    # }}}
    async def __arun(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__arun()")

        self.result = await TestList.requestAll()

    # }}}


# }}}
class _TFromJson(QtCore.QThread):  # {{{
    def __init__(self, obj, parent=None):  # {{{
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtCore.QThread.__init__(self, parent)

        self.__obj = obj
        self.result = None

    # }}}
    def run(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.run()")

        asyncio.run(self.__arun())

    # }}}
    async def __arun(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__arun()")

        self.result = await Test.fromJson(self.__obj)

    # }}}


# }}}
class _TSelectFilter(QtCore.QThread):  # {{{
    def __init__(self, trade_list, filter, parent=None):  # {{{
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtCore.QThread.__init__(self, parent)

        self.__trade_list = trade_list
        self.__filter = filter
        self.result = None

    # }}}
    def run(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.run()")

        asyncio.run(self.__arun())

    # }}}
    async def __arun(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__arun()")

        self.result = await self.__trade_list.selectFilter(self.__filter)

    # }}}


# }}}
class _TSelectFilterList(QtCore.QThread):  # {{{
    def __init__(self, trade_list, filter_list, parent=None):  # {{{
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtCore.QThread.__init__(self, parent)

        self.__trade_list = trade_list
        self.__filter_list = filter_list
        self.result = None

    # }}}
    def run(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.run()")

        asyncio.run(self.__arun())

    # }}}
    async def __arun(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__arun()")

        self.result = await self.__trade_list.selectFilterList(
            self.__filter_list
        )

    # }}}


# }}}
class _TAnyOfFilterList(QtCore.QThread):  # {{{
    def __init__(self, trade_list, filter_list, parent=None):  # {{{
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtCore.QThread.__init__(self, parent)

        self.__trade_list = trade_list
        self.__filter_list = filter_list
        self.result = None

    # }}}
    def run(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.run()")

        asyncio.run(self.__arun())

    # }}}
    async def __arun(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__arun()")

        self.result = await self.__trade_list.anyOfFilterList(
            self.__filter_list
        )

    # }}}


# }}}


class TRunTest(QtCore.QThread):  # {{{
    def __init__(self, test: Test, parent=None):  # {{{
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtCore.QThread.__init__(self, parent)

        self.test = test

    # }}}
    def run(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.run()")

        asyncio.run(self.__arun())

    # }}}
    async def __arun(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__anew()")

        t = Tester()
        await t.run(self.test)

    # }}}


# }}}


if __name__ == "__main__":
    ...
