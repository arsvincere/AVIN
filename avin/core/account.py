#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================


@dataclass  #Operation# {{{
class Operation():
    class Direction(enum.Enum):# {{{
        UNDEFINE =     0
        BUY =          1
        SELL =         2
    # }}}
    signal: object
    dt: datetime
    direction: Direction
    asset: Asset
    lots: int
    price: float
    quantity: int
    amount: float
    commission: float
    broker_info: object=None

    def __str__(self):# {{{
        msk_dt = self.dt + MSK_TIME_DIF
        str_dt = msk_dt.strftime("%Y-%m-%d %H:%M")
        string = (
            f"{str_dt} {self.direction.name} {self.asset.ticker} "
            f"{self.quantity} * {self.price} = {self.amount} "
            f"+ {self.commission}"
            )
        return string
    # }}}
    @staticmethod  # toJSON{{{
    def toJSON(op) -> dict:
        obj = {
            "signal_id":  op.signal.ID,
            "dt":         str(op.dt),
            "direction":  str(op.direction),
            "asset":      Asset.toJSON(op.asset),
            "lots":       op.lots,
            "quantity":   op.quantity,
            "price":      op.price,
            "amount":     op.amount,
            "commission": op.commission,
            }
        return obj
    # }}}
    @staticmethod  # fromJSON{{{
    def fromJSON(obj):
        ID_dict = obj["asset"]
        assert eval(ID_dict["type"]) == Type.SHARE
        share = Share(ID_dict["ticker"])
        o = Operation(
            signal=     "????????????",
            dt=         datetime.fromisoformat(obj["dt"]),
            direction=  eval("Operation." + obj["direction"]),
            asset=      share,
            lots=       obj["lots"],
            quantity=   obj["quantity"],
            price=      obj["price"],
            amount=     obj["amount"],
            commission= obj["commission"],
            )
        return o
    # }}}
    def parent(self):# {{{
        return self.signal
    # }}}
# }}}
class Position():# {{{
    class Status(enum.Enum):# {{{
        UNDEFINE =     0
        OPEN =         1
        CLOSE =        2
    # }}}
    def __init__(self, signal, operation: Operation):# {{{
        self.__signal = signal
        self.__operations = [operation,]
        self.__status = Position.Status.OPEN
    # }}}
    def __writePositionInfo(self):# {{{
        if self.status != self.Status.CLOSE:
            raise PositionError("Запись результатов для незакрытой позиции")
        info = dict()
        info["result"] = self.result()
        info["percent"] = self.percent()
        info["holding_days"] = self.holdingDays()
        info["percent_per_day"] = self.percentPerDay()
        info["buy_amount"] = self.buyAmount()
        info["sell_amount"] = self.sellAmount()
        info["commission"] = self.sellCommission() + self.buyCommission()
        info["open_datetime"] = self.openDatetime()
        info["open_price"] = self.openPrice()
        info["close_datetime"] = self.closeDatetime()
        info["close_price"] = self.closePrice()
        self.__signal.info.setdefault("position", info)
    # }}}
    def __writeOperationsInfo(self):# {{{
        self.__signal.info.setdefault("operation", list())
        for op in self.operations:
            self.__signal.info["operation"].append(op)
    # }}}
    @property  #signal# {{{
    def signal(self):
        return self.__signal
    # }}}
    @property  #asset# {{{
    def asset(self):
        return self.__signal.asset
    # }}}
    @property  #status# {{{
    def status(self):
        return self.__status
    # }}}
    @property  #operations# {{{
    def operations(self):
        return self.__operations
    # }}}
    def parent(self):# {{{
        return self.__signal
    # }}}
    def add(self, operation):# {{{
        assert self.__status == Position.Status.OPEN
        self.__operations.append(operation)
        # Проверим не закрылась ли позиция
        if self.quantity() == 0:
            self.__status = Position.Status.CLOSE
            self.__writePositionInfo()
            self.__writeOperationsInfo()
    # }}}
    def lots(self):# {{{
        total = 0
        for op in self.__operations:
            if op.direction == Operation.Direction.BUY:
                total += op.lots
            elif op.direction == Operation.Direction.SELL:
                total -= op.lots
        return total
    # }}}
    def openPrice(self):# {{{
        return self.__operations[0].price
    # }}}
    def closePrice(self):# {{{
        assert self.__status == Position.Status.CLOSE
        return self.__operations[-1].price
    # }}}
    def openDatetime(self):# {{{
        return self.operations[0].dt
    # }}}
    def closeDatetime(self):# {{{
        assert self.__status == Position.Status.CLOSE
        return self.operations[-1].dt
    # }}}
    def quantity(self):# {{{
        total = 0
        for op in self.__operations:
            if op.direction == Operation.Direction.BUY:
                total += op.quantity
            elif op.direction == Operation.Direction.SELL:
                total -= op.quantity
        return total
    # }}}
    def buyQuantity(self):# {{{
        total = 0
        for op in self.operations:
            if op.direction == Operation.Direction.BUY:
                total += op.quantity
        return total
    # }}}
    def sellQuantity(self):# {{{
        total = 0
        for op in self.operations:
            if op.direction == Operation.Direction.SELL:
                total += op.quantity
        return total
    # }}}
    def amount(self):# {{{
        if self.__status == self.Status.CLOSE:
            return 0.0
        total = 0
        for op in self.operations:
            if op.direction == Operation.Direction.BUY:
                total += op.amount
            elif op.direction == Operation.Direction.SELL:
                total -= op.amount
        return total
    # }}}
    def buyAmount(self):# {{{
        total = 0
        for op in self.operations:
            if op.direction == Operation.Direction.BUY:
                total += op.amount
        return total
    # }}}
    def sellAmount(self):# {{{
        total = 0
        for op in self.operations:
            if op.direction == Operation.Direction.SELL:
                total += op.amount
        return total
    # }}}
    def buyCommission(self):# {{{
        total = 0
        for op in self.operations:
            if op.direction == Operation.Direction.BUY:
                total += op.commission
        return total
    # }}}
    def sellCommission(self):# {{{
        total = 0
        for op in self.operations:
            if op.direction == Operation.Direction.SELL:
                total += op.commission
        return total
    # }}}
    def average(self):# {{{
        return self.amount() / self.quantity()
    # }}}
    def averageBuy(self):# {{{
        if self.buyQuantity() == 0:
            return 0.0
        else:
            return self.buyAmount() / self.buyQuantity()
    # }}}
    def averageSell(self):# {{{
        if self.sellQuantity() == 0:
            return 0.0
        else:
            return self.sellAmount() / self.sellQuantity()
    # }}}
    def result(self):# {{{
        if self.__status != self.Status.CLOSE:
            raise PositionError("Вызов результата для незакрытой позиции")
        result = (self.sellAmount() - self.buyAmount() -
                self.buyCommission() - self.sellCommission())
        return round(result, 2)
    # }}}
    def holdingDays(self):# {{{
        if self.__status != self.Status.CLOSE:
            raise PositionError("Вызов времени удержания для незакрытой позиции")
        opn_dt = self.operations[0].dt
        cls_dt = self.operations[-1].dt
        holding = cls_dt - opn_dt + ONE_DAY
        return holding.days
    # }}}
    def percent(self):# {{{
        if self.__status != self.Status.CLOSE:
            raise PositionError("Вызов результата в процентах для незакрытой позиции")
        persent = self.result() / self.buyAmount() * 100
        return round(persent, 2)
    # }}}
    def percentPerDay(self):# {{{
        if self.__status != self.Status.CLOSE:
            raise PositionError("Вызов результата в процентах для незакрытой позиции")
        persent = self.result() / self.buyAmount() * 100
        holding = self.holdingDays()
        persent_per_day = persent / holding
        return round(persent_per_day, 2)
    # }}}
# }}}
class Portfolio():# {{{
    @dataclass  #Cash# {{{
    class Cash():
        currency: str
        value: float
        block: float
    # }}}
    @dataclass  #Share# {{{
    class Share():
        share: Share
        balance: int
        block: int
        ID: str
        full_responce: None
    # }}}
    @dataclass  #Bound# {{{
    class Bound(): pass
    # }}}
    @dataclass  #Future# {{{
    class Future: pass
    # }}}
    @dataclass  #Option# {{{
    class Option: pass
    # }}}
    def __init__(self, cash, shares, bounds, futures, options):# {{{
        self.cash = cash
        self.shares = shares
        self.bounds = bounds
        self.futures = futures
        self.options = options
        # depricate
        self.positions = list()
        self.rub = 0.0
        self.block = 0.0
        self.free = 0.0
    # }}}
    def virtualSetMoney(self, money):# {{{
        self.rub = money
        self.free = money * 5
        self.block = 0.0
    # }}}
    def add(self, position):# {{{
        self.positions.append(position)
    # }}}
    def remove(self, position):# {{{
        for pos in self.positions:
            if id(pos) == id(position):
                assert pos.status == "closed"
                self.positions.remove(pos)
                return True
        raise PortfolioError("Такой позиции нет в портфеле: {0}".format(
                             position))
        return False
    # }}}
# }}}
