#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

from __future__ import annotations

from datetime import date, datetime
from typing import Any

from avin.const import Res
from avin.data.data_source import DataSource
from avin.data.instrument import Instrument
from avin.keeper import Keeper
from avin.utils import Cmd, logger, now


class _InstrumentsInfoCache:
    def __init__(  # {{{
        self,
        source: DataSource,
        itype: Instrument.Type,
        original_info: list[str],
        formatted_info: list[dict],
    ):
        self.__source = source
        self.__type = itype
        self.__original = original_info
        self.__formatted = formatted_info

    # }}}
    @property  # source{{{
    def source(self):
        return self.__source

    # }}}
    @property  # type{{{
    def type(self):
        return self.__type

    # }}}
    @property  # original{{{
    def original(self):
        return self.__original

    # }}}
    @property  # formatted{{{
    def formatted(self):
        return self.__formatted

    # }}}
    @classmethod  # save# {{{
    async def save(cls, cache: _InstrumentsInfoCache) -> None:
        logger.debug(f"{cls.__name__}.save()")

        # save original cache in res files
        file_path = Cmd.path(
            Res.CACHE,
            cache.source.name.lower(),
            f"{cache.type.name}.json",
        )
        Cmd.saveJson(cache.original, file_path, encoder=cls.encoderJson)

        # save formatted cache in postgres
        await Keeper.update(cache)

    # }}}
    @classmethod  # load# {{{
    def load(
        cls, source: DataSource, itype: Instrument.Type
    ) -> _InstrumentsInfoCache:
        logger.debug(f"{cls.__name__}.load()")

        cache_path = Cmd.path(
            Res.CACHE,
            source.name.lower(),
            f"{itype.name}.json",
        )
        json_info = Cmd.loadJson(cache_path, decoder=cls.decoderJson)
        cache = _InstrumentsInfoCache(source, itype, json_info, [])

        return cache

    # }}}
    @classmethod  # checkCachingDate# {{{
    def checkCachingDate(cls, source: DataSource) -> bool:
        logger.debug(f"{cls.__name__}.checkCachingDate()")

        # ckeck file with last update datetime
        file_path = Cmd.path(Res.CACHE, source.name.lower(), "last_update")
        if not Cmd.isExist(file_path):
            return False

        # read file, return True if last update == today
        string = Cmd.read(file_path)
        last_update = datetime.fromisoformat(string)
        return now().date() == last_update.date()

    # }}}
    @classmethod  # updateCachingDate# {{{
    def updateCachingDate(cls, source: DataSource) -> None:
        logger.debug(f"{cls.__name__}.updateCachingDate()")

        dt = now().isoformat()
        file_path = Cmd.path(Res.CACHE, source.name.lower(), "last_update")
        Cmd.write(dt, file_path)

    # }}}
    @staticmethod  # encoderJson# {{{
    def encoderJson(obj) -> Any:
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()

    # }}}
    @staticmethod  # decoderJson# {{{
    def decoderJson(obj) -> Any:
        # NOTE::
        # см формат файлов кэша, там слишком много деталей спецефичных
        # сейчас в MOEX файлах после чтения остаются строками разные даты:
        # "SETTLEDATE": "2024-05-31"
        # "LASTTRADEDATE": "2025-03-20",
        # "LASTDELDATE": "2025-03-20",
        # "IMTIME": "2024-05-29T18:58:11",
        # Пока они нигде не используются, так что пусть так и лежат.
        # На будущее возможное решение - при сохранении все эти поля
        # проверять и переводить в UTC datetime сразу при кэшировании
        # а сейчас они после загрузки как строки идут
        for k, v in obj.items():
            if isinstance(v, str) and "+00:00" in v:
                obj[k] = datetime.fromisoformat(obj[k])
        return obj

    # }}}
