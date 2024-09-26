#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

""" Doc """

from __future__ import annotations

class Report():# {{{
    """ Const """# {{{
    # FUNCTIONS = None  # инициализируется внизу класса
    # }}}
    def __init__(self, test: Test):# {{{
        self._test = test
        self.__df = Report.calculate(test.tlist)
    # }}}
    def __str__(self):# {{{
        return str(self.__df)
    # }}}
    @staticmethod  #_grossProfit# {{{
    def _grossProfit(results: list) -> float:
        """ Возвращает валовую прибыль всех <results> """
        value = 0.0
        for i in results:
            if i > 0.0:
                value += i
        return value
    # }}}
    @staticmethod  #_grossLoss# {{{
    def _grossLoss(results: list) -> float:
        """ Возвращает валовый убыток всех <results> """
        value = 0.0
        for i in results:
            if i < 0.0:
                value += i
        return value
    # }}}
    @staticmethod  #_totalNetProfit# {{{
    def _totalNetProfit(results: list) -> float:
        value = 0.0
        for i in results:
            value += i
        return round(value, 2)
    # }}}
    @staticmethod  #_totalTrades# {{{
    def _totalTrades(results: list) -> int:
        return len(results)
    # }}}
    @staticmethod  #_winningTrades# {{{
    def _winningTrades(results: list) -> int:
        value = 0
        for i in results:
            if i > 0.0:
                value += 1
        return value
    # }}}
    @staticmethod  #_losingTrades# {{{
    def _losingTrades(results: list) -> int:
        value = 0
        for i in results:
            if i < 0.0:
                value += 1
        return value
    # }}}
    @staticmethod  #_percentProfitable# {{{
    def _percentProfitable(results: list) -> float:
        win = Report._winningTrades(results)
        total = Report._totalTrades(results)
        if total == 0:
            return 0
        else:
            return win / total * 100
    # }}}
    @staticmethod  #_percentUnprofitable# {{{
    def _percentUnprofitable(results: list) -> float:
        loss = Report._losingTrades(results)
        total = Report._totalTrades(results)
        if total == 0:
            return 0
        else:
            return loss / total * 100
    # }}}
    @staticmethod  #_largestWin# {{{
    def _largestWin(results: list) -> float:
        if len(results) == 0:
            return 0.0
        maximum = max(results)
        return max(maximum, 0.0)
    # }}}
    @staticmethod  #_largestLoss# {{{
    def _largestLoss(results: list) -> float:
        if len(results) == 0:
            return 0.0
        minimum = min(results)
        return min(minimum, 0.0)
    # }}}
    @staticmethod  #_averageWin# {{{
    def _averageWin(results: list) -> float:
        win_count = Report._winningTrades(results)
        if win_count == 0:
            return 0.0
        else:
            return Report._grossProfit(results) / win_count
    # }}}
    @staticmethod  #_averageLoss# {{{
    def _averageLoss(results: list) -> float:
        loss_count = Report._losingTrades(results)
        if loss_count == 0:
            return 0.0
        else:
            return Report._grossLoss(results) / loss_count
    # }}}
    @staticmethod  #_averageTrade# {{{
    def _averageTrade(results: list) -> float:
        count = Report._totalTrades(results)
        if count == 0:
            return 0
        else:
            return Report._totalNetProfit(results) / count
    # }}}
    @staticmethod  #_maxWinSeries# {{{
    def _maxWinSeries(results: list) -> int:
        value = 0
        series = 0
        for i in results:
            if i >= 0.0:
                series += 1
            else:
                series = 0
            value = max(value, series)
        return value
    # }}}
    @staticmethod  #_maxLossSeries# {{{
    def _maxLossSeries(results: list) -> int:
        value = 0
        series = 0
        for i in results:
            if i < 0.0:
                series += 1
            else:
                series = 0
            value = max(value, series)
        return value
    # }}}
    @staticmethod  #_ratio# {{{
    def _ratio(results: list) -> float:
        avg_loss = Report._averageLoss(results)
        if avg_loss == 0:
            return 0.0
        else:
            return abs(Report._averageWin(results) / avg_loss)
    # }}}
    @staticmethod  #_getResults# {{{
    def _getResults(tlist: TradeList) -> list[float]:
        results = list()
        for trade in tlist.trades:
            if not trade.isBlocked():
                results.append(trade.result)
        return results
    # }}}
    @staticmethod  #save# {{{
    def save(report, path) -> bool:
        report.__df.to_csv(path, sep=";")
        return True
    # }}}
    @staticmethod  #load# {{{
    def load(file_path: str, parent):
        report = Report(parent)
        report.__df = pd.read_csv(file_path, sep=";")
        return report
    # }}}
    @staticmethod  #delete# {{{
    def delete(report):
        path = report.path
        if not Cmd.isExist(path):
            logger.warning(f"Can't delete Report: '{path}', file not found")
            return False
        Cmd.delete(path)
        return True
    # }}}
    @staticmethod  #getHeader# {{{
    def getHeader() -> list[str]:
        header = list()
        header.append("name")
        for column_name in Report.FUNCTIONS:
            header.append(column_name)
        return header
    # }}}
    @staticmethod  #calculate# {{{
    def calculate(tlist: TradeList) -> pd.DataFrame:
        dct = dict()
        dct["name"] = tlist.name
        results = Report._getResults(tlist)
        for column, function in Report.FUNCTIONS.items():
            value = round(function(results), 2)
            dct[column] = value
        df = pd.DataFrame([dct])
        for tl in tlist._childs:
            df_child = Report.calculate(tl)
            df = pd.concat([df, df_child], ignore_index=True)
        return df
    # }}}
    @property  #path# {{{
    def path(self):
        path = Cmd.join(self._test.dir_path, "report.csv")
        return path
    # }}}
    def parent(self):# {{{
        return self._parent
    # }}}
    def update(self):# {{{
        self.__df = Report.calculate(self._parent.tlist)
    # }}}
    def clear(self):# {{{
        indexes = self.__df.index
        self.__df.drop(indexes)
    # }}}
    FUNCTIONS = {# {{{
        # Column            Function
        "profit":           _totalNetProfit,
        "%":                _percentProfitable,
        "trades":           _totalTrades,
        "win":              _winningTrades,
        "loss":             _losingTrades,
        "w-seq":            _maxWinSeries,
        "l-seq":            _maxLossSeries,
        "avg":              _averageTrade,
        "avg win":          _averageWin,
        "avg loss":         _averageLoss,
        "max win":          _largestWin,
        "max loss":         _largestLoss,
        "gross profit":     _grossProfit,
        "gross loss":       _grossLoss,
        "ratio":            _ratio,
        }
    # }}}
# Report.FUNCTIONS ={{{
#     # Column            Function
#     "profit":           Report._totalNetProfit,
#     "%":                Report._percentProfitable,
#     "trades":           Report._totalTrades,
#     "win":              Report._winningTrades,
#     "loss":             Report._losingTrades,
#     "w-seq":            Report._maxWinSeries,
#     "l-seq":            Report._maxLossSeries,
#     "avg":              Report._averageTrade,
#     "avg win":          Report._averageWin,
#     "avg loss":         Report._averageLoss,
#     "max win":          Report._largestWin,
#     "max loss":         Report._largestLoss,
#     "gross profit":     Report._grossProfit,
#     "gross loss":       Report._grossLoss,
#     "ratio":            Report._ratio,
#     }
    # }}}
# }}}

if __name__ == "__main__":
    ...

