#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

""" Doc """

from __future__ import annotations

import abc

from avin.const import Usr
from avin.core.asset import AssetList
from avin.core.trade import Trade
from avin.utils import Cmd, Signal


class Strategy(metaclass=abc.ABCMeta):  # {{{
    """Signal"""  # {{{

    newTrade = Signal(Trade)
    tradeClosed = Signal(Trade)

    # }}}
    def __init__(self, name, version):  # {{{
        self.__name = name
        self.__version = version
        self.__loadConfig()
        self.__loadShortList()
        self.__loadLongList()

    # }}}
    def __str__(self):  # {{{
        return f"{self.name}-{self.version}"

    # }}}
    @property  # name# {{{
    def name(self):
        return self.__name

    # }}}
    @property  # version# {{{
    def version(self):
        return self.__version

    # }}}
    @property  # config# {{{
    def config(self):
        return self.__cfg

    # }}}
    @property  # timeframe_list# {{{
    def timeframe_list(self):
        return self.__cfg["timeframe_list"]

    # }}}
    @property  # long_list# {{{
    def long_list(self):
        return self.__long_list

    @long_list.setter
    def long_list(self, alist):
        alist.name = "long"
        self.__long_list = alist

    # }}}
    @property  # short_list# {{{
    def short_list(self):
        return self.__short_list

    @short_list.setter
    def short_list(self, alist):
        alist.name = "short"
        self.__short_list = alist

    # }}}
    @property  # path# {{{
    def path(self):
        path = Cmd.path(self.dir_path, f"{self.version}.py")
        return path

    # }}}
    @property  # dir_path# {{{
    def dir_path(self):
        path = Cmd.path(Usr.STRATEGY, self.name)
        return path

    # }}}
    @property  # general# {{{
    def general(self):
        return self.__general

    # }}}
    def start(self):  # {{{
        ...

    # }}}
    def finish(self):  # {{{
        ...

    # }}}
    @classmethod  # load# {{{
    def load(cls, name: str, version: str):
        module = name.lower()
        path = f"user.strategy.{name}.{version}"
        modul = importlib.import_module(path)
        strategy_class = modul.__getattribute__(f"UStrategy")
        s = strategy_class()
        return s

    # }}}
    @classmethod  # versions# {{{
    def versions(cls, strategy_name: str):
        path = Cmd.path(STRATEGY_DIR, strategy_name)
        files = Cmd.getFiles(path)
        files = Cmd.select(files, extension=".py")
        ver_list = list()
        for file in files:
            ver = file.replace(".py", "")
            ver_list.append(ver)
        return ver_list

    # }}}
    def __loadConfig(self):  # {{{
        path = Cmd.path(self.dir_path, "config.cfg")
        if Cmd.isExist(path):
            self.__cfg = Cmd.loadJson(path)
            return

        self.__cfg = None

    # }}}
    def __loadLongList(self):  # {{{
        path = Cmd.path(self.dir_path, "long.al")
        if Cmd.isExist(path):
            self.__long_list = AssetList.load(path, parent=self)
            return

        self.__long_list = None

    # }}}
    def __loadShortList(self):  # {{{
        path = Cmd.path(self.dir_path, "short.al")
        if Cmd.isExist(path):
            self.__short_list = AssetList.load(path, parent=self)
            return

        self.__short_list = None

    # }}}


# }}}

if __name__ == "__main__":
    ...
