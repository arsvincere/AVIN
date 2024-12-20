import avin


def condition(item: avin.Asset | avin.Trade | avin.Chart) -> bool:
    class_name = item.__class__.__name__
    match class_name:
        case "Asset":
            return condition_asset(item)
        case "Trade":
            return condition_trade(item)
        case "Chart":
            return condition_chart(item)


def condition_asset(asset: avin.Asset) -> bool:
    assert False, "todo it"


def condition_trade(trade: avin.Trade) -> bool:
    assert False, "todo it"


def condition_chart(chart: avin.Chart) -> bool:
    assert False, "todo it"

    # Example:
    # if chart[3] is None:
    #     return False
    #
    # b3 = chart[3]
    # b2 = chart[2]
    # b1 = chart[1]
    #
    # if b3.isBull() and b2.isBull() and b1.isBull():
    #     return True
    #
    # return False
