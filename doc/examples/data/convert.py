#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

from avin.data import *

def main():
    # Converting timeframes <= D
    yndx = Data.find(Exchange.MOEX, AssetType.Share, "YNDX")
    in_type = DataType.BAR_1M
    out_types = [
        DataType.BAR_5M,
        DataType.BAR_10M,
        DataType.BAR_1H,
        DataType.BAR_D,
        ]
    for out_type in out_types:
        Data.convert(yndx, in_type, out_type)

    # Converting to timeframe W, M availible only from timeframe D
    sber = Data.find(Exchange.MOEX, AssetType.Share, "SBER")
    in_type = DataType.BAR_D

    out_type = DataType.BAR_W
    Data.convert(sber, in_type, out_type)

    out_type = DataType.BAR_M
    Data.convert(sber, in_type, out_type)




if __name__ == "__main__":
    main()

