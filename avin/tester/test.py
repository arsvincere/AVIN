#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================


class Test:
    class Status(enum.Enum):  # {{{
        UNDEFINE = 0
        NEW = 1
        EDITED = 2
        PROCESS = 3
        COMPLETE = 4

    # }}}
    def __init__(self, name):  # {{{
        self._status = Test.Status.NEW
        self._name = name
        self._cfg = collections.defaultdict(str)
        self._alist = AssetList(name="alist", parent=self)
        self._tlist = TradeList(name="tlist", parent=self)
        self._report = Report(test=self)

    # }}}
    @property  # status# {{{
    def status(self):
        return self._status

    @status.setter
    def status(self, new_status) -> bool:
        self._status = new_status

    # }}}
    @property  # name# {{{
    def name(self):
        return self._name

    @name.setter
    def name(self, new_name) -> bool:
        self._name = new_name

    # }}}
    @property  # description# {{{
    def description(self):
        return self._cfg["description"]

    @description.setter
    def description(self, description):
        self._cfg["description"] = description

    # }}}
    @property  # strategy# {{{
    def strategy(self):
        return self._cfg["strategy"]

    @strategy.setter
    def strategy(self, strategy):
        self._cfg["strategy"] = strategy

    # }}}
    @property  # version# {{{
    def version(self):
        # XXX: vestions list???
        # тогда можно будет внутри одного теста сравнивать разные версии
        # и прогонять тест сразу по всем версиям... это удобно будет вроде...
        # и как то сгруппированы они получаются.
        # test_smash_day
        #   - v1_tlist
        #       - short
        #       - long
        #       - 2018
        #       - 2019
        #   - v2_tlist
        #       - short
        #       - long
        #       - 2018
        #       - 2019
        return self._cfg["version"]

    @version.setter
    def version(self, version):
        self._cfg["version"] = version

    # }}}
    @property  # timeframe# {{{
    def timeframe(self):
        # XXX: time_step???
        # или вообще впизду, пусть всегда на шаге 1 мин
        # работает?
        return self._cfg["timeframe"]

    @timeframe.setter
    def timeframe(self, timeframe):
        self._cfg["timeframe"] = timeframe

    # }}}
    @property  # deposit# {{{
    def deposit(self):
        return self._cfg["deposit"]

    @deposit.setter
    def deposit(self, deposit):
        self._cfg["deposit"] = deposit

    # }}}
    @property  # commission# {{{
    def commission(self):
        return self._cfg["commission"]

    @commission.setter
    def commission(self, commission):
        self._cfg["commission"] = commission

    # }}}
    @property  # begin# {{{
    def begin(self):
        dt = datetime.fromisoformat(self._cfg["begin"])
        return dt.replace(tzinfo=UTC)

    @begin.setter
    def begin(self, begin):
        self._cfg["begin"] = begin

    # }}}
    @property  # end# {{{
    def end(self):
        dt = datetime.fromisoformat(self._cfg["end"])
        return dt.replace(tzinfo=UTC)

    @end.setter
    def end(self, end):
        self._cfg["end"] = end

    # }}}
    @property  # alist# {{{
    def alist(self):
        return self._alist

    @alist.setter
    def alist(self, alist):
        self._alist = alist

    # }}}
    @property  # tlist# {{{
    def tlist(self):
        return self._tlist

    # }}}
    @property  # peropt# {{{
    def report(self):
        return self._report

    # }}}
    @property  # dir_path# {{{
    def dir_path(self):
        assert self._name != ""
        path = Cmd.join(TEST_DIR, self.name)
        Cmd.createDirs(path)
        return path

    # }}}
    def updateReport(self):  # {{{
        self._report = Report(test=self)

    # }}}
    def clear(self):  # {{{
        TradeList.delete(self._tlist)
        Report.delete(self._report)
        self._tlist.clear()
        self._report.clear()
        self._status = Test.Status.NEW

    # }}}
    @staticmethod  # save# {{{
    def save(test) -> bool:
        test.__saveConfig()
        test.__saveAssetList()
        test.__saveTrades()
        test.__saveStatus()
        test.__saveReport()
        return True

    # }}}
    @staticmethod  # load#{{{
    def load(dir_path: str) -> Test:
        if not Cmd.isExist(dir_path):
            logger.error(f"Test.load: dir not found '{dir_path}'")
            return None
        name = Cmd.name(dir_path)
        test = Test(name)
        test._loadConfig()
        test._loadAssetList()
        test._loadTrades()
        test._loadStatus()
        test._loadReport()
        return test

    # }}}
    @staticmethod  # rename# {{{
    def rename(test, new_name: str):
        old_path = test.dir_path
        if Cmd.isExist(test.dir_path):
            Cmd.deleteDir(test.dir_path)
            test._name = new_name
            Test.save(test)
        else:
            test._name = new_name

    # }}}
    @staticmethod  # delete# {{{
    def delete(test) -> bool:
        Cmd.deleteDir(test.dir_path)
        return True

    # }}}
    def __saveConfig(self):  # {{{
        path = Cmd.join(self.dir_path, "config.cfg")
        Cmd.saveJSON(self._cfg, path)
        return True

    # }}}
    def __saveAssetList(self):  # {{{
        file_path = Cmd.join(self.dir_path, "alist.al")
        AssetList.save(self._alist, file_path)
        return True

    # }}}
    def __saveTrades(self):  # {{{
        file_path = Cmd.join(self.dir_path, "tlist.tl")
        TradeList.save(self._tlist, file_path)
        return True

    # }}}
    def __saveStatus(self):  # {{{
        file_path = Cmd.join(self.dir_path, "status")
        text = str(self._status)
        Cmd.save(text, file_path)
        return True

    # }}}
    def __saveReport(self):  # {{{
        file_path = Cmd.join(self.dir_path, "report.csv")
        Report.save(self._report, file_path)
        return True

    # }}}
    def _loadConfig(self):  # {{{
        path = Cmd.join(self.dir_path, "config.cfg")
        if Cmd.isExist(path):
            self._cfg = Cmd.loadJSON(path)
            return True
        else:
            logger.warning(f"Test._loadConfig: config not found '{path}'")
            self._cfg = collections.defaultdict(str)
            assert False

    # }}}
    def _loadAssetList(self):  # {{{
        file_path = Cmd.join(self.dir_path, "alist.al")
        if Cmd.isExist(file_path):
            self._alist = AssetList.load(file_path)
            return True
        else:
            logger.warning(f"Asset list not found: test={self.name}")
            assert False

    # }}}
    def _loadTrades(self):  # {{{
        file_path = Cmd.join(self.dir_path, "tlist.tl")
        if Cmd.isExist(file_path):
            self._tlist = TradeList.load(file_path, parent=self)
            return True
        else:
            self._tlist = TradeList(name="tlist", parent=self)
            return False

    # }}}
    def _loadStatus(self):  # {{{
        file_path = Cmd.join(self.dir_path, "status")
        if Cmd.isExist(file_path):
            text = Cmd.read(file_path)
            status = "Test." + text
            self._status = eval(status)
            return True
        else:
            logger.warning(f"Test._loadStatus: not found '{file_path}'")
            self._status = Test.Status.UNDEFINE

    # }}}
    def _loadReport(self):  # {{{
        file_path = Cmd.join(self.dir_path, "report.csv")
        if Cmd.isExist(file_path):
            self._report = Report.load(file_path, parent=self)
            return True
        else:
            self._report = Report(test=self)
            return False

    # }}}
