
class Message():# {{{
    def __init__(self, *args):# {{{
        self.args = args
        self.__receivers = list()
    # }}}
    def __checkTypes(self, args: tuple):# {{{
        for i, j in zip(args, self.args):
            assert type(i) == j
    # }}}
    def emit(self, *args):# {{{
        for i in self.__receivers:
            self.__checkTypes(args)
            i(*args)
    # }}}
    def connect(self, slot_func):# {{{
        self.__receivers.append(slot_func)
    # }}}
# }}}
