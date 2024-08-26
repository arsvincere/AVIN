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
    def __checkTypes(self, args: tuple):  # {{{
        for i, j in zip(args, self.args):
            assert isinstance(i, j)

    # }}}
    def emit(self, *args):  # {{{
        for receiver in self.__slots:
            self.__checkTypes(args)
            receiver(*args)

    # }}}
    def connect(self, slot):  # {{{
        self.__slots.append(slot)

    # }}}


# }}}


if __name__ == "__main__":
    ...
