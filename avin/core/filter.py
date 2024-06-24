#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

""" doc """

from __future__ import annotations
from avin.const import Usr
from avin.utils import Cmd

class Filter():# {{{
    def __init__(self, name: str, code: str):# {{{
        self.__name = name
        self.__code = code
        self.__createFunc()
    # }}}
    @property  #name# {{{
    def name(self):
        return self.__name
    @name.setter
    def name(self, name):
        self.__name = name
    # }}}
    @property  #code# {{{
    def code(self):
        return self.__code
    @code.setter
    def code(self, code):
        self.__code = code
        self.__createFunc()
    # }}}
    @property  #path# {{{
    def path(self) -> str:
        return Cmd.path(Usr.FILTER, f"{self.name}.py")
    # }}}
    def check(self, item: Asset | Trade) -> bool:# {{{
        return self.__condition(item)
    # }}}
    @classmethod  #save# {{{
    def save(cls, f: Filter, file_path=None) -> None:
        print()
        if file_path is None:
            file_path = f.path
        Cmd.write(f.code, file_path)
    # }}}
    @classmethod  #load# {{{
    def load(cls, file_path: str) -> Filter:
        name = Cmd.name(file_path, extension=False)
        code = Cmd.read(file_path)
        f = Filter(name, code)
        return f
    # }}}
    @classmethod  #rename# {{{
    def rename(cls, f: Filter, new_name: str) -> None:
        if Cmd.isExist(f.path):
            new_path = Cmd.path(Usr.FILTER, f"{new_name}.py")
            Cmd.rename(f.path, new_path)
        f.__name = new_name
    # }}}
    @classmethod  #delete# {{{
    def delete(cls, f: Filter) -> None:
        Cmd.delete(f.path)
    # }}}
    def __createFunc(self):# {{{
        context = globals().copy()
        exec(self.__code, context)
        self.__condition = context["condition"]
    # }}}
# }}}

