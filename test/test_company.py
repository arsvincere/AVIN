#!/usr/bin/env  python3
# LICENSE:      GNU GPL
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com


import sys
from avin.utils import *
from avin.const import *
from avin.core import *
from avin.company import *
from avin.gui import *

def test_Analytic():
    asset = Share("AFKS")
    Analytic.researchBarSize(asset)
    chart = asset.loadChart("D", "2023-08-01", "2023-09-01")
    bar = chart.last
    size = Analytic.size(bar.body)
    assert size == Range.Size.NORMAL

def test_Tester():
    tester = Tester()
    test = Test.load("user/test/.example")
    tester.setTest(test)
    tester.runTest()
    assert Cmd.isExist(
        "user/test/.example/tlist.tl"
        )
    assert Cmd.isExist(
        "user/test/.example/report.csv"
        )
    test = Test.load("user/test/.example")
    assert test.tlist.count == 46















