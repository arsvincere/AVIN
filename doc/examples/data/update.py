#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

from avin.data import *

def main():
    # Update specified data
    # the update uses the same source as the download data
    sber_id = Data.find(Exchange.MOEX, AssetType.Share, "SBER")
    data_type = DataType.BAR_D
    Data.update(sber_id, data_type)

    yndx_id = Data.find(Exchange.MOEX, AssetType.Share, "YNDX")
    data_type = DataType.BAR_1M
    Data.update(yndx_id, data_type)

    # Update all data in the system
    Data.updateAll()


if __name__ == "__main__":
    main()

