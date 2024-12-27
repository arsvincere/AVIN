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

# TODO: перемудрил...
# DataInfo - это должна быть одна нода, один элемент про один актив один тип
# DataInfoList - это уже список этих элементов
# По аналогии с Asset AssetList
# а тут у тебя порно сильно отличное от остального кода
# надо переименовать и обновить gui и keeper
# DataInfoNode -> DataInfo
# DataInfo -> DataInfoList


@dataclass  # DataInfoNode  # {{{
class DataInfoNode:
    source: DataSource
    instrument: Instrument
    data_type: DataType
    first_dt: datetime
    last_dt: datetime

    @classmethod  # fromRecord  # {{{
    def fromRecord(cls, record: asyncpg.Record) -> _BarsDataInfo:
        logger.debug(f"{cls.__name__}.fromRecord()")

        data_info_node = cls(
            source=DataSource.fromRecord(record),
            instrument=Instrument.fromRecord(record),
            data_type=DataType.fromRecord(record),
            first_dt=record["first_dt"],
            last_dt=record["last_dt"],
        )
        return data_info_node

    # }}}
    @classmethod  # load  # {{{
    async def load(
        cls, instrument: Instrument, data_type: DataType
    ) -> DataInfoNode | None:
        logger.debug(f"{cls.__name__}.load()")

        node = await Keeper.get(
            cls, instrument=instrument, data_type=data_type
        )
        return node

        # }}}


# }}}
class DataInfo:  # {{{
    def __init__(self, nodes: Optional[list] = None):  # {{{
        logger.debug(f"{self.__class__.__name__}.__init__()")
        self.__nodes: list[DataInfoNode] = nodes if nodes else list()

    # }}}
    def __getitem__(  # {{{
        self, instrument: Instrument
    ) -> list[DataInfoNode]:
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
    def add(self, node: DataInfoNode) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.add({node})")
        assert isinstance(node, DataInfoNode)

        self.__nodes.append(node)

    # }}}
    def remove(self, node: DataInfoNode) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.remove({node})")
        assert isinstance(node, DataInfoNode)

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
    ) -> DataInfoNode | None:
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
    def fromRecord(cls, records: list[asyncpg.Record]) -> DataInfo:
        logger.debug(f"{cls.__name__}.fromRecord()")

        nodes = list()
        for record in records:
            node = DataInfoNode.fromRecord(record)
            nodes.append(node)

        return DataInfo(nodes)

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
