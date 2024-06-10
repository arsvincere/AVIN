
# def test_Signal():
#     s = Strategy.load("Every", "day")
#     afks = Share("AFKS")
#     sig = Signal(
#         dt=             now(),
#         strategy=       s,
#         signal_type=    Signal.Type.SHORT,
#         asset=          afks,
#         )
#     assert sig.strategy == s
#     assert sig.type == Signal.Type.SHORT
#     assert sig.type.name == "SHORT"
#     assert sig.asset == afks
#     assert sig.position is None
#     assert sig.isShort()
#     assert not sig.isLong()
#
# def test_Strategy():
#     s = Strategy.load("Every", "day")
#     assert s.name == "Every"
#     assert s.version == "day"
#     assert s.long_list[0].ticker == "AFKS"
#     assert s.short_list[0].ticker == "AFKS"
#     assert s.long_list.name == "long"
#     assert s.short_list.name == "short"
#
