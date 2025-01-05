#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

"""The module provides interaction with the postgresql database

It is assumed, that the user does not use this class directly. All other
classes in program turn to the database through the interface of this class
"Keeper". Thus, the entire SQL code is collected inside this class.

But if you really need to make a direct request to the database, you can use
the method - Keeper.transaction(sql_request).
"""

from __future__ import annotations

import inspect
import os
from datetime import datetime
from typing import Any

import asyncpg

from avin.config import Auto, Usr
from avin.const import ONE_DAY, ONE_MONTH, Dir
from avin.utils import Cmd, ask_user, logger, now

__all__ = ("Keeper",)


class Keeper:
    USER = Usr.PG_USER
    DATABASE = Usr.PG_DATABASE
    HOST = Usr.PG_HOST

    __LAST_BACKUP_DATA_DT = Cmd.path(Usr.DATA, "backup_db_data")
    __LAST_BACKUP_USER_DT = Cmd.path(Usr.DATA, "backup_db_user")
    __BACKUP_DATA = Auto.BACKUP_MARKET_DATA
    __BACKUP_USER = Auto.BACKUP_USER_DB

    @classmethod  # createDataBase  # {{{
    def createDataBase(cls) -> None:
        logger.debug(f"{cls.__name__}.createDataBase()")

        enums = Cmd.path(Dir.LIB, "keeper", "enums.sql")
        data_scheme = Cmd.path(Dir.LIB, "keeper", "data_scheme.sql")
        public_scheme = Cmd.path(Dir.LIB, "keeper", "public_scheme.sql")
        tester_scheme = Cmd.path(Dir.LIB, "keeper", "tester_scheme.sql")
        trader_scheme = Cmd.path(Dir.LIB, "keeper", "trader_scheme.sql")

        os.system(f"createdb {cls.DATABASE}")
        os.system(f"psql -d {cls.DATABASE} < {enums}")
        os.system(f"psql -d {cls.DATABASE} < {data_scheme}")
        os.system(f"psql -d {cls.DATABASE} < {public_scheme}")
        os.system(f"psql -d {cls.DATABASE} < {tester_scheme}")
        os.system(f"psql -d {cls.DATABASE} < {trader_scheme}")

        logger.info("Database has been created")

    # }}}
    @classmethod  # dropDataBase  # {{{
    def dropDataBase(cls) -> None:
        logger.debug(f"{cls.__name__}.dropDataBase()")

        if not ask_user("Delete database?"):
            return

        if not ask_user("Double confirmation. Are you sure?"):
            return

        os.system(f"dropdb {cls.DATABASE}")
        logger.info("Database has been deleted")

    # }}}
    @classmethod  # backupUserData  # {{{
    def backupUserData(cls):
        logger.debug(f"{cls.__name__}.backupUserData()")

        Cmd.makeDirs(Auto.BACKUP_PATH)
        public_path = Cmd.path(Auto.BACKUP_PATH, "public_Fc")
        os.system(f"pg_dump {cls.DATABASE} -Fc -f {public_path} -n public")

        logger.info("Backup user data complete!")

    # }}}
    @classmethod  # backupMarketData  # {{{
    def backupMarketData(cls):
        logger.debug(f"{cls.__name__}.backupMarketData()")

        Cmd.makeDirs(Auto.BACKUP_PATH)
        data_path = Cmd.path(Auto.BACKUP_PATH, "data_Fc")
        os.system(f"pg_dump {cls.DATABASE} -Fc -f {data_path} -n data")

        logger.info("Backup market data complete!")

    # }}}
    @classmethod  # restoreUserData  # {{{
    def restoreUserData(cls):
        logger.debug(f"{cls.__name__}.restoreUserData()")

        public_path = Cmd.path(Auto.BACKUP_PATH, "public_Fc")
        if not Cmd.isExist(public_path):
            logger.error(f"Failed restore, no backup file: {public_path}")

        os.system(
            f"psql -a {cls.DATABASE} {cls.USER} "
            f"-c 'DROP SCHEMA public CASCADE'"
        )
        os.system(f"pg_restore -d {cls.DATABASE} {public_path}")

        logger.info("Restore user data complete!")

    # }}}
    @classmethod  # restoreMarketData  # {{{
    def restoreMarketData(cls):
        logger.debug(f"{cls.__name__}.restoreMarketData()")

        data_path = Cmd.path(Auto.BACKUP_PATH, "data_Fc")
        if not Cmd.isExist(data_path):
            logger.error(f"Failed restore, no backup file: {data_path}")

        os.system(
            f"psql -a {cls.DATABASE} {cls.USER} "
            f"-c 'DROP SCHEMA data CASCADE'"
        )
        os.system(f"pg_restore -d {cls.DATABASE} {data_path}")

        logger.info("Restore market data complete!")

    # }}}
    @classmethod  # checkBackupData  # {{{
    def checkBackupData(cls):
        logger.debug(f"{cls.__name__}.checkBackupData()")

        # ckeck file with last update datetime
        if not Cmd.isExist(cls.__LAST_BACKUP_DATA_DT):
            need_update = True
        else:
            # read file, check last update > month ago
            dt_str = Cmd.read(cls.__LAST_BACKUP_DATA_DT)
            last_update = datetime.fromisoformat(dt_str)
            need_update = (now() - last_update) > ONE_MONTH

        if not need_update:
            return

        # backup & update file with datetime
        logger.info(":: Need backup market data - starting dump")
        cls.backupMarketData()
        dt = now().isoformat()
        Cmd.write(dt, cls.__LAST_BACKUP_DATA_DT)

    # }}}
    @classmethod  # checkBackupUser  # {{{
    def checkBackupUser(cls):
        logger.debug(f"{cls.__name__}.checkBackupUser()")

        # ckeck file with last update datetime
        if not Cmd.isExist(cls.__LAST_BACKUP_USER_DT):
            need_update = True
        else:
            # read file, check last update > day ago
            dt_str = Cmd.read(cls.__LAST_BACKUP_USER_DT)
            last_update = datetime.fromisoformat(dt_str)
            need_update = (now() - last_update) > ONE_DAY

        if not need_update:
            return

        # backup & update file with datetime
        logger.info(":: Need backup user data - starting dump")
        cls.backupUserData()
        dt = now().isoformat()
        Cmd.write(dt, cls.__LAST_BACKUP_USER_DT)

    # }}}

    @classmethod  # transaction  # {{{
    async def transaction(cls, sql_request: str) -> list[asyncpg.Record]:
        logger.debug(f"{cls.__name__}.transaction()\n{sql_request}")

        try:
            conn = await asyncpg.connect(
                user=cls.USER,
                database=cls.DATABASE,
                host=cls.HOST,
            )
            records = await conn.fetch(sql_request)
            await conn.close()
            return records
        except asyncpg.exceptions.NumericValueOutOfRangeError as err:
            logger.critical(err)
            exit(2)

    # }}}
    @classmethod  # info  # {{{
    async def info(cls, source, itype, **kwargs):
        """Looks for information about the asset in the cache.

        Returns a list of dictionaries with information about assets
        suitable for a request 'kwargs'
        """

        logger.debug(f"{cls.__name__}.info()")

        # Create source, exchange, itype conditions
        pg_source = f"data_source = '{source.name}'" if source else "TRUE"
        pg_itype = f"instrument_type = '{itype.name}'" if itype else "TRUE"

        # Remove None values in kwargs
        none_keys = [key for key in kwargs if kwargs[key] is None]
        for i in none_keys:
            kwargs.pop(i)
        # Create kwargs conditions
        if not kwargs:
            pg_kwargs = "TRUE"
        else:
            json_string = Cmd.toJson(kwargs)
            pg_kwargs = f"instrument_info @> '{json_string}'"

        # Request assets info records
        request = f"""
            SELECT
                instrument_info
            FROM data."InstrumentInfo"
            WHERE
                {pg_source} AND {pg_itype} AND {pg_kwargs};
            """
        records = await cls.transaction(request)

        # Create info dicts from records
        instruments_info = list()
        for record in records:
            json_string = record["instrument_info"]
            info_dict = Cmd.fromJson(json_string)
            instruments_info.append(info_dict)

        return instruments_info

    # }}}
    @classmethod  # add  # {{{
    async def add(cls, obj: Any) -> None:
        logger.debug(f"{cls.__name__}.add()")

        # Get class_name & choose method
        class_name = cls.__getClassName(obj)
        methods = {
            # "MOEX": cls.__addExchange,
            # "SPB": cls.__addExchange,
            # "_TEST_EXCHANGE": cls.__addExchange,
            "Instrument": cls.__addInstrument,
            "_BarsData": cls.__addBarsData,
            "Asset": cls.__addAsset,
            "Share": cls.__addAsset,
            "Index": cls.__addAsset,
            "AssetList": cls.__addAssetList,
            "Account": cls.__addAccount,
            "Strategy": cls.__addStrategy,
            "UStrategy": cls.__addStrategy,
            "StrategySet": cls.__addStrategySet,
            "Trade": cls.__addTrade,
            "TradeList": cls.__addTradeList,
            "Operation": cls.__addOperation,
            "MarketOrder": cls.__addOrder,
            "LimitOrder": cls.__addOrder,
            "StopOrder": cls.__addOrder,
            "StopLoss": cls.__addOrder,
            "TakeProfit": cls.__addOrder,
            "Test": cls.__addTest,
            "TestList": cls.__addTestList,
            "AnalyticData": cls.__addAnalyticData,
        }
        add_method = methods[class_name]

        # Add object
        await add_method(obj)

    # }}}
    @classmethod  # get  # {{{
    async def get(cls, Class, **kwargs) -> Any:
        logger.debug(f"{cls.__name__}.get()")
        assert inspect.isclass(Class)

        # Get class_name & choose method
        class_name = cls.__getClassName(Class)
        methods = {
            "Instrument": cls.__getInstrument,
            "DataInfo": cls.__getDataInfo,
            "DataInfoList": cls.__getDataInfoList,
            "DataSource": cls.__getDataSource,
            "DataType": cls.__getDataType,
            "datetime": cls.__getDateTime,
            "_Bar": cls.__getBarsRecords,
            "Bar": cls.__getBars,
            "Asset": cls.__getAsset,
            "AssetList": cls.__getAssetList,
            # "Account": cls.__getAccount,
            "StrategySet": cls.__getStrategySet,
            "Trade": cls.__getTrade,
            "TradeList": cls.__getTradeList,
            "Operation": cls.__getOperations,
            "Order": cls.__getOrders,
            "Test": cls.__getTest,
            "TestList": cls.__getTestList,
            "AnalyticData": cls.__getAnalyticData,
        }
        get_method = methods[class_name]

        # Get object(s)
        result = await get_method(Class, kwargs)
        return result

    # }}}
    @classmethod  # delete  # {{{
    async def delete(cls, obj, **kwargs) -> None:
        logger.debug(f"{cls.__name__}.delete()")

        # Get class_name & choose method
        class_name = cls.__getClassName(obj)
        methods = {
            "_BarsData": cls.__deleteBarsData,
            # "_TEST_EXCHANGE": cls.__deleteExchange,
            # "MOEX": cls.__deleteExchange,
            # "SPB": cls.__deleteExchange,
            "Instrument": cls.__deleteAsset,
            "Asset": cls.__deleteAsset,
            "Share": cls.__deleteAsset,
            "Index": cls.__deleteAsset,
            "AssetList": cls.__deleteAssetList,
            "Account": cls.__deleteAccount,
            "Strategy": cls.__deleteStrategy,
            "UStrategy": cls.__deleteStrategy,
            "StrategySet": cls.__deleteStrategySet,
            "Trade": cls.__deleteTrade,
            "TradeList": cls.__deleteTradeList,
            "Operation": cls.__deleteOperation,
            "MarketOrder": cls.__deleteOrder,
            "LimitOrder": cls.__deleteOrder,
            "StopOrder": cls.__deleteOrder,
            "Test": cls.__deleteTest,
            "TestList": cls.__deleteTestList,
            "AnalyticData": cls.__deleteAnalyticData,
        }
        delete_method = methods[class_name]

        # Delete object
        await delete_method(obj, kwargs)

    # }}}
    @classmethod  # update  # {{{
    async def update(cls, obj: Any, **kwargs) -> None:
        logger.debug(f"{cls.__name__}.update()")

        # Get class_name & choose method
        class_name = cls.__getClassName(obj)
        methods = {
            "Strategy": cls.__updateStrategy,
            "UStrategy": cls.__updateStrategy,
            "Trade": cls.__updateTrade,
            "MarketOrder": cls.__updateOrder,
            "LimitOrder": cls.__updateOrder,
            "StopOrder": cls.__updateOrder,
            "StopLoss": cls.__updateOrder,
            "TakeProfit": cls.__updateOrder,
            "Operation": cls.__updateOperation,
            "Test": cls.__updateTest,
            "_InstrumentsInfoCache": cls.__updateCache,
        }

        # Update object
        update_method = methods[class_name]
        await update_method(obj, kwargs)

    # }}}

    # @classmethod  # __addExchange  # {{{
    # async def __addExchange(cls, exchange: Exchange) -> None:
    #     logger.debug(f"{cls.__name__}.__addExchange()")
    #
    #     request = f"""
    #     INSERT INTO "Exchange"(exchange_name)
    #     VALUES ('{exchange.name}');
    #     """
    #
    #     try:
    #         await cls.transaction(request)
    #     except asyncpg.UniqueViolationError:
    #         logger.warning(
    #             f"Exchange '{exchange.name}' already exist in database"
    #         )
    #
    # # }}}
    @classmethod  # __addInstrument  # {{{
    async def __addInstrument(cls, instrument) -> None:
        logger.debug(f"{cls.__name__}.__addInstrument()")

        request = f"""
        INSERT INTO data."Instrument" (
            figi,
            exchange,
            type,
            ticker,
            name,
            lot,
            min_price_step
            )
        VALUES (
            '{instrument.figi}',
            '{instrument.exchange.name}',
            '{instrument.type.name}',
            '{instrument.ticker}',
            '{instrument.name}',
            {instrument.lot},
            {instrument.min_price_step}
            );
        """

        try:
            await cls.transaction(request)
        except asyncpg.UniqueViolationError:
            # logger.warning(f"Asset '{instrument}' already exist")
            return

    # }}}
    @classmethod  # __addBarsData  # {{{
    async def __addBarsData(cls, data) -> None:
        logger.debug(f"{cls.__name__}.__addBarsData()")

        # Create table if not exist
        bars_table_name = cls.__getTableName(data.instrument, data.type)
        await cls.__createBarsDataTable(bars_table_name)

        # If exist - delete old data at the same period
        request = f"""
            DELETE FROM {bars_table_name}
            WHERE
                '{data.first_dt}' <= dt AND dt <= '{data.last_dt}'
                ;
            """
        await cls.transaction(request)

        # Add bars data
        values = cls.__formatBarsData(data)
        request = f"""
        INSERT INTO {bars_table_name} (dt, open, high, low, close, volume)
        VALUES
            {values}
            ;
        """
        await cls.transaction(request)

        # Update table data."DataInfo" - about availible market data
        request = f"""
            DELETE FROM data."DataInfo"
            WHERE
                figi = '{data.instrument.figi}' AND
                data_type = '{data.type.name}'
                ;
            """
        await cls.transaction(request)
        request = f"""
            INSERT INTO data."DataInfo"(
                data_source, data_type, figi, first_dt, last_dt
                )
            VALUES (
                '{data.source.name}',
                '{data.type.name}',
                '{data.instrument.figi}',
                (SELECT min(dt) FROM {bars_table_name}),
                (SELECT max(dt) FROM {bars_table_name})
            );
            """
        await cls.transaction(request)

        # Update table "Asset" add new instrument if not exist
        await cls.__addAsset(data.instrument)

    # }}}
    @classmethod  # __addAsset  # {{{
    async def __addAsset(cls, asset) -> None:
        logger.debug(f"{cls.__name__}.__addAsset()")

        request = f"""
        INSERT INTO "Asset" (figi)
        VALUES ('{asset.figi}');
        """

        try:
            await cls.transaction(request)
        except asyncpg.UniqueViolationError:
            # logger.warning(f"Asset '{asset}' already exist in database")
            return

    # }}}
    @classmethod  # __addAssetList  # {{{
    async def __addAssetList(cls, alist) -> None:
        logger.debug(f"{cls.__name__}.__addAssetList()")

        # Add asset list
        request = f"""
            INSERT INTO "AssetList"(asset_list_name)
            VALUES ('{alist.name}');
        """
        await cls.transaction(request)

        # if asset list is empty - return
        if len(alist) == 0:
            return

        # Add assets
        pg_values = cls.__formatAssetList(alist)
        request = f"""
            INSERT INTO "AssetList-Asset" (asset_list_name, figi)
            VALUES
                {pg_values}
            ;
            """
        await cls.transaction(request)

    # }}}
    @classmethod  # __addAccount  # {{{
    async def __addAccount(cls, account) -> None:
        logger.debug(f"{cls.__name__}.__addAccount()")

        request = f"""
        INSERT INTO "Account" (
            account_name,
            broker
            )
        VALUES (
            '{account.name}',
            '{account.broker.name}'
            );
        """

        try:
            await cls.transaction(request)
        except asyncpg.UniqueViolationError:
            logger.warning(
                f"Account '{account.name}-{account.broker}'"
                "already exist in database"
            )

    # }}}
    @classmethod  # __addStrategy  # {{{
    async def __addStrategy(cls, strategy) -> None:
        logger.debug(f"{cls.__name__}.__addStrategy()")

        request = f"""
            INSERT INTO "Strategy"
                (strategy_name, version)
            VALUES
                ('{strategy.name}', '{strategy.version}');
        """

        try:
            await cls.transaction(request)
        except asyncpg.UniqueViolationError:
            logger.warning(
                f"Strategy '{strategy.name}-{strategy.version}' already exist"
            )

    # }}}
    @classmethod  # __addStrategySet  # {{{
    async def __addStrategySet(cls, s_set) -> None:
        logger.debug(f"{cls.__name__}.__addStrategySet()")

        # add StrategySet
        request = f"""
            INSERT INTO "StrategySet" (strategy_set_name)
            VALUES ('{s_set.name}');
        """
        await cls.transaction(request)

        # ensure not empty
        if not len(s_set):
            return

        # create pg_values for items
        pg_values = ""
        for i in s_set:
            val = (
                f"('{s_set.name}', '{i.strategy}','{i.version}', "
                f"'{i.figi}', {i.long}, {i.short}),\n"
            )
            pg_values += val
        pg_values = pg_values[0:-2]  # remove ",\n" after last value

        # add StrategySet items
        request = f"""
            INSERT INTO "StrategySet-Strategy"
                (strategy_set_name, strategy, version, figi, long, short)
            VALUES {pg_values};
        """
        await cls.transaction(request)

    # }}}
    @classmethod  # __addTradeList  # {{{
    async def __addTradeList(cls, trade_list) -> None:
        logger.debug(f"{cls.__name__}.__addTradeList()")

        request = f"""
            INSERT INTO "TradeList" (trade_list_name)
            VALUES ('{trade_list.name}');
            """
        await cls.transaction(request)

    # }}}
    @classmethod  # __addTrade  # {{{
    async def __addTrade(cls, trade) -> None:
        logger.debug(f"{cls.__name__}.__addTrade()")

        # add trade
        request = f"""
            INSERT INTO "Trade" (
                trade_id,
                trade_list,
                figi,
                strategy,
                version,
                dt,
                status,
                trade_type,
                trade_info
                )
            VALUES (
                '{trade.trade_id}',
                '{trade.trade_list_name}',
                '{trade.instrument.figi}',
                '{trade.strategy}',
                '{trade.version}',
                '{trade.dt}',
                '{trade.status.name}',
                '{trade.type.name}',
                {cls.__formatInfo(trade)}
                );
            """
        await cls.transaction(request)

    # }}}
    @classmethod  # __addOrder  # {{{
    async def __addOrder(cls, order) -> None:
        logger.debug(f"{cls.__name__}.__addOrder()")

        # format prices
        if order.type.name == "MARKET":
            price, s_price, e_price = "NULL", "NULL", "NULL"
        elif order.type.name == "LIMIT":
            price, s_price, e_price = order.price, "NULL", "NULL"
        elif order.type.name in ("STOP", "STOP_LOSS", "TAKE_PROFIT"):
            price, s_price, e_price = (
                "NULL",
                order.stop_price,
                order.exec_price,
            )
            e_price = e_price if e_price else "NULL"
        else:
            assert False, f"WTF??? Order type='{order.type}'"

        # format trade_id
        # trade_id = f"" if order.trade_id else "NULL"

        # add
        request = f"""
            INSERT INTO "Order" (
                order_id,
                trade_id,
                account,
                figi,
                order_type,
                status,
                direction,
                lots,
                quantity,
                price,
                stop_price,
                exec_price,
                exec_lots,
                exec_quantity,
                broker_id,
                meta
                )
            VALUES (
                '{order.order_id}',
                '{order.trade_id}',
                '{order.account_name}',
                '{order.instrument.figi}',
                '{order.type.name}',
                '{order.status.name}',
                '{order.direction.name}',
                {order.lots},
                {order.quantity},
                {price},
                {s_price},
                {e_price},
                {order.exec_lots},
                {order.exec_quantity},
                '{order.broker_id}',
                $${order.meta}$$
                );
            """
        await cls.transaction(request)

    # }}}
    @classmethod  # __addOperation  # {{{
    async def __addOperation(cls, operation) -> None:
        logger.debug(f"{cls.__name__}.__addOperation()")

        request = f"""
            INSERT INTO "Operation" (
                operation_id,
                order_id,
                trade_id,
                account,
                figi,
                dt,
                direction,
                lots,
                quantity,
                price,
                amount,
                commission,
                meta
            )
            VALUES (
                '{operation.operation_id}',
                '{operation.order_id}',
                '{operation.trade_id}',
                '{operation.account_name}',
                '{operation.instrument.figi}',
                '{operation.dt}',
                '{operation.direction.name}',
                {operation.lots},
                {operation.quantity},
                {operation.price},
                {operation.amount},
                {operation.commission},
                $${operation.meta}$$
            );
        """
        await cls.transaction(request)

    # }}}
    @classmethod  # __addTest  # {{{
    async def __addTest(cls, test) -> None:
        logger.debug(f"{cls.__name__}.__addTest()")

        # add test
        request = f"""
            INSERT INTO "Test/Trader" (
                name,
                type,
                config
                )
            VALUES (
                '{test.name}',
                'TEST',
                '{test.toJson(test)}'
                );
            """
        await cls.transaction(request)

    # }}}
    @classmethod  # __addTestList  # {{{
    async def __addTestList(cls, test_list) -> None:
        logger.debug(f"{cls.__name__}.__addTestList()")

        # Add test list
        request = f"""
            INSERT INTO "TestList"(test_list_name)
            VALUES ('{test_list.name}');
        """
        await cls.transaction(request)

        # if test list is empty - return
        if len(test_list) == 0:
            return

        # Add tests
        pg_values = cls.__formatTestList(test_list)
        request = f"""
            INSERT INTO "TestList-Test" (test_list_name, test)
            VALUES
                {pg_values}
            ;
            """
        await cls.transaction(request)

    # }}}

    @classmethod  # __addAnalyticData  # {{{
    async def __addAnalyticData(cls, analytic_data) -> None:
        logger.debug(f"{cls.__name__}.__addAnalyticData()")

        pg_name = f"'{analytic_data.name}'"
        pg_figi = f"'{analytic_data.asset.figi}'"
        pg_data = f"'{analytic_data.json_str}'"

        # Add analytic data
        request = f"""
            INSERT INTO "AnalyticData" (analytic_name, figi, analyse_json)
            VALUES ({pg_name}, {pg_figi}, {pg_data})
            ;
            """
        await cls.transaction(request)

    # }}}

    @classmethod  # __getInstrument  # {{{
    async def __getInstrument(cls, Instrument, kwargs: dict) -> list:
        """Search Instrument

        Unlike the function Keeper.info(...), this method called from
        Keeper.get(Instrument, kwargs) looks for assets not in cache, but
        only among those for which exchange data are loaded. They are stored
        in table public."Asset"

        See also: __getAsset

        Args:
            Instrument (class Instrument): reference to class, to provide
                access to the method Instrument.fromRecord(...). It is need
                for return object of class Asset, instead asyncpg.Record.
                The title letter in the name of the argument recalls that
                this is the class.
            kwargs (str): for example: figi="BBG004730N88"

        Returns:
            Instrument
        """
        logger.debug(f"{cls.__name__}.__getInstrument()")

        exchange = kwargs.get("exchange")
        itype = kwargs.get("itype")
        ticker = kwargs.get("ticker")
        figi = kwargs.get("figi")

        # create condition
        if figi:
            pg_condition = f"figi = '{figi}'"
        elif exchange and itype and ticker:
            pg_condition = (
                f"exchange = '{exchange.name}' AND "
                f"type = '{itype.name}' AND "
                f"ticker = '{ticker}'"
            )
        else:
            assert False

        # Request instrument IDs
        request = f"""
            SELECT
                figi,
                type,
                exchange,
                ticker,
                name,
                lot,
                min_price_step
            FROM data."Instrument"
            WHERE
                {pg_condition}
            ORDER BY ticker
            ;
            """
        records = await cls.transaction(request)

        # Create 'list' of 'Instrument' from records
        instr_list = list()
        for record in records:
            instrument = Instrument.fromRecord(record)
            instr_list.append(instrument)

        return instr_list

    # }}}
    @classmethod  # __getDataInfo  # {{{
    async def __getDataInfo(cls, DataInfo, kwargs: dict):
        logger.debug(f"{cls.__name__}.__getDataInfo()")

        instrument = kwargs["instrument"]
        data_type = kwargs["data_type"]

        # Create condition
        pg_figi = f"data.\"DataInfo\".figi = '{instrument.figi}'"
        pg_data_type = f"data.\"DataInfo\".data_type = '{data_type.name}'"

        # Request data info
        request = f"""
            SELECT
                data."DataInfo".data_source,
                data."DataInfo".data_type,
                data."DataInfo".figi,
                data."DataInfo".first_dt,
                data."DataInfo".last_dt
            FROM data."DataInfo"
            WHERE
                {pg_figi} AND {pg_data_type}
            ;
            """

        records = await cls.transaction(request)
        if not records:
            return None

        assert len(records) == 1
        node = await DataInfo.fromRecord(records[0])
        return node

    # }}}
    @classmethod  # __getDataInfoList  # {{{
    async def __getDataInfoList(cls, DataInfoList, kwargs: dict):
        logger.debug(f"{cls.__name__}.__getDataInfoList()")

        instrument = kwargs.get("instrument")
        data_type = kwargs.get("data_type")

        # Create figi condition
        pg_figi = (
            f"data.\"DataInfo\".figi = '{instrument.figi}'"
            if instrument
            else "TRUE"
        )

        # Create type condition
        pg_data_type = (
            f"data.\"DataInfo\".type = '{data_type.name}'"
            if data_type
            else "TRUE"
        )

        # Request data info
        request = f"""
            SELECT
                data."DataInfo".data_source,
                data."DataInfo".data_type,
                data."DataInfo".figi,
                data."DataInfo".first_dt,
                data."DataInfo".last_dt,
                data."Instrument".ticker
            FROM data."DataInfo"
            JOIN data."Instrument"
                ON data."DataInfo".figi = data."Instrument".figi
            WHERE
                {pg_figi} AND {pg_data_type}
            ORDER BY data."Instrument".ticker
            ;
            """
        records = await cls.transaction(request)

        data_info = await DataInfoList.fromRecord(records)
        return data_info

    # }}}
    @classmethod  # __getDataSource  # {{{
    async def __getDataSource(cls, DataSource, kwargs: dict):
        logger.debug(f"{cls.__name__}.__getDataSource()")

        instrument = kwargs["instrument"]
        data_type = kwargs["data_type"]

        request = f"""
            SELECT (data_source)
            FROM data."DataInfo"
            WHERE
                figi = '{instrument.figi}' AND data_type = '{data_type.name}'
                ;
            """
        records = await cls.transaction(request)
        if not records:
            return None

        assert len(records) == 1
        source = DataSource.fromRecord(records[0])
        return source

    # }}}
    @classmethod  # __getDataType  # {{{
    async def __getDataType(cls, DataType, kwargs: dict):
        logger.debug(f"{cls.__name__}.__getDataType()")

        instrument = kwargs["instrument"]

        request = f"""
            SELECT (data_type) FROM data."DataInfo"
            WHERE
                figi = '{instrument.figi}';
            """
        records = await cls.transaction(request)

        data_types = list()
        for i in records:
            typ = DataType.fromStr(i["type"])
            data_types.append(typ)

        return data_types

    # }}}
    @classmethod  # __getDateTime  # {{{
    async def __getDateTime(cls, datetime, kwargs: dict):
        logger.debug(f"{cls.__name__}.__getData()")

        instrument = kwargs["instrument"]
        data_type = kwargs["data_type"]

        # Create figi condition
        pg_figi = f"figi = '{instrument.figi}'"

        # Create data type condition
        pg_data_type = f"type = '{data_type.name}'"

        # Request data info
        request = f"""
            SELECT * FROM data."DataInfo"
            WHERE
                {pg_figi} AND {pg_data_type};
            """
        records = await cls.transaction(request)
        assert len(records) == 1
        record = records[0]
        return [record["first_dt"], record["last_dt"]]

    # }}}
    @classmethod  # __getBarsRecords  # {{{
    async def __getBarsRecords(cls, _Bar, kwargs: dict):
        logger.debug(f"{cls.__name__}.__getBars()")

        instrument = kwargs["instrument"]
        data_type = kwargs.get("data_type")
        begin = kwargs.get("begin")
        end = kwargs.get("end")

        # create table name
        bars_table_name = cls.__getTableName(instrument, data_type=data_type)

        # create condition for begin-end:
        if begin is None and end is None:
            pg_period = "TRUE"
        elif begin is not None and end is None:
            pg_period = f"'{begin}' <= dt"
        elif begin is None and end is not None:
            pg_period = f"dt < '{end}'"
        else:
            pg_period = f"'{begin}' <= dt AND dt < '{end}'"

        # request bars records
        request = f"""
            SELECT dt, open, high, low, close, volume
            FROM {bars_table_name}
            WHERE
                {pg_period}
            ORDER BY dt
            ;
            """
        records = await cls.transaction(request)

        return records

    # }}}
    @classmethod  # __getBars  # {{{
    async def __getBars(cls, Bar, kwargs: dict):
        logger.debug(f"{cls.__name__}.__getBars()")

        # timeframe -> data_type, and add it to kwargs
        kwargs.setdefault("data_type", kwargs["timeframe"].toDataType())

        # request bars records
        records = await cls.__getBarsRecords(Bar, kwargs)

        # create bars
        bars = list()
        for record in records:
            bar = Bar.fromRecord(record)
            bars.append(bar)

        return bars

    # }}}
    @classmethod  # __getAsset  # {{{
    async def __getAsset(cls, Asset, kwargs: dict):
        """Search asset

        Unlike the function Keeper.info(...), this method called from
        Keeper.get(Asset, kwargs) looks for assets not in cache, but
        only among those for which exchange data are loaded. They are stored
        in table public."Asset"

        See also: __getInstrument

        Args:
            Asset (class Asset): reference to class, to provide access to the
                method Asset.fromRecord(...). It is need for return object of
                class Asset, instead asyncpg.Record.
                The title letter in the name of the argument recalls that
                this is the class.
            kwargs (str): for example: figi="BBG004730N88"

        Returns:
            Asset
        """

        logger.debug(f"{cls.__name__}.__getAsset()")

        asset_type = kwargs.get("asset_type")
        exchange = kwargs.get("exchange")
        ticker = kwargs.get("ticker")
        figi = kwargs.get("figi")

        # create condition
        if figi:
            pg_condition = f"\"Asset\".figi = '{figi}'"
        elif asset_type and exchange and ticker:
            pg_condition = (
                f"type = '{asset_type.name}' AND "
                f"exchange = '{exchange.name}' AND "
                f"ticker = '{ticker}'"
            )
        else:
            pg_condition = "TRUE"

        # request = f"""
        #     SELECT
        #         data."Instrument".figi,
        #         data."Instrument".exchange,
        #         data."Instrument".type,
        #         data."Instrument".ticker,
        #         data."Instrument".name,
        #         data."Instrument".lot,
        #         data."Instrument".min_price_step
        #     FROM data."Instrument"
        #     WHERE
        #         {pg_condition}
        #     ORDER BY ticker
        #     ;
        #     """
        request = f"""
            SELECT
                "Asset".figi,
                data."Instrument".exchange,
                data."Instrument".type,
                data."Instrument".ticker,
                data."Instrument".name,
                data."Instrument".lot,
                data."Instrument".min_price_step
            FROM "Asset"
            JOIN data."Instrument"
                ON data."Instrument".figi = "Asset".figi
            WHERE
                {pg_condition}
            ORDER BY ticker
            ;
            """
        asset_records = await cls.transaction(request)

        # if one return it
        if len(asset_records) == 1:
            asset = Asset.fromRecord(asset_records[0])
            return asset

        # if several return list
        all_assets = list()
        for i in asset_records:
            asset = Asset.fromRecord(i)
            all_assets.append(asset)
        return all_assets

    # }}}
    @classmethod  # __getAssetList  # {{{
    async def __getAssetList(cls, AssetList, kwargs: dict):
        logger.debug(f"{cls.__name__}.__getAssetList()")

        get_only_names = kwargs.get("get_only_names")

        # return list[str_names] if flag 'get_only_names'
        if get_only_names:
            request = """
                SELECT asset_list_name FROM "AssetList";
                """
            records = await cls.transaction(request)
            all_names = list()
            for i in records:
                name = i["asset_list_name"]
                all_names.append(name)
            return all_names

        # return None if not name in kwargs
        name = kwargs.get("name")
        if not name:
            return None

        # check existing asset list with this name
        # return None if not exist
        request = f"""
            SELECT asset_list_name  FROM "AssetList"
            WHERE
                asset_list_name = '{name}'
            ;
            """
        records = await cls.transaction(request)
        if not records:
            return None

        # request assets of asset list
        request = f"""
            SELECT
                "AssetList-Asset".asset_list_name,
                data."Instrument".figi,
                data."Instrument".exchange,
                data."Instrument".type,
                data."Instrument".ticker,
                data."Instrument".name,
                data."Instrument".lot,
                data."Instrument".min_price_step
            FROM "AssetList-Asset"
            JOIN data."Instrument"
                ON "AssetList-Asset".figi = data."Instrument".figi
            WHERE
                "AssetList-Asset".asset_list_name = '{name}'
            ORDER BY ticker
            ;
            """
        records = await cls.transaction(request)

        alist = await AssetList.fromRecord(name, records)
        return alist

    # }}}
    @classmethod  # __getAccount  # {{{
    async def __getAccount(cls, Account, kwargs: dict):
        logger.debug(f"{cls.__name__}.__getAccount()")

        name = kwargs.get("name")

        # Create condition for name
        pg_name = f"name = '{name}'" if name else "TRUE"

        # Request accounts
        request = f"""
            SELECT account_name, broker FROM "Account"
            WHERE
                {pg_name}
            ;
            """
        records = await cls.transaction(request)

        # Create 'list' of 'Account' from 'Records'
        accounts = list()
        for i in records:
            acc = Account.fromRecord(i)
            accounts.append(acc)

        return accounts

    # }}}
    @classmethod  # __getStrategySet  # {{{
    async def __getStrategySet(cls, StrategySet, kwargs: dict):
        logger.debug(f"{cls.__name__}.__getStrategySet()")

        name = kwargs["name"]

        # ensure exist
        request = f"""
            SELECT strategy_set_name
            FROM "StrategySet"
            WHERE strategy_set_name = '{name}';
            """
        records = await cls.transaction(request)
        if not records:
            return None

        # load items
        request = f"""
            SELECT strategy_set_name, strategy, version, figi, long, short
            FROM "StrategySet-Strategy"
            WHERE strategy_set_name = '{name}';
            """
        records = await cls.transaction(request)

        # create StrategySet from records
        s_set = StrategySet.fromRecord(name, records)
        return s_set

    # }}}
    @classmethod  # __getTradeList  # {{{
    async def __getTradeList(cls, TradeList, kwargs: dict):
        logger.debug(f"{cls.__name__}.__getTradeList()")

        name = kwargs["name"]

        # return None, if not found
        request = f"""
            SELECT trade_list_name
            FROM "TradeList"
            WHERE trade_list_name = '{name}';
            """
        records = await cls.transaction(request)
        if not records:
            return None

        # select record of trades, join asset
        request = f"""
            SELECT
                "Trade".trade_id,
                "Trade".trade_list,
                "Trade".strategy,
                "Trade".version,
                "Trade".dt,
                "Trade".status,
                "Trade".trade_type,
                "Trade".trade_info,
                data."Instrument".figi,
                data."Instrument".exchange,
                data."Instrument".type,
                data."Instrument".ticker,
                data."Instrument".name,
                data."Instrument".lot,
                data."Instrument".min_price_step
            FROM "Trade"
            JOIN data."Instrument"
                ON "Trade".figi = data."Instrument".figi
            WHERE trade_list = '{name}';
            """
        records = await cls.transaction(request)

        # create TradeList from trade records
        trade_list = await TradeList.fromRecord(name, records)
        return trade_list

    # }}}
    @classmethod  # __getTrade  # {{{
    async def __getTrade(cls, Trade, kwargs: dict):
        logger.debug(f"{cls.__name__}.__getTrade()")

        trade_id = kwargs.get("trade_id")
        strategy = kwargs.get("strategy")
        statuses = kwargs.get("status")
        begin = kwargs.get("begin")
        end = kwargs.get("end")

        def condition(strategy, statuses, begin, end) -> str:  # {{{
            # Create condition for strategy
            if strategy is None:
                pg_strategy = "TRUE"
            else:
                pg_strategy = (
                    f"(strategy = '{strategy.name}' AND "
                    f"version = '{strategy.version}')"
                )
            # Create condition for statuses, like this:
            # (status = 'INITIAL' OR status = 'NEW' OR status = 'OPEN')
            if statuses is None:
                pg_statuses = "TRUE"
            else:
                pg_statuses = f"(status = '{statuses[0].name}'"
                i = 1
                while i < len(statuses):
                    pg_statuses += f" OR status = '{statuses[i].name}'"
                    i += 1
                pg_statuses += ")"
            # Create condition for begin datetime
            pg_begin = f"dt >= '{begin}'" if begin else "TRUE"
            # Create condition for end datetime
            pg_end = f"dt < '{end}'" if end else "TRUE"

            pg_condition = (
                f"{pg_strategy} AND {pg_statuses} AND "
                f"{pg_begin} AND {pg_end}"
            )
            return pg_condition

        # }}}

        # Create condition
        if trade_id:
            pg_condition = f"trade_id = '{trade_id}'"
        else:
            pg_condition = condition(strategy, statuses, begin, end)

        # Request trades
        request = f"""
            SELECT
                trade_id,
                trade_list,
                figi,
                strategy,
                version,
                dt,
                status,
                type,
                info
            FROM "Trade"
            WHERE {pg_condition}
            ORDER BY trade_id
            ;
            """
        trade_records = await cls.transaction(request)

        # Create 'list' of 'Trade' objects from 'Records'
        all_trades = list()
        for i in trade_records:
            trade = await Trade.fromRecord(i)
            all_trades.append(trade)

        return all_trades

    # }}}
    @classmethod  # __getOperations  # {{{
    async def __getOperations(cls, Operation, kwargs: dict):
        logger.debug(f"{cls.__name__}.__getOperations()")

        trade_id = kwargs.get("trade_id")
        operation_id = kwargs.get("operation_id")

        if trade_id:
            pg_condition = f"trade_id = '{trade_id}'"
        elif operation_id:
            pg_condition = f"operation_id = '{operation_id}'"
        else:
            pg_condition = "TRUE"  # return all operations

        request = f"""
            SELECT
                operation_id,
                order_id,
                trade_id,
                account,
                figi,
                dt,
                direction,
                lots,
                quantity,
                price,
                amount,
                commission,
                meta
            FROM "Operation"
            WHERE {pg_condition}
            ORDER BY operation_id
            ;
            """
        op_records = await cls.transaction(request)

        # Create 'list' of 'Operation' objects from 'Records'
        op_list = list()
        for i in op_records:
            op = await Operation.fromRecord(i)
            op_list.append(op)

        return op_list

    # }}}
    @classmethod  # __getOrders  # {{{
    async def __getOrders(cls, Order, kwargs: dict):
        logger.debug(f"{cls.__name__}.__getOrders()")

        trade_id = kwargs.get("trade_id")
        order_id = kwargs.get("order_id")

        # create condition
        if trade_id:
            pg_condition = f"trade_id = '{trade_id}'"
        elif order_id:
            pg_condition = f"order_id = '{order_id}'"
        else:
            pg_condition = "TRUE"  # return all orders

        request = f"""
            SELECT
                order_id,
                trade_id,
                account,
                figi,
                order_type,
                status,
                direction,
                lots,
                quantity,
                price,
                stop_price,
                exec_price,
                exec_lots,
                exec_quantity,
                broker_id,
                meta
            FROM "Order"
            WHERE {pg_condition}
            ORDER BY order_id
            ;
            """
        order_records = await cls.transaction(request)

        # Create 'list' of 'Order' objects from 'Records'
        order_list = list()
        for i in order_records:
            order = await Order.fromRecord(i)
            order_list.append(order)

        return order_list

    # }}}
    @classmethod  # __getTest  # {{{
    async def __getTest(cls, Test, kwargs: dict):
        logger.debug(f"{cls.__name__}.__getTest()")

        get_only_names = kwargs.get("get_only_names")

        # return list[str_names] if kwargs["get_only_names"]
        if get_only_names:
            request = """
                SELECT name FROM "Test";
                """
            records = await cls.transaction(request)
            all_names = list()
            for i in records:
                name = i["name"]
                all_names.append(name)
            return all_names

        # return test if kwargs["name"]
        name = kwargs.get("name")
        assert name is not None
        request = f"""
            SELECT
                "Test".name,
                "Test".config
            FROM "Test"
            WHERE "Test".name = '{name}'
            ;
            """
        records = await cls.transaction(request)
        if not records:
            return None

        assert len(records) == 1
        record = records[0]
        test = await Test.fromRecord(record)

        return test

    # }}}
    @classmethod  # __getTestList  # {{{
    async def __getTestList(cls, TestList, kwargs: dict):
        logger.debug(f"{cls.__name__}.__getTestList()")

        get_only_names = kwargs.get("get_only_names")

        # return list[str_names] if flag 'get_only_names'
        if get_only_names:
            request = """
                SELECT test_list_name FROM "TestList";
                """
            records = await cls.transaction(request)
            all_names = list()
            for i in records:
                name = i["test_list_name"]
                all_names.append(name)
            return all_names

        # return None if not name in kwargs
        name = kwargs.get("name")
        if not name:
            return None

        # check existing asset list with this name
        # return None if not exist
        request = f"""
            SELECT test_list_name  FROM "TestList"
            WHERE
                test_list_name = '{name}'
            ;
            """
        records = await cls.transaction(request)
        if not records:
            return None

        # request tests of test list
        request = f"""
            SELECT
                "TestList-Test".test_list_name,
                "Test/Trader".name,
                "Test/Trader".config
            FROM "TestList-Test"
            JOIN "Test/Trader"
                ON "TestList-Test".test = "Test/Trader".name
            WHERE
                "TestList-Test".test_list_name = '{name}'
            ORDER BY name
            ;
            """
        records = await cls.transaction(request)

        alist = await TestList.fromRecord(name, records)
        return alist

    # }}}
    @classmethod  # __getAnalyticData  # {{{
    async def __getAnalyticData(cls, AnalyticData, kwargs: dict) -> None:
        logger.debug(f"{cls.__name__}.__getAnalyticData()")

        # if flag get only names
        only_names = kwargs.get("get_only_names")
        if only_names is not None:
            request = """
                SELECT
                    "AnalyticData".analytic_name
                FROM "AnalyticData"
                ;
                """
            records = await cls.transaction(request)
            all_names = list()
            for i in records:
                name = i["analytic_name"]
                if name not in all_names:
                    all_names.append(name)
            return all_names

        # else request analytic data
        name = kwargs.get("name")
        figi = kwargs.get("figi")
        request = f"""
            SELECT
                "AnalyticData".analytic_name,
                "AnalyticData".figi,
                "AnalyticData".analyse_json
            FROM "AnalyticData"
            WHERE
                "AnalyticData".analytic_name = '{name}' AND
                "AnalyticData".figi = '{figi}'
            ;
            """
        records = await cls.transaction(request)
        assert len(records) == 1
        record = records[0]

        analytic_data = await AnalyticData.fromRecord(record)
        return analytic_data

    # }}}

    # @classmethod  # __deleteExchange  # {{{
    # async def __deleteExchange(cls, exchange, kwargs: dict) -> None:
    #     logger.debug(f"{cls.__name__}.__deleteExchange()")
    #
    #     request = f"""
    #     DELETE FROM "Exchange" WHERE name = '{exchange.name}';
    #     """
    #     await cls.transaction(request)
    #
    # # }}}
    @classmethod  # __deleteAsset  # {{{
    async def __deleteAsset(cls, asset, kwargs: dict) -> None:
        logger.debug(f"{cls.__name__}.__deleteAsset()")

        request = f"""
        DELETE FROM "Asset"
        WHERE figi = '{asset.figi}';
        """
        await cls.transaction(request)

    # }}}
    @classmethod  # __deleteAssetList  # {{{
    async def __deleteAssetList(cls, alist, kwargs: dict) -> None:
        logger.debug(f"{cls.__name__}.__deleteAssetList()")

        request = f"""
            DELETE FROM "AssetList-Asset"
            WHERE asset_list_name = '{alist.name}';
            """
        await cls.transaction(request)

        request = f"""
            DELETE FROM "AssetList"
            WHERE asset_list_name = '{alist.name}';
            """
        await cls.transaction(request)

    # }}}
    @classmethod  # __deleteBarsData  # {{{
    async def __deleteBarsData(cls, _Bar, kwargs: dict) -> None:
        logger.debug(f"{cls.__name__}.__deleteBarsData()")

        instrument = kwargs["instrument"]
        data_type = kwargs["data_type"]
        begin = kwargs.get("begin")
        end = kwargs.get("end")

        # Create condition for begin-end:
        if begin and end:
            pg_period = f"'{begin}' <= dt AND dt < '{end}'"
        else:
            pg_period = "TRUE"

        # Delete bars
        bars_table_name = cls.__getTableName(instrument, data_type)
        request = f"""
            DELETE FROM {bars_table_name}
            WHERE
                {pg_period}
            """
        await cls.transaction(request)

        # if table is empty - delete table & data info
        request = f"""
            SELECT * FROM {bars_table_name}
            """
        records = await cls.transaction(request)
        if not records:
            # Delete bars table
            request = f"""
                DROP TABLE {bars_table_name};
                """
            await cls.transaction(request)
            # Delete data info
            request = f"""
                DELETE FROM data."DataInfo"
                WHERE
                    figi = '{instrument.figi}' AND
                    data_type = '{data_type.name}'
                """
            await cls.transaction(request)
        else:
            # if talbe not empty after delete bars update table
            # data."DataInfo" - information about availible market data
            request = f"""
                UPDATE data."DataInfo"
                SET
                    first_dt = (SELECT min(dt) FROM {bars_table_name}),
                    last_dt = (SELECT max(dt) FROM {bars_table_name})
                WHERE
                    figi = '{instrument.figi}' AND
                    data_type = '{data_type.name}'
                ;
                """
            await cls.transaction(request)

    # }}}
    @classmethod  # __deleteAccount  # {{{
    async def __deleteAccount(cls, account, kwargs: dict) -> None:
        logger.debug(f"{cls.__name__}.__deleteAccount()")

        request = f"""
        DELETE FROM "Account"
        WHERE name = '{account.name}';
        """
        await cls.transaction(request)

    # }}}
    @classmethod  # __deleteStrategy  # {{{
    async def __deleteStrategy(cls, Strategy, kwargs: dict) -> None:
        logger.debug(f"{cls.__name__}.__deleteStrategy()")

        name = kwargs.get("name")
        version = kwargs.get("version")
        assert (name is not None) | (version is not None)

        # delete version
        if name and version:
            request = f"""
                DELETE FROM "Strategy"
                WHERE
                    strategy_name = '{name}'
                    AND
                    version = '{version}';
            """
            await cls.transaction(request)
            return

        # delete all strategy group
        if version is None:
            request = f"""
                DELETE FROM "Strategy"
                WHERE
                    name = '{name}';
            """
            await cls.transaction(request)
            return

    # }}}
    @classmethod  # __deleteStrategySet  # {{{
    async def __deleteStrategySet(cls, s_set, kwargs: dict) -> None:
        logger.debug(f"{cls.__name__}.__deleteStrategySet()")

        # delete strategy set items
        request = f"""
            DELETE FROM "StrategySet-Strategy"
            WHERE strategy_set_name = '{s_set.name}';
        """
        await cls.transaction(request)

        # delete strategy set
        request = f"""
            DELETE FROM "StrategySet"
            WHERE strategy_set_name = '{s_set.name}';
        """
        await cls.transaction(request)

    # }}}
    @classmethod  # __deleteTradeList  # {{{
    async def __deleteTradeList(cls, trade_list, kwargs: dict) -> None:
        logger.debug(f"{cls.__name__}.__deleteTradeList()")

        only_trades = kwargs.get("only_trades")

        # delete trades
        request = f"""
            DELETE FROM "Trade"
            WHERE trade_list = '{trade_list.name}';
            """
        await cls.transaction(request)

        if only_trades:
            return

        # delete trade list
        request = f"""
            DELETE FROM "TradeList"
            WHERE trade_list_name = '{trade_list.name}';
            """
        await cls.transaction(request)

    # }}}
    @classmethod  # __deleteTrade  # {{{
    async def __deleteTrade(cls, trade, kwargs: dict) -> None:
        logger.debug(f"{cls.__name__}.__deleteTrade()")

        request = f"""
            DELETE FROM "Trade"
            WHERE trade_id = '{trade.trade_id}';
            """
        await cls.transaction(request)

    # }}}
    @classmethod  # __deleteOrder  # {{{
    async def __deleteOrder(cls, order, kwargs: dict) -> None:
        logger.debug(f"{cls.__name__}.__deleteOrder()")

        request = f"""
            DELETE FROM "Order"
            WHERE order_id = '{order.order_id}';
            """
        await cls.transaction(request)

    # }}}
    @classmethod  # __deleteOperation  # {{{
    async def __deleteOperation(cls, operation, kwargs: dict) -> None:
        logger.debug(f"{cls.__name__}.__deleteOperation()")

        request = f"""
            DELETE FROM "Operation"
            WHERE
                operation_id = '{operation.operation_id}';
        """
        await cls.transaction(request)

    # }}}
    @classmethod  # __deleteTest  # {{{
    async def __deleteTest(cls, test, kwargs: dict) -> None:
        logger.debug(f"{cls.__name__}.__deleteTest()")

        request = f"""
            DELETE FROM "Test"
            WHERE name = '{test.name}';
        """
        await cls.transaction(request)

    # }}}
    @classmethod  # __deleteTestList  # {{{
    async def __deleteTestList(cls, test_list, kwargs: dict) -> None:
        logger.debug(f"{cls.__name__}.__deleteTestList()")

        request = f"""
            DELETE FROM "TestList-Test"
            WHERE test_list_name = '{test_list.name}';
            """
        await cls.transaction(request)

        request = f"""
            DELETE FROM "TestList"
            WHERE test_list_name = '{test_list.name}';
            """
        await cls.transaction(request)

    # }}}
    @classmethod  # __deleteAnalyticData  # {{{
    async def __deleteAnalyticData(cls, analytic_data, kwargs: dict) -> None:
        logger.debug(f"{cls.__name__}.__deleteAnalyticData()")

        pg_name = f"'{analytic_data.name}'"
        pg_figi = f"'{analytic_data.asset.figi}'"

        # Add analytic data
        request = f"""
            DELETE FROM "AnalyticData"
            WHERE
                "AnalyticData".analytic_name = {pg_name} AND
                "AnalyticData".figi = {pg_figi}
            ;
            """
        await cls.transaction(request)

    # }}}

    @classmethod  # __updateCache  # {{{
    async def __updateCache(cls, cache, kwargs: dict) -> None:
        logger.debug(f"{cls.__name__}.__updateCache()")

        # Delete old cache
        request = f"""
            DELETE FROM data."InstrumentInfo"
            WHERE
                data_source = '{cache.source.name}' AND
                instrument_type = '{cache.type.name}'
                ;
            """
        await cls.transaction(request)

        # save new cache
        values = cls.__formatCache(cache)
        request = f"""
            INSERT INTO data."InstrumentInfo" (
                data_source, instrument_type, figi, instrument_info
                )
            VALUES
                {values}
                ;
        """
        await cls.transaction(request)

        # save new instruments if not exist
        for info in cache.formatted:
            request = f"""
            INSERT INTO data."Instrument" (
                figi, exchange, type,
                ticker, name, lot,
                min_price_step
                )
            VALUES (
                '{info["figi"]}', '{info["exchange"]}', '{info["type"]}',
                '{info["ticker"]}', '{info["name"]}', {info["lot"]},
                {info["min_price_step"]}
                );
            """
            try:
                await cls.transaction(request)
            except asyncpg.UniqueViolationError:
                # logger.warning(f"Asset '{info["ticker"]}' already exist")
                return

    # }}}
    @classmethod  # __updateStrategy  # {{{
    async def __updateStrategy(cls, Strategy, kwargs: dict) -> None:
        logger.debug(f"{cls.__name__}.__updateStrategy()")

        # rename version name
        strategy = kwargs.get("strategy")
        new_version_name = kwargs.get("new_version_name")
        if strategy and new_version_name:
            request = f"""
                UPDATE "Strategy"
                SET
                    version = '{new_version_name}'
                WHERE
                    name = '{strategy.name}'
                    AND
                    version = '{strategy.version}';
                """
            await cls.transaction(request)
            return

        # rename strategy name
        old_name = kwargs.get("old_strategy_name")
        new_name = kwargs.get("new_strategy_name")
        if old_name and new_name:
            request = f"""
                UPDATE "Strategy"
                SET
                    name = '{new_name}'
                WHERE
                    name = '{old_name}'
                """
            await cls.transaction(request)
            return

        assert False, f"undefine behavior for {kwargs} "

    # }}}
    @classmethod  # __updateTrade  # {{{
    async def __updateTrade(cls, trade, kwargs: dict) -> None:
        logger.debug(f"{cls.__name__}.__updateTrade()")

        request = f"""
            UPDATE "Trade"
            SET
                status = '{trade.status.name}',
                trade_info = {cls.__formatInfo(trade)}
            WHERE
                trade_id = '{trade.trade_id}';
            """
        await cls.transaction(request)

    # }}}
    @classmethod  # __updateOrder  # {{{
    async def __updateOrder(cls, order, kwargs: dict) -> None:
        logger.debug(f"{cls.__name__}.__updateOrder()")

        request = f"""
            UPDATE "Order"
            SET
                trade_id = {order.trade_id},
                status = '{order.status.name}',
                exec_lots = {order.exec_lots},
                exec_quantity = {order.exec_quantity},
                meta = $${order.meta}$$,
                broker_id = '{order.broker_id}'
            WHERE
                order_id = '{order.order_id}';
            """
        await cls.transaction(request)

    # }}}
    @classmethod  # __updateOperation  # {{{
    async def __updateOperation(cls, operation, kwargs: dict) -> None:
        logger.debug(f"{cls.__name__}.__updateOperation()")
        request = f"""
            UPDATE "Operation"
            SET
                trade_id = '{operation.trade_id}',
                commission = {operation.commission}
            WHERE
                operation_id = '{operation.operation_id}';
            """
        await cls.transaction(request)

    # }}}
    @classmethod  # __updateTest  # {{{
    async def __updateTest(cls, test, kwargs: dict) -> None:
        logger.debug(f"{cls.__name__}.__updateTest()")

        request = f"""
            UPDATE "Test"
            SET
                name = '{test.name}',
                config = '{test.toJson(test)}'
            WHERE
                name = '{test.name}';
            """

        await cls.transaction(request)

    # }}}

    @classmethod  # __createBarsDataTable  # {{{
    async def __createBarsDataTable(cls, bars_table_name: str) -> None:
        """Create a separate table for bars

        Every asset have market data candles in different timeframes.
        I'm create a table for each. For example asset 'SBER' has some tables:
            - data."MOEX_SHARE_SBER_1M"
            - data."MOEX_SHARE_SBER_10M"
            - data."MOEX_SHARE_SBER_1H"
            - data."MOEX_SHARE_SBER_D"
            - ...
        """
        logger.debug(f"{cls.__name__}.__createBarsDataTable()")

        request = f"""
        CREATE TABLE IF NOT EXISTS {bars_table_name} (
            dt TIMESTAMP WITH TIME ZONE PRIMARY KEY,
            open float,
            high float,
            low float,
            close float,
            volume bigint
            );
            """
        await cls.transaction(request)

    # }}}
    @classmethod  # __getClassName  # {{{
    def __getClassName(cls, obj) -> str:
        logger.debug(f"{cls.__name__}.__getClassName()")

        # Get object class name, 'obj' may be a ClassVar, when its Exchange
        # like class: Exchange.MOEX
        if inspect.isclass(obj):
            return obj.__name__

        return obj.__class__.__name__

    # }}}
    @classmethod  # __getTableName  # {{{
    def __getTableName(cls, instrument, data_type) -> str:
        # table name looks like: data."MOEX_SHARE_SBER_1M"
        logger.debug(f"{cls.__name__}.__getTableName()")

        bars_table_name = (
            f'data."{instrument.exchange.name}_'
            f'{instrument.type.name}_{instrument.ticker}_{data_type}"'
        )
        return bars_table_name

    # }}}
    @classmethod  # __formatBarsData  # {{{
    def __formatBarsData(cls, data) -> str:
        # Format bars data in postges value
        values = ""
        for b in data.bars:
            dt = f"'{b.dt.isoformat()}'"
            val = f"({dt},{b.open},{b.high},{b.low},{b.close},{b.vol}),\n"
            values += val

        values = values[0:-2]  # remove ",\n" after last value
        return values

    # }}}
    @classmethod  # __formatTradeInfo  # {{{
    def __formatInfo(cls, trade) -> str:
        logger.debug(f"{cls.__name__}.__formatInfo()")

        json_string = Cmd.toJson(trade.info, trade.encoderJson)
        pg_trade_info = f"'{json_string}'"

        return pg_trade_info

    # }}}
    @classmethod  # __formatCache  # {{{
    def __formatCache(cls, cache) -> str:
        logger.debug(f"{cls.__name__}.__formatCache()")

        # Format cache into postgres values
        values = ""
        for info in cache.formatted:
            pg_source = f"'{cache.source.name}'"
            pg_itype = f"'{cache.type.name}'"
            pg_figi = f"'{info["figi"]}'"
            json_str = Cmd.toJson(info, encoder=cache.encoderJson)
            pg_asset_info = f"'{json_str}'"

            val = f"({pg_source},{pg_itype},{pg_figi},{pg_asset_info}),\n"
            values += val

        values = values[0:-2]  # remove ",\n" after last value
        return values

    # }}}
    @classmethod  # __formatAssetList  # {{{
    def __formatAssetList(cls, alist) -> str:
        logger.debug(f"{cls.__name__}.__formatAssetList()")

        # create pg values
        pg_values = ""
        for asset in alist:
            val = f"('{alist.name}', '{asset.figi}'),\n"
            pg_values += val

        pg_values = pg_values[0:-2]  # remove ",\n" after last value
        return pg_values

    # }}}
    @classmethod  # __formatTestConfig  # {{{
    def __formatTestConfig(cls, test):
        logger.debug(f"{cls.__name__}.__formatTestConfig()")

        json_string = Cmd.toJson(test.cfg, test.encoderJson)
        pg_test_cfg = f"'{json_string}'"

        return pg_test_cfg

    # }}}
    @classmethod  # __formatTestList  # {{{
    def __formatTestList(cls, test_list) -> str:
        logger.debug(f"{cls.__name__}.__formatTestList()")

        # create pg values
        pg_values = ""
        for test in test_list:
            val = f"('{test_list.name}', '{test.name}'),\n"
            pg_values += val

        pg_values = pg_values[0:-2]  # remove ",\n" after last value
        return pg_values

    # }}}


Keeper.checkBackupData()
Keeper.checkBackupUser()


if __name__ == "__main__":
    ...
