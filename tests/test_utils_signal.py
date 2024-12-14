#!/usr/bin/env python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

import asyncio

import pytest
from avin import *

order = "LimitOrder"
operations = ["op1", "op2", "op3"]


def test_Signal():
    return


async def slot1(*args):
    print("\nslot1", args)
    await asyncio.sleep(3)
    print("slot1 complete")


async def slot2(*args):
    print("slot2", args)
    await asyncio.sleep(3)
    print("slot2 complete")


@pytest.mark.asyncio  # test_AsyncSignal  # {{{
async def test_AsyncSignal(event_loop):
    fulfilled = AsyncSignal(str, list)
    fulfilled.aconnect(slot1)
    fulfilled.aconnect(slot2)

    await fulfilled.aemit(order, operations)


# }}}
