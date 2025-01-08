#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

from __future__ import annotations

import pandas as pd

from avin.core.trade import Trade, TradeList
from avin.utils import logger


class Summary:
    def __init__(self, trade_list: TradeList):  # {{{
        logger.debug(f"{self.__class__.__name__}.__init__()")

        self.__trade_list = trade_list
        self.__df = self.calculate(trade_list)

    # }}}
    def __str__(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__str__()")

        return str(self.__df)

    # }}}

    def data(self) -> pd.DataFrame:  # {{{
        return self.__df

    # }}}

    @classmethod  # header  # {{{
    def header(cls) -> list[str]:
        header = list()
        header.append("name")
        for column_name in cls.__FUNCTIONS:
            header.append(column_name)
        return header

    # }}}
    @classmethod  # calculate  # {{{
    def calculate(cls, trade_list: TradeList) -> pd.DataFrame:
        has_parent = trade_list.parent_list is not None

        dct = dict()
        dct["name"] = trade_list.subname if has_parent else trade_list.name
        results = Summary.__getResults(trade_list)

        for column, function in Summary.__FUNCTIONS.items():
            value = round(function(results), 2)
            dct[column] = value

        df = pd.DataFrame([dct])
        for tl in trade_list.childs:
            df_child = Summary.calculate(tl)
            df = pd.concat([df, df_child], ignore_index=True)

        return df

    # }}}
    @classmethod  # percentProfitable  # {{{
    def percentProfitable(cls, trade_list: TradeList) -> float:
        logger.debug(f"{self.__class__.__name__}.percentProfitable()")

        results = Summary.__getResults(trade_list)
        percent = Summary.__percentProfitable(results)

        return round(percent, 2)

    # }}}
    @classmethod  # save  # {{{
    def save(cls, summary: Summary, file_path: str) -> None:
        logger.debug(f"{self.__class__.__name__}.__save()")

        summary.__df.to_csv(file_path, sep=";")

    # }}}

    @staticmethod  # __grossProfit# {{{
    def __grossProfit(results: list) -> float:
        """Возвращает валовую прибыль всех <results>"""

        value = 0.0
        for i in results:
            if i > 0.0:
                value += i
        return value

    # }}}
    @staticmethod  # __grossLoss# {{{
    def __grossLoss(results: list) -> float:
        """Возвращает валовый убыток всех <results>"""

        value = 0.0
        for i in results:
            if i < 0.0:
                value += i
        return value

    # }}}
    @staticmethod  # __totalNetProfit# {{{
    def __totalNetProfit(results: list) -> float:
        """Чистая прибыль всех <results>"""

        value = 0.0
        for i in results:
            value += i
        return round(value, 2)

    # }}}
    @staticmethod  # __totalTrades# {{{
    def __totalTrades(results: list) -> int:
        """Общее количество трейдов"""

        return len(results)

    # }}}
    @staticmethod  # __winningTrades# {{{
    def __winningTrades(results: list) -> int:
        """Количество выигранных трейдов"""
        value = 0
        for i in results:
            if i > 0.0:
                value += 1
        return value

    # }}}
    @staticmethod  # __losingTrades# {{{
    def __losingTrades(results: list) -> int:
        """Количество проигранных трейдов"""

        value = 0
        for i in results:
            if i < 0.0:
                value += 1
        return value

    # }}}
    @staticmethod  # __percentProfitable# {{{
    def __percentProfitable(results: list) -> float:
        """Процент выигрышей"""

        win = Summary.__winningTrades(results)
        total = Summary.__totalTrades(results)
        if total == 0:
            return 0
        else:
            return win / total * 100

    # }}}
    @staticmethod  # __percentUnprofitable# {{{
    def __percentUnprofitable(results: list) -> float:
        """Процент проигрышей"""

        loss = Summary.__losingTrades(results)
        total = Summary.__totalTrades(results)
        if total == 0:
            return 0
        else:
            return loss / total * 100

    # }}}
    @staticmethod  # __largestWin# {{{
    def __largestWin(results: list) -> float:
        """Наибольший выигрыш"""

        if len(results) == 0:
            return 0.0
        maximum = max(results)
        return max(maximum, 0.0)

    # }}}
    @staticmethod  # __largestLoss# {{{
    def __largestLoss(results: list) -> float:
        """Наибольший проигрыш"""

        if len(results) == 0:
            return 0.0
        minimum = min(results)
        return min(minimum, 0.0)

    # }}}
    @staticmethod  # __averageWin# {{{
    def __averageWin(results: list) -> float:
        """Средний выигрыш"""

        win_count = Summary.__winningTrades(results)
        if win_count == 0:
            return 0.0
        else:
            return Summary.__grossProfit(results) / win_count

    # }}}
    @staticmethod  # __averageLoss# {{{
    def __averageLoss(results: list) -> float:
        """Средний проигрыш"""

        loss_count = Summary.__losingTrades(results)
        if loss_count == 0:
            return 0.0
        else:
            return Summary.__grossLoss(results) / loss_count

    # }}}
    @staticmethod  # __averageTrade# {{{
    def __averageTrade(results: list) -> float:
        """Средний результат трейда"""

        count = Summary.__totalTrades(results)
        if count == 0:
            return 0
        else:
            return Summary.__totalNetProfit(results) / count

    # }}}
    @staticmethod  # __maxWinSeries# {{{
    def __maxWinSeries(results: list) -> int:
        """Максимальное количество последовательных выигрышей"""

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
    @staticmethod  # __maxLossSeries# {{{
    def __maxLossSeries(results: list) -> int:
        """Максимальное количество последовательных проигрышей"""

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
    @staticmethod  # __ratio# {{{
    def __ratio(results: list) -> float:
        """Отношение среднего выигрыша к среднему проигрышу"""

        # avg_loss = Summary.__averageLoss(results)
        # if avg_loss == 0:
        #     return 0.0
        # else:
        #     return abs(Summary.__averageWin(results) / avg_loss)

        """Отношение общей прибыли к общему убытку"""
        gross_loss = Summary.__grossLoss(results)
        if gross_loss == 0:
            return 100.0
        else:
            return abs(Summary.__grossProfit(results) / gross_loss)

    # }}}
    @staticmethod  # __getResults# {{{
    def __getResults(tlist: TradeList) -> list[float]:
        """Возвращает список финансовых результатов трейдов

        Учитываются только закрытые трейды
        """

        results = list()
        for trade in tlist.trades:
            if trade.isBlocked():
                continue
            if trade.status == Trade.Status.CLOSED:
                results.append(trade.result())

        return results

    # }}}
    __FUNCTIONS = {  # {{{
        # Column: Function
        "profit": __totalNetProfit,
        "%": __percentProfitable,
        "trades": __totalTrades,
        "win": __winningTrades,
        "loss": __losingTrades,
        "w-seq": __maxWinSeries,
        "l-seq": __maxLossSeries,
        "gross profit": __grossProfit,
        "gross loss": __grossLoss,
        "ratio": __ratio,
        "avg": __averageTrade,
        "avg win": __averageWin,
        "avg loss": __averageLoss,
        "max win": __largestWin,
        "max loss": __largestLoss,
    }
    # }}}


if __name__ == "__main__":
    ...
