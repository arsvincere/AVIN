
# def test_Order():
#     strategy = Strategy.load("Every", "day")
#     afks = Share("AFKS")
#     sig = Signal(
#         dt= now(),
#         strategy=strategy,
#         signal_type=Signal.Type.LONG,
#         asset= afks,
#         )
#     o = Order(
#         signal=sig,
#         type=Order.Type.LIMIT,
#         direction=Order.Direction.SELL,
#         asset=afks,
#         lots=10,
#         price=101.1,
#         )
#     assert o.signal == sig
#     assert o.type == Order.Type.LIMIT
#     assert o.direction == Order.Direction.SELL
#     assert o.asset == afks
#     assert o.lots == 10
#     assert o.price == 101.1
#
# def test_Operation():
#     strategy = Strategy.load("Every", "day")
#     afks = Share("AFKS")
#     sig = Signal(
#         dt= now(),
#         strategy=strategy,
#         signal_type=Signal.Type.LONG,
#         asset= afks,
#         )
#     o = Order(
#         signal=sig,
#         type=Order.Type.LIMIT,
#         direction=Order.Direction.SELL,
#         asset=afks,
#         lots=10,
#         price=101.1,
#         )
#     dt=now()
#     quantity = o.lots * o.asset.brockerInfo()["lot"]
#     amount = quantity * o.price
#     com = amount * 0.0005
#     op = Operation(
#         signal=o.signal,
#         dt=dt,
#         direction=Operation.Direction.SELL,
#         asset=o.asset,
#         lots=o.lots,
#         quantity=quantity,
#         price=o.price,
#         amount=amount,
#         commission=com,
#         )
#     assert op.signal == o.signal
#     assert op.dt == dt
#     assert op.direction == Operation.Direction.SELL
#     assert op.asset == afks
#     assert op.lots == o.lots
#     assert op.quantity == quantity
#     assert op.price == o.price
#     assert op.amount == amount
#     assert op.commission == com
#     obj = Operation.toJSON(op)
#     from_obj = Operation.fromJSON(obj)
#     assert op.dt == from_obj.dt
#     assert op.direction == from_obj.direction
#     assert op.asset.name == from_obj.asset.name
#     assert op.lots == from_obj.lots
#     assert op.quantity == from_obj.quantity
#     assert op.price == from_obj.price
#     assert op.amount == from_obj.amount
#     assert op.commission == from_obj.commission
#
# def test_Position():
#     strategy = Strategy.load("Every", "day")
#     afks = Share("AFKS")
#     sig = Signal(
#         dt= now(),
#         strategy=strategy,
#         signal_type=Signal.Type.LONG,
#         asset= afks,
#         )
#     op = Operation(
#         signal=     sig,
#         dt=         now(),
#         direction=  Operation.Direction.SELL,
#         asset=      afks,
#         lots=       100,
#         quantity=   100 * afks.lot,
#         price=      20,
#         amount=     20 * 100 * afks.lot,
#         commission= 20 * 100 * afks.lot * 0.0005,
#         )
#     pos = Position(sig, op)
#     assert pos.asset == sig.asset
#     assert pos.status == Position.Status.OPEN
#     assert len(pos.operations) == 1
#     assert pos.parent() == sig
#     assert pos.lots() == -op.lots
#     assert pos.openDatetime() == op.dt
#     assert pos.quantity() == -op.quantity
#     assert pos.buyQuantity() == 0
#     assert pos.sellQuantity() == op.quantity
#     assert pos.amount() == -op.amount
#     assert pos.buyAmount() == 0
#     assert pos.sellAmount() == op.amount
#     assert pos.buyCommission() == 0
#     assert pos.sellCommission() == op.commission
#     assert pos.average() == op.amount / op.quantity
#     assert pos.averageBuy() == 0
#     assert pos.averageSell() == op.amount / op.quantity
#     op2 = Operation(
#         signal=     sig,
#         dt=         now(),
#         direction=  Operation.Direction.BUY,
#         asset=      afks,
#         lots=       100,
#         quantity=   100 * afks.lot,
#         price=      19,
#         amount=     19 * 100 * afks.lot,
#         commission= 19 * 100 * afks.lot * 0.0005,
#         )
#     pos.add(op2)
#     assert pos.result() == 9805.0
#     assert pos.closeDatetime() == op2.dt
#     assert pos.holdingDays() == 1
#     assert pos.percent() == 5.16
#     assert pos.percentPerDay() == 5.16
#     assert pos.status == Position.Status.CLOSE
#     assert sig.info["position"]["result"] == pos.result()
#
# def test_Trade_TradeList_Test_Report():
#     ...
#
