#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

from __future__ import annotations
import abc
from avin.utils import now

class Uid(metaclass=abc.ABCMeta):
    @classmethod  #newUid# {{{
    def newUid(cls, obj: Signal | Order | Operation | Position):
        assert False
        # ???? подумать
        uid = f"{obj.__class__.__name__}-{now()}???"

    # }}}

"""
наверное имени класса и даты (включая микросекунды) достаточно для
идентификации объекта.
Внутри идентификатора они хранятся как два поля
    класс должен еще определять метод ==

    имея поле дт можно потом фильтровать объекты(события) по дням месяцам
    и тп...
    Хотя интерфейс получается уже не согласованный. Это тогда не совсем юид
    это уже база данных какая то.

    Uid.get(Position, begin, eng)
    Uid.get(Operation, begin, eng)

    Скорее тогда Keeper
    Keeper.get(Position, begin, eng)
    Keeper.get(Operation, begin, eng)

    Keeper.newUid(pos) -> uid
    Keeper.newUid(order) -> uid
    Да так логичнее.
    И потом класс кипер может сохраняя интерфейс переделать реализацию
        на БД




"""
