import avin


def condition(asset: avin.Asset) -> bool:
    chart = asset.chart("D")

    # if chart[3] is None:
    #     return False
    #
    # b3 = chart[3]
    # b2 = chart[2]
    # b1 = chart[1]
    #
    # if b3.isBull() and b2.isBull() and b1.isBull():
    #     return True

    return False
