#!/usr/bin/env python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

import asyncio


class Signal:  # {{{
    def __init__(self, *args):  # {{{
        self.args = args
        self.__slots = list()

    # }}}
    def __checkTypes(self, args: tuple):  # {{{
        for i, j in zip(args, self.args):
            assert isinstance(i, j)

    # }}}
    def emit(self, *args):  # {{{
        for slot in self.__slots:
            self.__checkTypes(args)
            slot(*args)

    # }}}
    def connect(self, slot):  # {{{
        self.__slots.append(slot)

    # }}}


# }}}
class AsyncSignal:  # {{{
    def __init__(self, *args):  # {{{
        self.args = args
        self.__async_slots = list()

    # }}}
    def __checkTypes(self, args: tuple):  # {{{
        for i, j in zip(args, self.args):
            # TODO: raise Exception, с сообщением о том что сигнал
            # отправлен с неправильными типами аргументов
            # или вообще нахер всю эту проверку типов? not pythonic way?
            # Может если кому где надо, проверку полученных
            # аргументов уже в слоте реализовывать?
            assert isinstance(i, j)

    # }}}
    async def async_emit(self, *args):  # {{{
        all_task = list()
        for aslot in self.__async_slots:
            self.__checkTypes(args)
            coro = aslot(*args)
            task = asyncio.create_task(coro)
            all_task.append(task)
        await asyncio.gather(*all_task)

    # }}}
    async def async_connect(self, async_slot):  # {{{
        # NOTE: async тут только для визуального выделения в коде
        # и сделано корутиной тоже только для выделения, чтобы сразу
        # иметь ввиду что слоты должны быть тоже корутинами.
        # Возможно это я перебдел. Может уберу потом async из def
        # TODO: check что слот это корутина
        self.__async_slots.append(slot)

    # }}}


# }}}

if __name__ == "__main__":
    ...
