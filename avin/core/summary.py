#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

from __future__ import annotations

import pandas as pd

# TODO: .data_frame...
# возвращает результат как дата фрейм... надо сделать методом или свойством
# и плюс отдельные функции - вычисление каждого отдельного параметра.
# или нет... вычисляет пусть все таки в df...
# или нет... пусть на лету вычисляет...
# короче это уже другой вопрос.
# Суть ближайшего изменение - доступ ко всему саммари как к ДФ
# и доступ к каждой отдельно колонке через соответствующую функцию.


# TODO:
# и вообще саммари это реал тайм объект над трейд листом
# или еще вернее - это то что трейд лист может вернуть..
# да! Summary относится к трейд листу а не к тесту!
# Подумай об этом еще.. попробуй в отдельной ветке...


class Summary:
    def __init__(self, test: Test):  # {{{
        self._test = test
        self.__df = Summary.calculate(test.trade_list)

    # }}}
    def __str__(self):  # {{{
        return str(self.__df)

    # }}}

    @staticmethod  # save# {{{
    def save(report, path) -> bool:
        report.__df.to_csv(path, sep=";")
        return True

    # }}}
    @staticmethod  # load# {{{
    def load(file_path: str, parent):
        report = Summary(parent)
        report.__df = pd.read_csv(file_path, sep=";")
        return report

    # }}}
    @staticmethod  # delete# {{{
    def delete(report):
        path = report.path
        if not Cmd.isExist(path):
            logger.warning(f"Can't delete Summary: '{path}', file not found")
            return False
        Cmd.delete(path)
        return True

    # }}}
    @staticmethod  # getHeader# {{{
    def getHeader() -> list[str]:
        header = list()
        header.append("name")
        for column_name in Summary.__FUNCTIONS:
            header.append(column_name)
        return header

    # }}}
    @staticmethod  # calculate# {{{
    def calculate(tlist: TradeList) -> pd.DataFrame:
        dct = dict()
        dct["name"] = tlist.name
        results = Summary._getResults(tlist)

        for column, function in Summary.__FUNCTIONS.items():
            value = round(function(results), 2)
            dct[column] = value

        df = pd.DataFrame([dct])
        for tl in tlist.childs:
            df_child = Summary.calculate(tl)
            df = pd.concat([df, df_child], ignore_index=True)

        return df

    # }}}

    def update(self):  # {{{
        # TODO: вообще косяк с название метода...
        # update - это из серии save load delete update
        # это про обновление объекта на диске
        # здесь же пересчет recalculate или просто
        # calculate нужно назвать...
        assert False, "пересделать"

    # }}}
    def clear(self):  # {{{
        indexes = self.__df.index
        self.__df.drop(indexes)

    # }}}

    @staticmethod  # _grossProfit# {{{
    def _grossProfit(results: list) -> float:
        """Возвращает валовую прибыль всех <results>"""
        value = 0.0
        for i in results:
            if i > 0.0:
                value += i
        return value

    # }}}
    @staticmethod  # _grossLoss# {{{
    def _grossLoss(results: list) -> float:
        """Возвращает валовый убыток всех <results>"""
        value = 0.0
        for i in results:
            if i < 0.0:
                value += i
        return value

    # }}}
    @staticmethod  # _totalNetProfit# {{{
    def _totalNetProfit(results: list) -> float:
        value = 0.0
        for i in results:
            value += i
        return round(value, 2)

    # }}}
    @staticmethod  # _totalTrades# {{{
    def _totalTrades(results: list) -> int:
        return len(results)

    # }}}
    @staticmethod  # _winningTrades# {{{
    def _winningTrades(results: list) -> int:
        value = 0
        for i in results:
            if i > 0.0:
                value += 1
        return value

    # }}}
    @staticmethod  # _losingTrades# {{{
    def _losingTrades(results: list) -> int:
        value = 0
        for i in results:
            if i < 0.0:
                value += 1
        return value

    # }}}
    @staticmethod  # _percentProfitable# {{{
    def _percentProfitable(results: list) -> float:
        win = Summary._winningTrades(results)
        total = Summary._totalTrades(results)
        if total == 0:
            return 0
        else:
            return win / total * 100

    # }}}
    @staticmethod  # _percentUnprofitable# {{{
    def _percentUnprofitable(results: list) -> float:
        loss = Summary._losingTrades(results)
        total = Summary._totalTrades(results)
        if total == 0:
            return 0
        else:
            return loss / total * 100

    # }}}
    @staticmethod  # _largestWin# {{{
    def _largestWin(results: list) -> float:
        if len(results) == 0:
            return 0.0
        maximum = max(results)
        return max(maximum, 0.0)

    # }}}
    @staticmethod  # _largestLoss# {{{
    def _largestLoss(results: list) -> float:
        if len(results) == 0:
            return 0.0
        minimum = min(results)
        return min(minimum, 0.0)

    # }}}
    @staticmethod  # _averageWin# {{{
    def _averageWin(results: list) -> float:
        win_count = Summary._winningTrades(results)
        if win_count == 0:
            return 0.0
        else:
            return Summary._grossProfit(results) / win_count

    # }}}
    @staticmethod  # _averageLoss# {{{
    def _averageLoss(results: list) -> float:
        loss_count = Summary._losingTrades(results)
        if loss_count == 0:
            return 0.0
        else:
            return Summary._grossLoss(results) / loss_count

    # }}}
    @staticmethod  # _averageTrade# {{{
    def _averageTrade(results: list) -> float:
        count = Summary._totalTrades(results)
        if count == 0:
            return 0
        else:
            return Summary._totalNetProfit(results) / count

    # }}}
    @staticmethod  # _maxWinSeries# {{{
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
    @staticmethod  # _maxLossSeries# {{{
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
    @staticmethod  # _ratio# {{{
    def _ratio(results: list) -> float:
        avg_loss = Summary._averageLoss(results)
        if avg_loss == 0:
            return 0.0
        else:
            return abs(Summary._averageWin(results) / avg_loss)

    # }}}
    @staticmethod  # _getResults# {{{
    def _getResults(tlist: TradeList) -> list[float]:
        results = list()
        for trade in tlist.trades:
            if not trade.isBlocked():
                results.append(trade.result())
        return results

    # }}}
    __FUNCTIONS = {  # {{{
        # Column: Function
        "profit": _totalNetProfit,
        "%": _percentProfitable,
        "trades": _totalTrades,
        "win": _winningTrades,
        "loss": _losingTrades,
        "w-seq": _maxWinSeries,
        "l-seq": _maxLossSeries,
        "avg": _averageTrade,
        "avg win": _averageWin,
        "avg loss": _averageLoss,
        "max win": _largestWin,
        "max loss": _largestLoss,
        "gross profit": _grossProfit,
        "gross loss": _grossLoss,
        "ratio": _ratio,
    }
    # }}}


# Summary.__FUNCTIONS ={{{
#     # Column            Function
#     "profit":           Summary._totalNetProfit,
#     "%":                Summary._percentProfitable,
#     "trades":           Summary._totalTrades,
#     "win":              Summary._winningTrades,
#     "loss":             Summary._losingTrades,
#     "w-seq":            Summary._maxWinSeries,
#     "l-seq":            Summary._maxLossSeries,
#     "avg":              Summary._averageTrade,
#     "avg win":          Summary._averageWin,
#     "avg loss":         Summary._averageLoss,
#     "max win":          Summary._largestWin,
#     "max loss":         Summary._largestLoss,
#     "gross profit":     Summary._grossProfit,
#     "gross loss":       Summary._grossLoss,
#     "ratio":            Summary._ratio,
#     }
# }}}


if __name__ == "__main__":
    ...
