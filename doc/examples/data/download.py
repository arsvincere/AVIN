#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

from avin.data import *

def main():
    # Download one asset, one year, from MOEX
    source = Source.MOEX
    sber_id = Data.find(Exchange.MOEX, AssetType.Share, "SBER")
    Data.download(source, DataType.BAR_D, sber_id, 2024)

    # Download one asset, one year, from Tinkoff
    source = Source.TINKOFF
    yndx_id = Data.find(Exchange.MOEX, AssetType.Share, "YNDX")
    Data.download(source, DataType.BAR_1M, yndx_id, 2024)

    # Multiple download
    source = Source.MOEX
    data_type = DataType.BAR_D
    indexes = Data.assets(source, AssetType.Index)
    indexes = indexes[0:3]  # select first three indexes there are a lot of them
    begin = 1997
    end = 2025
    for i in indexes:
        for year in range(begin, end):
            Data.download(source, data_type, i, year)





if __name__ == "__main__":
    main()

