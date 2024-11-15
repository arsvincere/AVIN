#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

import asyncio

from PyQt6 import QtCore

from avin.core import Asset, AssetList
from avin.utils import logger
from gui.custom import awaitQThread


class Thread:  # {{{
    """Fasade class"""

    @classmethod  # save  # {{{
    def save(cls, alist: AssetList) -> None:
        logger.debug(f"{cls.__name__}.save()")
        assert isinstance(alist, AssetList)

        thread = _TSave(alist)
        thread.start()
        awaitQThread(thread)

    # }}}
    @classmethod  # load  # {{{
    def load(cls, name: str) -> AssetList:
        logger.debug(f"{cls.__name__}.load()")

        thread = _TLoad(name)
        thread.start()
        awaitQThread(thread)

        return thread.alist

    # }}}
    @classmethod  # copy  # {{{
    def copy(cls, alist: AssetList, new_name: str) -> None:
        logger.debug(f"{cls.__name__}.copy()")

        thread = _TCopy(alist, new_name)
        thread.start()
        awaitQThread(thread)

    # }}}
    @classmethod  # rename  # {{{
    def rename(cls, alist: AssetList, new_name: str) -> None:
        logger.debug(f"{cls.__name__}.rename()")

        thread = _TRename(alist, new_name)
        thread.start()
        awaitQThread(thread)

    # }}}
    @classmethod  # delete  # {{{
    def delete(cls, alist: AssetList) -> None:
        logger.debug(f"{cls.__name__}.delete()")

        thread = _TDelete(alist)
        thread.start()
        awaitQThread(thread)

    # }}}
    @classmethod  # requestAllAssetList  # {{{
    def requestAllAssetList(cls) -> list[str]:
        logger.debug(f"{cls.__name__}.requestAllAssetList()")

        thread = _TRequestAllAssetList()
        thread.start()
        awaitQThread(thread)

        return thread.all_list

    # }}}
    @classmethod  # requestAllAsset  # {{{
    def requestAllAsset(cls) -> list[Asset]:
        logger.debug(f"{cls.__name__}.requestAllAsset()")

        thread = _TRequestAllAsset()
        thread.start()
        awaitQThread(thread)

        return thread.assets

    # }}}


# }}}


class _TRequestAllAssetList(QtCore.QThread):  # {{{
    def __init__(self, parent=None):  # {{{
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtCore.QThread.__init__(self, parent)

        self.all_list = list()

    # }}}
    def run(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.run()")
        asyncio.run(self.__arequest())

    # }}}
    async def __arequest(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__arequest()")

        self.all_list = await AssetList.requestAll()

    # }}}


# }}}
class _TRequestAllAsset(QtCore.QThread):  # {{{
    def __init__(self, parent=None):  # {{{
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtCore.QThread.__init__(self, parent)

        self.assets = None

    # }}}
    def run(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.run()")

        asyncio.run(self.__aload())

    # }}}
    async def __aload(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__aload()")

        self.assets = await Asset.requestAll()

    # }}}


# }}}
class _TLoad(QtCore.QThread):  # {{{
    def __init__(  # {{{
        self, name, parent=None
    ):
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtCore.QThread.__init__(self, parent)

        self.__name = name
        self.alist = None

    # }}}
    def run(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.run()")

        asyncio.run(self.__aload())

    # }}}
    async def __aload(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__aload()")

        self.alist = await AssetList.load(self.__name)

    # }}}


# }}}
class _TSave(QtCore.QThread):  # {{{
    def __init__(self, alist, parent=None):  # {{{
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtCore.QThread.__init__(self, parent)

        self.__alist = alist

    # }}}
    def run(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.run()")

        asyncio.run(self.__asave())

    # }}}
    async def __asave(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__asave()")

        await AssetList.save(self.__alist)

    # }}}


# }}}
class _TCopy(QtCore.QThread):  # {{{
    def __init__(self, alist, new_name, parent=None):  # {{{
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtCore.QThread.__init__(self, parent)

        self.__alist = alist
        self.__new_name = new_name

    # }}}
    def run(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.run()")

        asyncio.run(self.__acopy())

    # }}}
    async def __acopy(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__acopy()")

        await AssetList.copy(self.__alist, self.__new_name)

    # }}}


# }}}
class _TRename(QtCore.QThread):  # {{{
    def __init__(self, alist, new_name, parent=None):  # {{{
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtCore.QThread.__init__(self, parent)

        self.__alist = alist
        self.__new_name = new_name

    # }}}
    def run(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.run()")

        asyncio.run(self.__arename())

    # }}}
    async def __arename(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__arename()")

        await AssetList.rename(self.__alist, self.__new_name)

    # }}}


# }}}
class _TDelete(QtCore.QThread):  # {{{
    def __init__(self, alist, parent=None):  # {{{
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtCore.QThread.__init__(self, parent)

        self.__alist = alist

    # }}}
    def run(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.run()")

        asyncio.run(self.__adelete())

    # }}}
    async def __adelete(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__adelete()")

        await AssetList.delete(self.__alist)

    # }}}


# }}}

if __name__ == "__main__":
    ...
