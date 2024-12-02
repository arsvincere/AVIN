#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

import asyncio

from PyQt6 import QtCore

from avin.data import Data, DataInfo, Instrument
from avin.utils import logger
from gui.custom import awaitQThread


class Thread:  # {{{
    """Fasade class"""

    @classmethod  # info  # {{{
    def info(cls) -> DataInfo | None:
        logger.debug(f"{cls.__name__}.info()")

        thread = _TInfo()
        thread.start()
        awaitQThread(thread)

        return thread.info

    # }}}
    @classmethod  # find  # {{{
    def find(cls, source, itype) -> list[Instrument]:
        logger.debug(f"{cls.__name__}.find()")

        thread = _TFind(source, itype)
        thread.start()
        awaitQThread(thread)

        return thread.instruments

    # }}}
    @classmethod  # firstDateTime  # {{{
    def firstDateTime(cls, source, tree) -> None:
        logger.debug(f"{cls.__name__}.firstDateTime()")

        thread = _TFirstDate(source, tree)
        thread.start()
        awaitQThread(thread)

    # }}}
    @classmethod  # download  # {{{
    def download(cls, source, instruments, timeframes, begin, end) -> None:
        logger.debug(f"{cls.__name__}.download()")

        thread = _TDownload(source, instruments, timeframes, begin, end)
        thread.start()
        awaitQThread(thread)

    # }}}
    @classmethod  # delete  # {{{
    def delete(cls, data_info: DataInfo) -> None:
        logger.debug(f"{cls.__name__}.delete()")

        thread = _TDelete(data_info)
        thread.start()
        awaitQThread(thread)

    # }}}
    @classmethod  # update  # {{{
    def update(cls, data_info: DataInfo) -> None:
        logger.debug(f"{cls.__name__}.update()")

        thread = _TUpdate(data_info)
        thread.start()
        awaitQThread(thread)

    # }}}


# }}}


class _TInfo(QtCore.QThread):  # {{{
    def __init__(self, parent=None):  # {{{
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtCore.QThread.__init__(self, parent)

    # }}}
    def run(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.run()")
        asyncio.run(self.__ainfo())

    # }}}
    async def __ainfo(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__ainfo()")

        self.info = await Data.info()

    # }}}


# }}}
class _TFind(QtCore.QThread):  # {{{
    def __init__(self, source, itype, parent=None):  # {{{
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtCore.QThread.__init__(self, parent)

        self.__source = source
        self.__itype = itype

    # }}}
    def run(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.run()")
        asyncio.run(self.__afind())

    # }}}
    async def __afind(self):  # {{{
        self.instruments = await Data.find(
            source=self.__source, itype=self.__itype
        )

    # }}}


# }}}
class _TFirstDate(QtCore.QThread):  # {{{
    def __init__(self, source, tree, parent=None):  # {{{
        QtCore.QThread.__init__(self, parent)
        self.__source = source
        self.__tree = tree

    # }}}
    def run(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.run()")
        asyncio.run(self.__afirst())

    # }}}
    async def __afirst(self):  # {{{
        # TODO: логи уровня инфо - затолкать в модуль дата
        # передача дерева - это очень спорное решение, так проще
        # но это ппц, думай как сделать нормально
        logger.debug(f"{self.__class__.__name__}.__afirst()")
        logger.info(":: Receiving first date")

        for i in self.__tree:
            if i.checkState(_Item.Column.Ticker) != Qt.CheckState.Checked:
                continue

            # receive first 1M datetime
            dt = await Data.firstDateTime(
                self.__source, i.instrument, DataType.BAR_1M
            )
            if dt is not None:
                dt = dt.strftime("%Y-%m-%d")
                i.setText(_Item.Column.First_1M, dt)
                logger.info(
                    f"  - received first 1M date for {i.instrument} -> {dt}"
                )

            # receive first D datetime
            dt = await Data.firstDateTime(
                self.__source, i.instrument, DataType.BAR_D
            )
            if dt is not None:
                dt = dt.strftime("%Y-%m-%d")
                i.setText(_Item.Column.First_D, dt)
                logger.info(
                    f"  - received first D date for {i.instrument} -> {dt}"
                )

    # }}}


# }}}
class _TDownload(QtCore.QThread):  # {{{
    def __init__(  # {{{
        self, source, instruments, timeframes, begin, end, parent=None
    ):
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtCore.QThread.__init__(self, parent)

        self.__source = source
        self.__instruments = instruments
        self.__timeframes = timeframes
        self.__begin = begin
        self.__end = end

    # }}}
    def run(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.run()")
        asyncio.run(self.__adownload())

    # }}}
    async def __adownload(self):  # {{{
        # TODO: тоже самое, логи уровня инфо - тут скорее всего лишнее
        # пусть это в ядре будет, там как то понятно и однозначно
        # не надо размазывать логи по всему приложению
        # в модуль дата это все пихай.
        logger.info(":: Start download data")

        for instrument in self.__instruments:
            for timeframe in self.__timeframes:
                data_type = timeframe.toDataType()
                year = self.__begin
                while year <= self.__end:
                    await Data.download(
                        self.__source, instrument, data_type, year
                    )
                    year += 1

        logger.info("Download complete!")

    # }}}


# }}}
class _TDelete(QtCore.QThread):  # {{{
    def __init__(  # {{{
        self, data_info: DataInfo, parent=None
    ):
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtCore.QThread.__init__(self, parent)

        self.__data_info = data_info

    # }}}
    def run(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.run()")
        asyncio.run(self.__adelete())

    # }}}
    async def __adelete(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__adelete()")

        for i in self.__data_info:
            await Data.delete(i.instrument, i.data_type)

    # }}}


# }}}
class _TUpdate(QtCore.QThread):  # {{{
    def __init__(  # {{{
        self, data_info: DataInfo, parent=None
    ):
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtCore.QThread.__init__(self, parent)

        self.__data_info = data_info

    # }}}
    def run(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.run()")
        asyncio.run(self.__aupdate())

    # }}}
    async def __aupdate(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__aupdate()")

        # update all if no selected items
        if len(self.__data_info) == 0:
            await Data.updateAll()

        # if has selected - update only selected items
        for i in self.__data_info:
            await Data.update(i.instrument, i.data_type)

    # }}}


# }}}


if __name__ == "__main__":
    ...
