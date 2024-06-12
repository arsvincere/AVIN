#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

from avin.data import *

def main():
    # Request first datetime IMOEX, use 1M and D data type
    imoex = Data.find(Exchange.MOEX, AssetType.Index, "IMOEX")
    source = Source.MOEX
    bars_1m = DataType.BAR_1M
    bars_d = DataType.BAR_D
    first_dt_1m = Data.firstDateTime(source, bars_1m, imoex)
    first_dt_d = Data.firstDateTime(source, bars_d, imoex)
    print("IMOEX first availible candle 1M at MOEX", first_dt_1m)
    print("IMOEX first availible candle D at MOEX", first_dt_d)

    # Request first datetime SBER, use 1M and D data type
    sber = Data.find(Exchange.MOEX, AssetType.Share, "SBER")
    source = Source.MOEX
    bars_1m = DataType.BAR_1M
    bars_d = DataType.BAR_D
    first_dt_1m = Data.firstDateTime(source, bars_1m, sber)
    first_dt_d = Data.firstDateTime(source, bars_d, sber)
    print("SBER first availible candle 1M at MOEX", first_dt_1m)
    print("SBER first availible candle D at MOEX", first_dt_d)

    # Request first datetime from Tinkoff
    # You can only download 1M candles from Tinkoff in
    # archives starting from 2018, now, when feature download from MOEX
    # avalible, it is does't make sens
    source = Source.TINKOFF
    first_dt_1m = Data.firstDateTime(source, bars_1m, sber)
    first_dt_d = Data.firstDateTime(source, bars_d, sber)
    print("SBER first availible candle 1M at Tinkoff", first_dt_1m)
    print("SBER first availible candle D at Tinkoff", first_dt_d)

if __name__ == "__main__":
    main()

