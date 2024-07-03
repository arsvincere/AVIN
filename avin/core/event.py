
class Event():# {{{
    class Type(enum.Enum):# {{{
        UNDEFINE =      0
        NEW_BAR =       1
        ORDER =         2
        OPERATION =     3
        LAST_PRICE =    4
        INFO =          5
        PING =          6
        UPDATED_ASSET = 7
    # }}}
    class NewBar():# {{{
        def __init__(self, figi, timeframe, bar):
            self.figi = figi
            self.timeframe = timeframe
            self.bar = bar
            self.type = Event.Type.NEW_BAR
    # }}}
    # @dataclass  #NewBar{{{
    # class NewBar():
    #     figi:       str
    #     timeframe:  TimeFrame
    #     bar:        Bar
    #     type:       EventType.NEW_BAR
    # }}}
    @dataclass  #Order# {{{
    class Order():
        ...
    # }}}
    @dataclass  #Operation# {{{
    class Operation():
        ...
    # }}}
    @dataclass  #LastPrice# {{{
    class LastPrice():
        ...
    # }}}
    @dataclass  #Info# {{{
    class Info():
        ...
    # }}}
    @dataclass  #Ping# {{{
    class Ping():
        ...
    # }}}
# }}}
