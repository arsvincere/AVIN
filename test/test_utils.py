#!/usr/bin/env python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================


from avin.utils import *


def test_binarySearch():
    v1 = [0, 1, 2, 3, 4, 5, 6, 7, 8]
    v2 = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    for i in v1:
        assert binarySearch(v1, i) == i
    for i in v2:
        assert binarySearch(v2, i) == i
    x = -5
    assert binarySearch(v1, x) is None
    x = 100
    assert binarySearch(v1, x) is None
    x = 0.5
    assert binarySearch(v1, x) is None


def test_find_Left_Right():
    v1 = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    x = -5
    assert findLeft(v1, x) is None
    assert findRight(v1, x) == 0
    x = 3
    assert findLeft(v1, x) == 3
    assert findRight(v1, x) == 3
    x = 3.5
    assert findLeft(v1, x) == 3
    assert findRight(v1, x) == 4
    x = 11
    assert findLeft(v1, x) == 9
    assert findRight(v1, x) == None


if __name__ == "__main__":
    ...
