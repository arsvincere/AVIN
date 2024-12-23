#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

import asyncio

from PyQt6 import QtCore
from PyQt6.QtCore import Qt

from avin.data import ConvertTaskList, Data, DataInfo, DataType, Instrument
from avin.utils import logger
from gui.custom import awaitQThread
from gui.data.item import DownloadItem


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
    @classmethod  # requestData  # {{{
    def requestData(cls, instrument, data_type, begin, end) -> None:
        logger.debug(f"{cls.__name__}.firstDateTime()")

        thread = _TRequestData(instrument, data_type, begin, end)
        thread.start()
        awaitQThread(thread)

        return thread.result

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

        # alias
        CHECKED = Qt.CheckState.Checked

        for i in self.__tree:
            if i.checkState(DownloadItem.Column.Ticker) != CHECKED:
                continue

            # receive first 1M datetime
            dt = await Data.firstDateTime(
                self.__source, i.instrument, DataType.BAR_1M
            )
            if dt is not None:
                dt = dt.strftime("%Y-%m-%d")
                i.setText(DownloadItem.Column.First_1M, dt)
                logger.info(
                    f"  - received first 1M date for {i.instrument} -> {dt}"
                )

            # receive first D datetime
            dt = await Data.firstDateTime(
                self.__source, i.instrument, DataType.BAR_D
            )
            if dt is not None:
                dt = dt.strftime("%Y-%m-%d")
                i.setText(DownloadItem.Column.First_D, dt)
                logger.info(
                    f"  - received first D date for {i.instrument} -> {dt}"
                )

    # }}}


# }}}
class _TRequestData(QtCore.QThread):  # {{{
    def __init__(self, instrument, data_type, begin, end, parent=None):  # {{{
        QtCore.QThread.__init__(self, parent)

        self.__instrument = instrument
        self.__data_type = data_type
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

        self.result = await Data.request(
            self.__instrument, self.__data_type, self.__begin, self.__end
        )


# }}}


class TDownload(QtCore.QThread):  # {{{
    name = "Download"

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
        logger.debug(f"{self.__class__.__name__}.__adownload()")

        for instrument in self.__instruments:
            for timeframe in self.__timeframes:
                data_type = timeframe.toDataType()
                year = self.__begin
                while year <= self.__end:
                    await Data.download(
                        self.__source, instrument, data_type, year
                    )
                    year += 1

    # }}}


# }}}
class TDelete(QtCore.QThread):  # {{{
    name = "Delete"

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
class TUpdate(QtCore.QThread):  # {{{
    name = "Update"

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
class TConvert(QtCore.QThread):  # {{{
    name = "Convert"

    def __init__(  # {{{
        self, convert_list_name: str, parent=None
    ):
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtCore.QThread.__init__(self, parent)

        self.__clist_name = convert_list_name

    # }}}
    def run(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.run()")
        asyncio.run(self.__aconvert())

    # }}}
    async def __aconvert(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__aconvert()")

        clist = await ConvertTaskList.load(self.__clist_name)
        for task in clist:
            await Data.convert(task)

    # }}}


# }}}


if __name__ == "__main__":
    ...
