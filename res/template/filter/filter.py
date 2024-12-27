from avin import *


async def conditionChart(chart: Chart) -> bool:
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
    return False


async def conditionAsset(asset: Asset) -> bool:
    chart = asset.chart("D")
    result = await conditionChart(chart)
    return result


async def conditionTrade(trade: Trade) -> bool:
    chart = await trade.loadChart("D")
    result = await conditionChart(chart)
    return result
