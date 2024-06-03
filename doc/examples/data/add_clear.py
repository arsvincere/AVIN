#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

from avin.data import *

def main():
    # Importing data in to standart csv format
    # market data must be download before, see doc/examples/data/download.py
    # then delete downloaded files (usr/download/<source_name>)

    source = Source.MOEX
    Data.add(source)
    Data.clear(source)

    source = Source.TINKOFF
    Data.add(source)
    Data.clear(source)


if __name__ == "__main__":
    main()

