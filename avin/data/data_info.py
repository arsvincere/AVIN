#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from avin.data.data_source import DataSource
from avin.data.data_type import DataType
from avin.data.instrument import Instrument
from avin.keeper import Keeper
from avin.utils import logger


@dataclass  # DataInfo  # {{{
class DataInfo:
    source: DataSource
    instrument: Instrument
    data_type: DataType
    first_dt: datetime
    last_dt: datetime

    @classmethod  # fromRecord  # {{{
    async def fromRecord(cls, record: asyncpg.Record) -> _BarsDataInfo:
        logger.debug(f"{cls.__name__}.fromRecord()")

        instrument = await Instrument.fromFigi(record["figi"])

        data_info_node = cls(
            source=DataSource.fromRecord(record),
            instrument=instrument,
            data_type=DataType.fromRecord(record),
            first_dt=record["first_dt"],
            last_dt=record["last_dt"],
        )
        return data_info_node

    # }}}
    @classmethod  # load  # {{{
    async def load(
        cls, instrument: Instrument, data_type: DataType
    ) -> DataInfo | None:
        logger.debug(f"{cls.__name__}.load()")

        node = await Keeper.get(
            cls, instrument=instrument, data_type=data_type
        )
        return node

        # }}}


# }}}
class DataInfoList:  # {{{
    def __init__(self, nodes: Optional[list] = None):  # {{{
        logger.debug(f"{self.__class__.__name__}.__init__()")
        self.__nodes: list[DataInfo] = nodes if nodes else list()

    # }}}
    def __getitem__(  # {{{
        self, instrument: Instrument
    ) -> list[DataInfo]:
        selected = list()
        for i in self.__nodes:
            if i.instrument == instrument:
                selected.append(i)

        return selected

    # }}}
    def __iter__(self) -> Iterator:  # {{{
        return iter(self.__nodes)

    # }}}
    def __len__(self):  # {{{
        return len(self.__nodes)

    # }}}
    def add(self, node: DataInfo) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.add({node})")
        assert isinstance(node, DataInfo)

        self.__nodes.append(node)

    # }}}
    def remove(self, node: DataInfo) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.remove({node})")
        assert isinstance(node, DataInfo)

        try:
            self.__nodes.remove(node)
        except ValueError as err:
            logger.exception(err)

    # }}}
    def clear(self) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.clear()")
        self.__nodes.clear()

    # }}}
    def info(  # {{{
        self, instrument: Instrument, data_type: DataType
    ) -> DataInfo | None:
        logger.debug(f"{self.__class__.__name__}.info()")

        nodes = self[instrument]
        for node in nodes:
            if node.data_type == data_type:
                return node

        return None

    # }}}
    def getInstruments(self) -> list[Instrument]:  # {{{
        logger.debug(f"{self.__class__.__name__}.getInstruments()")

        all_instr = list()
        for i in self.__nodes:
            if i.instrument not in all_instr:
                all_instr.append(i.instrument)

        return all_instr

    # }}}
    @classmethod  # fromRecord  # {{{
    async def fromRecord(cls, records: list[asyncpg.Record]) -> DataInfo:
        logger.debug(f"{cls.__name__}.fromRecord()")

        nodes = list()
        for record in records:
            node = await DataInfo.fromRecord(record)
            nodes.append(node)

        return DataInfoList(nodes)

    # }}}
    @classmethod  # load  # {{{
    async def load(
        cls,
        instr: Optional[Instrument] = None,
        data_type: Optional[DataType] = None,
    ) -> DataInfo | None:
        logger.debug(f"{cls.__name__}.load({instr}-{data_type})")

        data_info = await Keeper.get(
            cls, instrument=instr, data_type=data_type
        )
        return data_info

    # }}}


# }}}


if __name__ == "__main__":
    ...
