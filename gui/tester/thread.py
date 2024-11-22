#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

from PyQt6 import QtCore

from avin.tester import Test, Tester


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
