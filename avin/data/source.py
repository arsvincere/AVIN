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


class Source(enum.Enum):  # {{{
    UNDEFINE = 0
    MOEX = 1
    TINKOFF = 2

    @classmethod  # save# {{{
    def save(cls, source: Source, file_path: str):
        string = source.name
        Cmd.write(string, file_path)

    # }}}
    @classmethod  # load# {{{
    def load(cls, file_path):
        string = Cmd.read(file_path).strip()
        sources = {
            "UNDEFINE": Source.UNDEFINE,
            "MOEX": Source.MOEX,
            "TINKOFF": Source.TINKOFF,
        }
        return sources[string]

    # }}}


# }}}
