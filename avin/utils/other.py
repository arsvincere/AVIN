#!/usr/bin/env python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

import bisect
import os
from datetime import datetime, timezone
from decimal import Decimal

from avin.utils.cmd import Cmd


def now():  # {{{
    return datetime.now(timezone.utc)


# }}}
def round_price(price: float, min_price_step: float):  # {{{
    price = Decimal(price)
    price -= price % Decimal(min_price_step)
    return float(price)


# }}}
def binary_search(vector, x, key=None):  # {{{
    left = 0
    right = len(vector) - 1
    while left <= right:
        mid = (right - left) // 2 + left
        mid_val = vector[mid] if key is None else key(vector[mid])
        if x == mid_val:
            return mid
        if x < mid_val:
            right = mid - 1
        else:
            left = mid + 1
    return None


# }}}
def find_left(vector, x, key=None):  # {{{
    """Возвращает индекс элемента меньше или равного 'x'
    Если 'x', меньше самого левого элемента в векторе, возвращает None
    """
    i = bisect.bisect_right(vector, x, key=key)
    if i:
        return i - 1
    return None


# }}}
def find_right(vector, x, key=None):  # {{{
    """Возвращает индекс элемента больше или равного 'x'
    Если 'x', больше самого правого элемента в векторе, возвращает None
    """
    i = bisect.bisect_left(vector, x, key=key)
    if i != len(vector):
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
    count_file = 0
    count_str = 0
    for root, _, files in os.walk(dir_path):
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                text = Cmd.loadText(file_path)
                n = len(text)
                count_str += n
                count_file += 1
    return count_file, count_str


# }}}
def ask_user(message: str) -> bool:  # {{{
    while True:
        answer = input(f"> {message} (y/n): ")
        if answer in "yY":
            return True
        if answer in "nN":
            return False
        print("Некорректный ввод. Введите 'y' или 'n': ")


# }}}

if __name__ == "__main__":
    ...
