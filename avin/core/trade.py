#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

from __future__ import annotations

class Trade():# {{{
    class Type(enum.Enum):# {{{
        UNDEFINE =  0
        LONG =      1
        SHORT =     2
    # }}}
    class Status(enum.Enum):# {{{
        UNDEFINE = 0
        INITIAL =  1
        NEW =      2
        POST =     3
        OPEN =     4
        CLOSE =    5
        ARCHIVE =  7
        CANCELED = 8
    # }}}
    def __init__(# {{{
        self,
        dt: datetime,
        strategy: Strategy,
        trade_type: Trade.Type,
        asset: Asset,
        status: Trade.Status=Trade.Status.INITIAL,
        uid="",
        ):

        strategy_info = {
            "datetime":         dt,
            "strategy":         strategy.name,
            "version":          strategy.version,
            "type":             trade_type,
            "asset":            asset,
            }
        self.__info = {
            "uid":              uid,
            "status":           status,
            "strategy":         strategy_info,
            "orders":           list(),
            "operations":       list(),
            "position":         None,
            }
        self.__blocked = False
    # }}}
    def __str__(self):# {{{
        dt = self.dt
        dt = dt.strftime("%Y-%m-%d %H:%M")
        string = (
            f"==> Trade {dt} {self.strategy}-{self.version} "
            f"{self.asset.ticker} {self.type.name.lower()}"
            )
        return string
    # }}}
    @property  #uid# {{{
    def uid(self):
        return self.__info["uid"]
    # }}}
    @property  #status# {{{
    def status(self):
        return self.__info["status"]
    @status.setter
    def status(self, status):
        self.__info["status"] = status
    # }}}
    @property  #dt# {{{
    def dt(self):
        return self._info["strategy"]["signal_datetime"]
    # }}}
    @property  #strategy# {{{
    def strategy(self):
        return self._info["strategy"]
    # }}}
    @property  #type# {{{
    def type(self):
        return self.__info["strategy"]["type"]
    # }}}
    @property  #asset# {{{
    def asset(self):
        return self._info["strategy"]["asset"]
    # }}}
    @property  #order# {{{
    def order(self):
        return self._info["order"]
    # }}}
    @property  #operation# {{{
    def operation(self):
        return self._info["operation"]
    # }}}
    @property  #position# {{{
    def position(self):
        return self._info["position"]
    # }}}
    @property  #open_price# {{{
    def open_price(self):
        return self.__info["strategy"]["open_price"]
    # }}}
    @property  #stop_price# {{{
    def stop_price(self):
        return self.__info["strategy"]["stop_price"]
    # }}}
    @property  #take_price# {{{
    def take_price(self):
        return self.__info["strategy"]["take_price"]
    # }}}
    @property  #open_dt# {{{
    def open_dt(self):
        return self._info["position"]["open_datetime"]
    # }}}
    @property  #close_dt# {{{
    def close_dt(self):
        return self._info["position"]["close_datetime"]
    # }}}
    @property  #result# {{{
    def result(self):
        result = self._info["position"]["result"]
        return round(result, 2)
    # }}}
    @property  #holding# {{{
    def holding(self):
        return self._info["position"]["holding_days"]
    # }}}
    @property  #percent_per_day# {{{
    def percent_per_day(self):
        return self._info["position"]["percent_per_day"]
    # }}}
    def addOrder(self, order: Order):# {{{
        self.__info["orders"].append(order)
    # }}}
    def addOperation(self, operation: Operation):# {{{
        self.__info["operations"].append(operation)
    # }}}
    def addPosition(self, Position):# {{{
        self.__info["positions"].append(position)
    # }}}
    def chart(self, timeframe: TimeFrame) -> Chart:# {{{
        assert self.asset.type == Type.SHARE
        end = self.dt
        begin = self.dt - Chart.DEFAULT_BARS_COUNT * timeframe
        chart = Chart(self.asset, timeframe, begin, end)
        return chart
    # }}}
    def isLong(self):# {{{
        return self._info["strategy"]["type"] == Signal.Type.LONG
    # }}}
    def isShort(self):# {{{
        return self._info["strategy"]["type"] == Signal.Type.SHORT
    # }}}
    def isWin(self):# {{{
        return self.result > 0
    # }}}
    def isLoss(self):# {{{
        return self.result <= 0
    # }}}
    def isBlocked(self):# {{{
        return self.__blocked
    # }}}
    def setBlocked(self, val: bool):# {{{
        self.__blocked = val
    # }}}
    @classmethod  #toJSON# {{{
    def toJSON(cls, trade):
        return trade._info
    # }}}
    @classmethod  #fromJSON# {{{
    def fromJSON(cls, obj):
        assert False
    # }}}
    @classmethod  # save{{{
    def save(cls, signal: Signal):
        assert False, "не написана функция, или в bin?"
    # }}}
    @classmethod  # load{{{
    def load(cls, path: str):
        assert False, "не написана функция, или в bin?"
    # }}}
    def __encode_for_JSON(self, obj):# {{{
        for k, v in obj.items():
            if isinstance(v, (enum.Enum, datetime, TimeFrame)):
                obj[k] = str(obj[k])
            elif isinstance(v, Asset):
                obj[k] = Asset.toJSON(obj[k])
            elif isinstance(v, Strategy):
                obj[k] = obj[k].name + "-" + obj[k].version
            elif k == "timeframe_list":
                tmp = list()
                for t in obj["timeframe_list"]:
                    string = str(t)
                    tmp.append(string)
                obj["timeframe_list"] = tmp
                # after transformation it looks like ["1M", "D"]
        return obj
    # }}}
    def __formatInfo(self):# {{{
        i = self.__info
        i["status"] =   str(i["status"])
        i["strategy"] = self.__encode_for_JSON(i["strategy"])
        i["analytic"] = self.__encode_for_JSON(i["analytic"])
        i["market"] =   self.__encode_for_JSON(i["market"])
        i["risk"] =     self.__encode_for_JSON(i["risk"])
        i["ruler"] =    self.__encode_for_JSON(i["ruler"])
        i["adviser"] =  self.__encode_for_JSON(i["adviser"])
        i["position"] = self.__encode_for_JSON(i["position"])
        for n, op in enumerate(i["operation"]):
            i["operation"][n] = Operation.toJSON(op)
        return i
    # }}}
# }}}
class TradeList():# {{{
    def __init__(self, name: str="unnamed", trades=None, parent=None):# {{{
        self._name = name
        self._trades = trades if trades is not None else list()
        self._childs = list()
        self._asset = None
        self._parent = parent
        if isinstance(parent, Test):
            self._test = parent
        elif isinstance(parent, TradeList):
            self._asset = parent._asset
            self._test = parent._test
    # }}}
    def __iter__(self):# {{{
        return iter(self._trades)
    # }}}
    def _createChild(self, trades, suffix):# {{{
        child_name = f"- {suffix}"
        child = TradeList(
            name=child_name,
            trades=trades,
            parent=self
            )
        child._asset = self.asset
        self._childs.append(child)
        return child
    # }}}
    def _selectStrategy(self, key, value):# {{{
        selected = list()
        for trade in self._trades:
            x = trade["strategy"].get(key)
            if x == value:
                selected.append(trade)
        tlist = TradeList(
            name="- " + self.name + f" strategy-{key}-{value}",
            trades=selected,
            parent=self
            )
        tlist._asset = self.asset
        self._childs.append(tlist)
        return tlist
    # }}}
    def _selectAnalytic(self, key, value):# {{{
        selected = list()
        for trade in self._trades:
            x = trade["analytic"].get(key)
            if x == value:
                selected.append(trade)
        tlist = TradeList(
            name="- " + self.name + f" analytic-{key}-{value}",
            trades=selected,
            parent=self
            )
        tlist._asset = self.asset
        self._childs.append(tlist)
        return tlist
    # }}}
    def _selectMarket(self, key, value):# {{{
        selected = list()
        for trade in self._trades:
            x = trade["market analytic"].get(key)
            if x == value:
                selected.append(trade)
        tlist = TradeList(
            name="- " + self.name + f" market-{key}-{value}",
            trades=selected,
            parent=self
            )
        tlist._asset = self.asset
        self._childs.append(tlist)
        return tlist
    # }}}
    def _selectRisk(self, key, value):# {{{
        selected = list()
        for trade in self._trades:
            x = trade["risk manager"].get(key)
            if x == value:
                selected.append(trade)
        tlist = TradeList(
            name="- " + self.name + f" risk-{key}-{value}",
            trades=selected,
            parent=self
            )
        tlist._asset = self.asset
        self._childs.append(tlist)
        return tlist
    # }}}
    def _selectRuler(self, key, value):# {{{
        selected = list()
        for trade in self._trades:
            x = trade["ruler"].get(key)
            if x == value:
                selected.append(trade)
        tlist = TradeList(
            name="- " + self.name + f" risk-{key}-{value}",
            trades=selected,
            parent=self
            )
        tlist._asset = self.asset
        self._childs.append(tlist)
        return tlist
    # }}}
    def _selectAdviser(self, key, value):# {{{
        selected = list()
        for trade in self._trades:
            x = trade["adviser"].get(key)
            if x == value:
                selected.append(trade)
        tlist = TradeList(
            name="- " + self.name + f" adviser-{key}-{value}",
            trades=selected,
            parent=self
            )
        tlist._asset = self.asset
        self._childs.append(tlist)
        return tlist
    # }}}
    def _selectPosition(self, key, value):# {{{
        selected = list()
        for trade in self._trades:
            x = trade["position"].get(key)
            if x == value:
                selected.append(trade)
        tlist = TradeList(
            name="- " + self.name + f" position-{key}-{value}",
            trades=selected,
            parent=self
            )
        tlist._asset = self.asset
        self._childs.append(tlist)
        return tlist
    # }}}
    @staticmethod  #save# {{{
    def save(trade_list, file_path=None):
        if file_path is None:
            file_path = trade_list.path  # default in parent dir
        obj = list()
        for trade in trade_list:
            trade_info_dict = Trade.toJSON(trade)
            obj.append(trade_info_dict)
        Cmd.saveJSON(obj, file_path)
        return True
    # }}}
    @staticmethod  #load# {{{
    def load(file_path, parent=None):
        name = Cmd.name(file_path, extension=False)
        info_list = Cmd.loadJSON(file_path)
        tlist = TradeList(name, parent=parent)
        for info in info_list:
            trade = Trade(info, parent=tlist)
            tlist.add(trade)
        return tlist
    # }}}
    @staticmethod  #delete# {{{
    def delete(tlist):
        path = tlist.path
        if not Cmd.isExist(path):
            # logger.warning(
            #     f"Can't delete TradeList: '{path}', file not found"
            #     )
            return False
        Cmd.delete(path)
        return True
    # }}}
    @property  #name# {{{
    def name(self):
        return self._name
    # }}}
    @property  #trades# {{{
    def trades(self):
        return self._trades
    # }}}
    @property  #count# {{{
    def count(self):
        return len(self._trades)
    # }}}
    @property  #asset# {{{
    def asset(self):
        return self._asset
    # }}}
    @property  #test# {{{
    def test(self):
        return self._test
    # }}}
    @property  #dir_path# {{{
    def dir_path(self):
        if self._test is not None:
            return self._test.dir_path
        else:
            assert False, "WTF???"
    # }}}
    @property  #path# {{{
    def path(self):
        path = Cmd.join(self.dir_path, "tlist.tl")
        return path
    # }}}
    def parent(self):# {{{
        return self._parent
    # }}}
    def add(self, trade: Trade) -> None:# {{{
        self._trades.append(trade)
        trade._parent = self
    # }}}
    def remove(self, trade: Trade) -> None:# {{{
        self._trades.remove(trade)
    # }}}
    def clear(self) -> None:# {{{
        self._trades.clear()
    # }}}
    def selectLong(self):# {{{
        selected = list()
        for trade in self._trades:
            if trade.isLong():
                selected.append(trade)
        child = self._createChild(selected, "long")
        return child
    # }}}
    def selectShort(self):# {{{
        selected = list()
        for trade in self._trades:
            if trade.isShort():
                selected.append(trade)
        child = self._createChild(selected, "short")
        return child
    # }}}
    def selectWin(self):# {{{
        selected = list()
        for trade in self._trades:
            if trade.isWin():
                selected.append(trade)
        child = self._createChild(selected, "win")
        return child
    # }}}
    def selectLoss(self):# {{{
        selected = list()
        for trade in self._trades:
            if trade.isLoss():
                selected.append(trade)
        child = self._createChild(selected, "loss")
        return child
    # }}}
    def selectBack(self):# {{{
        selected = list()
        for trade in self._trades:
            if trade.isBack():
                selected.append(trade)
        child = self._createChild(selected, "back")
        return child
    # }}}
    def selectForward(self):# {{{
        selected = list()
        for trade in self._trades:
            if trade.isForward():
                selected.append(trade)
        child = self._createChild(selected, "forward")
        return child
    # }}}
    def selectFilter(f):# {{{
        assert False
    # }}}
# }}}
