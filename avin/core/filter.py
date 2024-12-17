#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

from __future__ import annotations

from typing import Callable

from avin.config import Usr
from avin.utils import Cmd, logger


class Filter:
    def __init__(self, name: str, code: str):  # {{{
        logger.debug(f"{self.__class__.__name__}.__init__()")

        self.__name = name
        self.__code = code
        self.__condition = self.__createCondition(code)

    # }}}

    @property  # name  # {{{
    def name(self):
        return self.__name

    @name.setter
    def name(self, name):
        self.__name = name

    # }}}
    @property  # code  # {{{
    def code(self):
        return self.__code

    @code.setter
    def code(self, code):
        self.__code = code
        self.__condition = self.__createCondition(code)

    # }}}
    @property  # path  # {{{
    def path(self) -> str:
        return Cmd.path(Usr.FILTER, f"{self.__name}.py")

    # }}}

    def check(self, item: Asset | Trade) -> bool:  # {{{
        logger.debug(f"{self.__class__.__name__}.check()")

        return self.__condition(item)

    # }}}

    @classmethod  # save  # {{{
    def save(cls, f: Filter, file_path=None) -> None:
        logger.debug(f"{cls.__name__}.save()")

        if file_path is None:
            file_path = f.path

        Cmd.write(f.code, file_path)

    # }}}
    @classmethod  # load  # {{{
    def load(cls, name: str) -> Filter | None:
        logger.debug(f"{cls.__name__}.load()")

        file_path = Cmd.path(Usr.FILTER, f"{name}.py")
        if not Cmd.isExist(file_path):
            return None

        code = Cmd.read(file_path)

        f = Filter(name, code)
        return f

    # }}}
    @classmethod  # rename  # {{{
    def rename(cls, f: Filter, new_name: str) -> None:
        logger.debug(f"{cls.__name__}.rename()")

        if Cmd.isExist(f.path):
            new_path = Cmd.path(Usr.FILTER, f"{new_name}.py")
            Cmd.rename(f.path, new_path)
        f.__name = new_name

    # }}}
    @classmethod  # delete  # {{{
    def delete(cls, f: Filter) -> None:
        logger.debug(f"{cls.__name__}.delete()")

        Cmd.delete(f.path)

    # }}}

    def __createCondition(self, code: str) -> Callable:  # {{{
        logger.debug(f"{self.__class__.__name__}.__createCondition()")

        context = globals().copy()
        exec(code, context)
        func = context["condition"]

        return func

    # }}}


if __name__ == "__main__":
    ...
