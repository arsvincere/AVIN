#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

from __future__ import annotations

from datetime import date, datetime

from avin.const import Res
from avin.keeper import Keeper
from avin.utils import Cmd, now


class _InstrumentInfoCache:  # {{{
    def __init__(  # {{{
        self,
        source: DataSource,
        asset_type: AssetType,
        assets_info: list[dict],
    ):
        self.source = source
        self.asset_type = asset_type
        self.assets_info = assets_info

    # }}}
    @classmethod  # save# {{{
    async def save(cls, cache: _InstrumentInfoCache) -> None:
        # save cache in res files
        cache_dir = Cmd.path(Res.CACHE, cache.source.name.lower())
        file_path = Cmd.path(cache_dir, f"{cache.asset_type.name}.json")
        Cmd.saveJson(cache.assets_info, file_path, encoder=cls.encoderJson)

        # save cache in postgres
        await Keeper.update(cache)

    # }}}
    @classmethod  # load# {{{
    def load(cls, source: Source, asset_type: AssetType):
        cache_dir = Cmd.path(Res.CACHE, source.name.lower())
        cache_path = Cmd.path(cache_dir, f"{asset_type.name}.json")
        cache = Cmd.loadJson(cache_path, decoder=cls.decoderJson)
        return cache

    # }}}
    @classmethod  # checkCachingDate# {{{
    def checkCachingDate(cls, source: Source):
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
    def updateCachingDate(cls, source: Source):
        dt = now().isoformat()
        file_path = Cmd.path(Res.CACHE, source.name.lower(), "last_update")
        Cmd.write(dt, file_path)

    # }}}
    @staticmethod  # encoderJson# {{{
    def encoderJson(obj):
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()

    # }}}
    @staticmethod  # decoderJson# {{{
    def decoderJson(obj):
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


# }}}
