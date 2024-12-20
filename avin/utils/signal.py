#!/usr/bin/env python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================


class Signal:  # {{{
    def __init__(self, *args):  # {{{
        self.args = args
        self.__slots = list()

    # }}}

    def connect(self, slot):  # {{{
        self.__slots.append(slot)

    # }}}
    def emit(self, *args):  # {{{
        for slot in self.__slots:
            self.__checkTypes(args)
            slot(*args)

    # }}}

    def __checkTypes(self, args: tuple):  # {{{
        for i, j in zip(args, self.args):
            assert isinstance(i, j)

    # }}}


# }}}
class AsyncSignal:  # {{{
    def __init__(self, *args):  # {{{
        self.args = args
        self.__async_slots = list()

    # }}}

    def aconnect(self, async_slot):  # {{{
        self.__async_slots.append(async_slot)

    # }}}
    async def aemit(self, *args):  # {{{
        all_task = list()
        for aslot in self.__async_slots:
            self.__checkTypes(args)
            coro = aslot(*args)
            #     task = asyncio.create_task(coro)
            #     all_task.append(task)
            # await asyncio.gather(*all_task)

            await coro

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


# }}}

if __name__ == "__main__":
    ...
