#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

import asyncio

from PyQt6 import QtCore

from avin.tester import Test, Tester
from avin.utils import logger
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
    def loadTest(cls, name: str) -> None:
        logger.debug(f"{cls.__name__}.loadTest()")

        thread = _TLoadTest(name)
        thread.start()
        awaitQThread(thread)

        return thread.result

    # }}}
    @classmethod  # copyTest  # {{{
    def copyTest(cls, test: Test, new_name: str) -> None:
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


class TesterThread(QtCore.QThread):  # {{{
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
        logger.debug(f"{self.__class__.__name__}.__anew()")

        t = Tester()
        t.setTest(self.__test)
        await t.runTest()

    # }}}


# }}}


if __name__ == "__main__":
    ...
