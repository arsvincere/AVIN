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
        self.__summary = self.__calculate(trade_list)

    # }}}
    def __str__(self):  # {{{
        return str(self.data_frame)

    # }}}

    @property  # data_frame   # {{{
    def data_frame(self) -> pd.DataFrame:
        full_df = pd.DataFrame([self.__summary])

        for tl in self.__trade_list.childs:
            child_summary = self.__calculate(tl)
            child_df = pd.DataFrame([child_summary])
            full_df = pd.concat([full_df, child_df], ignore_index=True)

        return full_df

    # }}}
    @property  # name   # {{{
    def name(self) -> float:
        return self.__summary["name"]

    # }}}
    @property  # profit   # {{{
    def profit(self) -> float:
        return self.__summary["profit"]

    # }}}
    @property  # accuracy   # {{{
    def accuracy(self) -> float:
        return self.__summary["%"]

    # }}}
    @property  # trades   # {{{
    def trades(self) -> float:
        return self.__summary["trades"]

    # }}}
    @property  # win   # {{{
    def win(self) -> float:
        return self.__summary["win"]

    # }}}
    @property  # loss   # {{{
    def loss(self) -> float:
        return self.__summary["loss"]

    # }}}
    @property  # ratio   # {{{
    def ratio(self) -> float:
        return self.__summary["ratio"]

    # }}}
    @property  # avg   # {{{
    def avg(self) -> float:
        return self.__summary["avg"]

    # }}}
    @property  # gross_profit   # {{{
    def gross_profit(self) -> float:
        return self.__summary["gross profit"]

    # }}}
    @property  # gross_loss   # {{{
    def gross_loss(self) -> float:
        return self.__summary["gross loss"]

    # }}}
    @property  # wseq   # {{{
    def wseq(self) -> float:
        return self.__summary["w-seq"]

    # }}}
    @property  # lseq   # {{{
    def lseq(self) -> float:
        return self.__summary["l-seq"]

    # }}}
    @property  # avg_win   # {{{
    def avg_win(self) -> float:
        return self.__summary["avg win"]

    # }}}
    @property  # avg_loss   # {{{
    def avg_loss(self) -> float:
        return self.__summary["avg loss"]

    # }}}
    @property  # max_win   # {{{
    def max_win(self) -> float:
        return self.__summary["max win"]

    # }}}
    @property  # max_loss   # {{{
    def max_loss(self) -> float:
        return self.__summary["max loss"]

    # }}}

    @classmethod  # header  # {{{
    def header(cls) -> list[str]:
        logger.debug(f"{cls.__name__}.header()")

        header = list()
        header.append("name")
        for column_name in cls.__FUNCTIONS:
            header.append(column_name)

        return header

    # }}}
    @classmethod  # percentProfitable  # {{{
    def percentProfitable(cls, trade_list: TradeList) -> float:
        logger.debug(f"{cls.__name__}.percentProfitable()")

        results = Summary.__getResults(trade_list)
        percent = Summary.__percentProfitable(results)

        return round(percent, 2)

    # }}}

    @classmethod  # save  # {{{
    def save(cls, summary: Summary, file_path: str) -> None:
        logger.debug(f"{self.__class__.__name__}.__save()")

        df = summary.data_frame
        df.to_csv(file_path, sep=";")

    # }}}

    def __calculate(self, trade_list: TradeList) -> dict:  # {{{
        has_parent = trade_list.parent_list is not None

        summary = dict()
        summary["name"] = (
            trade_list.subname if has_parent else trade_list.name
        )
        results = Summary.__getResults(trade_list)

        for column, function in Summary.__FUNCTIONS.items():
            value = round(function(results), 2)
            summary[column] = value

        return summary

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
        "ratio": __ratio,
        "avg": __averageTrade,
        "gross profit": __grossProfit,
        "gross loss": __grossLoss,
        "w-seq": __maxWinSeries,
        "l-seq": __maxLossSeries,
        "avg win": __averageWin,
        "avg loss": __averageLoss,
        "max win": __largestWin,
        "max loss": __largestLoss,
    }
    # }}}


if __name__ == "__main__":
    ...
