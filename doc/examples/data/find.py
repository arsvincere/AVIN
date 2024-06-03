#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

from avin.data import *

def main():
    # Find index
    imoex2 = Data.find(Exchange.MOEX, AssetType.Index, "IMOEX2")
    print(imoex2)
    print(imoex2.name)

    # Find share
    sber = Data.find(Exchange.MOEX, AssetType.Share, "SBER")
    print(sber)

    # Find share on SPB
    aapl = Data.find(Exchange.SPB, AssetType.Share, "AAPL")
    print(aapl)

    # Find bond
    ofz = Data.find(Exchange.MOEX, AssetType.Bond, "SU26225RMFS1")
    print(ofz)

    # Find by figi
    aflt = Data.find(Exchange.MOEX, AssetType.Share, "BBG004S683W7")
    print(aflt)

    # Find by tinkoff uid
    gazp = Data.find(
        Exchange.MOEX, AssetType.Share, "962e2a95-02a9-4171-abd7-aa198dbe643a"
        )
    print(gazp)
    print(gazp.name)


if __name__ == "__main__":
    main()

