
# def test_Extremum():
#     b1 = Bar(10, 11, 12, 9, 1000, now(), parent=True)
#     b2 = Bar(11, 12, 13, 10, 1000, now(), parent=True)
#     e1 = Extremum(Extremum.Type.MIN, b1)
#     e2 = Extremum(Extremum.Type.MAX | Extremum.Type.LONGTERM, b2)
#     assert b1.isExtremum()
#     assert b2.isExtremum()
#     assert e2.isLongterm()
#     assert e2.isMidterm()
#     assert e2.isShortterm()
#     assert e1.price == 9
#     assert e1.parent() == b1
#     assert e1.dt == b1.dt
#     assert e2.price == 13
#     assert e2.parent() == b2
#     assert e2.dt == b2.dt
#     assert e1 < e2
#     assert e1 <= e2
#     assert e2 > e1
#     assert e2 >= e1
#     assert e1 != e2
#     assert not e1.isShortterm()
#     assert not e1.isMidterm()
#     assert not e1.isLongterm()
#     e1.addFlag(Extremum.Type.MIDTERM)
#     assert e1.isShortterm()
#     assert e1.isMidterm()
#     assert not e1.isLongterm()
#     e1.addFlag(Extremum.Type.LONGTERM)
#     assert e1.isShortterm()
#     assert e1.isMidterm()
#     assert e1.isLongterm()
#
# def test_ExtremumList():
#     asset = Asset(Exchange.MOEX, Type.SHARE, ticker="AFKS")
#     tf = TimeFrame("D")
#     begin = datetime(2018, 1, 1, tzinfo=UTC)
#     end = datetime(2023, 9, 1, tzinfo=UTC)
#     chart = Chart(asset, tf, begin, end)
#     assert chart.ticker == "AFKS"
#     extr = ExtremumList(chart)
#     assert extr.sterm[-1].isShortterm()
#     assert extr.mterm[-1].isMidterm()
#     assert extr.lterm[-1].isLongterm()
#
