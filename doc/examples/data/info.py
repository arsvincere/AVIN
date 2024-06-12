#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

from avin.data import *

def main():
    # Share info
    sber = Data.find(Exchange.MOEX, AssetType.Share, "SBER")
    info = Data.info(sber)
    print()
    print(info)

    # Index info
    imoex = Data.find(Exchange.MOEX, AssetType.Index, "IMOEX")
    info = Data.info(imoex)
    print()
    print(info)

    # Future info
    imoex = Data.find(Exchange.MOEX, AssetType.Future, "USDRUBF")
    info = Data.info(imoex)
    print()
    print(info)

if __name__ == "__main__":
    main()

