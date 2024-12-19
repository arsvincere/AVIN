#!/usr/bin/env python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

import bisect
import os
from datetime import date, datetime, time, timedelta, timezone
from decimal import Decimal

from avin.utils.cmd import Cmd

# alias
Date = date
Time = time
DateTime = datetime
TimeDelta = timedelta
TimeZone = timezone


def now():  # {{{
    return datetime.now(timezone.utc)


# }}}
def round_price(price: float, min_price_step: float):  # {{{
    p = Decimal(price)
    p -= p % Decimal(min_price_step)
    return float(p)


# }}}
def binary_search(seq, x, key=None):  # {{{
    left = 0
    right = len(seq) - 1
    while left <= right:
        mid = (right - left) // 2 + left
        mid_val = seq[mid] if key is None else key(seq[mid])
        if x == mid_val:
            return mid
        if x < mid_val:
            right = mid - 1
        else:
            left = mid + 1
    return None


# }}}
def find_left(seq, x, key=None):  # {{{
    """Возвращает индекс элемента меньше или равного 'x'
    Если 'x', меньше самого левого элемента в векторе, возвращает None
    """
    i = bisect.bisect_right(seq, x, key=key)
    if i:
        return i - 1
    return None


# }}}
def find_right(seq, x, key=None):  # {{{
    """Возвращает индекс элемента больше или равного 'x'
    Если 'x', больше самого правого элемента в векторе, возвращает None
    """
    i = bisect.bisect_left(seq, x, key=key)
    if i != len(seq):
        return i
    return None


# }}}
def encode_json(obj):  # {{{
    assert False
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    if isinstance(obj, avin.core.TimeFrame):
        return str(obj)
    if isinstance(obj, enum.Enum):
        return str(obj)
    if isinstance(obj, (avin.core.Asset)):
        return avin.core.Asset.toJSON(obj)


# }}}
def decode_json(obj):  # {{{
    assert False
    for k, v in obj.items():
        if isinstance(v, str) and "+00:00" in v:
            obj[k] = datetime.fromisoformat(obj[k])
        if k == "timeframe_list":
            tmp = list()
            for string in obj["timeframe_list"]:
                timeframe = avin.core.TimeFrame(string)
                tmp.append(timeframe)
            obj["timeframe_list"] = tmp
        if k == "timeframe":
            obj["timeframe"] = avin.core.TimeFrame(obj["timeframe"])
        if k == "asset":
            obj["asset"] = avin.core.Asset.fromJSON(obj["asset"])
        if isinstance(v, str) and "Type.SHORT" in v:
            obj[k] = avin.core.Signal.Type.SHORT
        if isinstance(v, str) and "Type.LONG" in v:
            obj[k] = avin.core.Signal.Type.LONG
    return obj


# }}}
def code_counter(dir_path):  # {{{
    count_files = 0
    count_str = 0
    for root, _, files in os.walk(dir_path):
        for file in files:
            if file.endswith(".py"):
                file_path = Cmd.path(root, file)
                text = Cmd.loadText(file_path)
                count_str += len(text)
                count_files += 1
            if file.endswith(".sql"):
                file_path = Cmd.path(root, file)
                text = Cmd.loadText(file_path)
                count_str += len(text)
                count_files += 1
    return count_files, count_str


# }}}
def ask_user(message: str) -> bool:  # {{{
    while True:
        answer = input(f"> {message} (y/n): ")
        if answer.lower() == "y":
            return True
        if answer.lower() == "n":
            return False
        print("Are your stupid? Type 'y' or 'n': ")


# }}}
def dbg(*args):  # {{{
    print("dbg:", args)


# }}}
def dbg_kv(**kvargs):  # {{{
    print("dbg:", kvargs)


# }}}
def stop(text: str):  # {{{
    input(f"stop: {text}")


# }}}
def next_month(dt: datetime) -> datetime:  # {{{
    """Возвращает datetime первое число следующего месяца от полученного dt"""

    if dt.month == 12:
        next = dt.replace(
            year=dt.year + 1,
            month=1,
            day=1,
            hour=0,
            minute=0,
            second=0,
        )
    else:
        next = dt.replace(
            month=dt.month + 1,
            day=1,
            hour=0,
            minute=0,
            second=0,
        )

    return next


# }}}


if __name__ == "__main__":
    ...
