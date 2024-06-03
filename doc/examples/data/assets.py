#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

from avin.data import Data, Source, DataType, Exchange, AssetType, Id

def main():
    # Receive all indexes from MOEX
    source = Source.MOEX
    asset_type = AssetType.Index
    indexes = Data.assets(source, asset_type)
    for i in indexes:
        print(i)

    # Receive all shares from Tinkoff
    source = Source.TINKOFF
    asset_type = AssetType.Share
    shares = Data.assets(source, asset_type)
    for i in shares:
        print(i)

    # Receive all bonds from Tinkoff
    source = Source.TINKOFF
    asset_type = AssetType.Bond
    bonds = Data.assets(source, asset_type)
    for i in bonds:
        print(i)

if __name__ == "__main__":
    main()

