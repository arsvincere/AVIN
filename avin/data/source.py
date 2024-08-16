#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

from __future__ import annotations

import enum

from avin.utils import Cmd

# TODO rename module -> data_source
# TODO rename class -> DataSource


class Source(enum.Enum):  # {{{
    MOEX = 1
    TINKOFF = 2

    @classmethod  # fromRecord  # {{{
    def fromRecord(cls, record):
        string = record["source"]
        sources = {
            "MOEX": Source.MOEX,
            "TINKOFF": Source.TINKOFF,
        }
        return sources[string]

    # }}}
    @classmethod  # save# {{{
    def save(cls, source: Source, file_path: str):
        # DEPICATE
        string = source.name
        Cmd.write(string, file_path)

    # }}}
    @classmethod  # load# {{{
    def load(cls, file_path):
        # DEPICATE
        string = Cmd.read(file_path).strip()
        sources = {
            "MOEX": Source.MOEX,
            "TINKOFF": Source.TINKOFF,
        }
        return sources[string]

    # }}}


# }}}
