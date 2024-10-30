#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

from __future__ import annotations

from datetime import datetime
from typing import Iterator, Optional

from avin.keeper import Keeper
from avin.utils import logger

# TODO: save, load, delete from db in class Keeper


class Transaction:
    def __init__(  # {{{
        self,
        order_id: str,
        dt: datetime,
        quantity: int,
        price: float,
        broker_id: str,
    ):
        self.order_id = order_id
        self.dt = dt
        self.quantity = quantity
        self.price = price
        self.broker_id = broker_id

    # }}}
    def __str__(self) -> str:  # {{{
        string = (
            f"Transaction order_id={self.order_id} dt={self.dt} "
            f"quantity={self.quantity} price={self.price}"
        )
        return string

    # }}}
    @classmethod  # save  # {{{
    async def save(cls, transaction: Transaction) -> None:
        await Keeper.add(transaction)

    # }}}
    @classmethod  # load  # {{{
    async def load(cls, order_id: str) -> list[Transaction]:
        transactions = await Keeper.get(cls, order_id=order_id)
        return transactions

    # }}}
    @classmethod  # delete  # {{{
    async def delete(cls, transaction: Transaction) -> None:
        await Keeper.delete(transaction)

    # }}}


class TransactionList:
    def __init__(self, transactions: Optional[list] = None):  # {{{
        logger.debug(f"{self.__class__.__name__}.__init__()")

        self.__transactions = transactions if transactions else list()

    # }}}
    def __str__(self):  # {{{
        return f"TransactionList={self.__transactions}"

    # }}}
    def __iter__(self) -> Iterator:  # {{{
        return iter(self.__transactions)

    # }}}
    def __contains__(self, transaction) -> bool:  # {{{
        return transaction in self.__transactions

    # }}}
    def __len__(self) -> int:  # {{{
        return len(self.__transactions)

    # }}}
    @property  # first  # {{{
    def first(self) -> Transaction:
        assert len(self.__transactions)

        return self.__transactions[0]

    # }}}
    @property  # last  # {{{
    def last(self) -> Transaction:
        assert len(self.__transactions)

        return self.__transactions[-1]

    # }}}
    @property  # transactions  # {{{
    def transactions(self) -> list[Transaction]:
        return self.__transactions

    @transactions.setter
    def transactions(self, transactions: list[Transaction]) -> None:
        self.__transactions = transactions

    # }}}
    def add(self, transaction: Transaction) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.add()")

        assert isinstance(transaction, Transaction)
        if transaction not in self.__transactions:
            self.__transactions.append(transaction)
            return

        logger.warning(f"{transaction} already in list '{self}'")

    # }}}
    def remove(self, transaction: Transaction) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.remove()")

        try:
            self.__transactions.remove(transaction)
        except ValueError:
            logger.exception(
                f"TransactionList.remove(transaction) failed: "
                f"{transaction}' not in list",
            )

    # }}}
    def clear(self) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.clear()")

        self.__transactions.clear()

    # }}}
    def quantity(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.quantity()")

        total = 0
        for t in self.__transactions:
            total += t.quantity

        return total

    # }}}
    def amount(self) -> float:  # {{{
        logger.debug(f"{self.__class__.__name__}.amount()")

        total = 0
        for t in self.__transactions:
            amount = t.price * t.quantity
            total += amount

        return total

    # }}}
    def average(self) -> float:  # {{{
        logger.debug(f"{self.__class__.__name__}.average()")

        if self.quantity() == 0:
            return 0.0

        return self.amount() / self.quantity()


# }}}


if __name__ == "__main__":
    ...
