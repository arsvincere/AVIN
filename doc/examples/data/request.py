#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

from avin.data import *

def main():
    # Request data
    # Data.request(...) return simply list of full path to data files in
    # closed interval [begin_year, end_year]
    # This is for greater flexibility. The requester can do whatever he wants
    # with them, read them as strings, as csv, as DateFrames...
    # If data not found - return []

    sber = Data.find(Exchange.MOEX, AssetType.Share, "SBER")
    data_files = Data.request(sber, DataType.BAR_D, 2021, 2023)
    print(data_files)

if __name__ == "__main__":
    main()

