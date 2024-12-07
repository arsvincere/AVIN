#!/usr/bin/env python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================


from avin.utils import *


def test_binary_search():  # {{{
    v1 = [0, 1, 2, 3, 4, 5, 6, 7, 8]
    v2 = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    for i in v1:
        assert binary_search(v1, i) == i
    for i in v2:
        assert binary_search(v2, i) == i
    x = -5
    assert binary_search(v1, x) is None
    x = 100
    assert binary_search(v1, x) is None
    x = 0.5
    assert binary_search(v1, x) is None


# }}}
def test_find_left_right():  # {{{
    v1 = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    x = -5
    assert find_left(v1, x) is None
    assert find_right(v1, x) == 0
    x = 3
    assert find_left(v1, x) == 3
    assert find_right(v1, x) == 3
    x = 3.5
    assert find_left(v1, x) == 3
    assert find_right(v1, x) == 4
    x = 11
    assert find_left(v1, x) == 9
    assert find_right(v1, x) == None


# }}}


if __name__ == "__main__":
    ...
