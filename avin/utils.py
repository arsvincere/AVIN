#!/usr/bin/env python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

import os
import json
import gzip
import pickle
import shutil
import bisect
import zipfile
import subprocess
from collections import deque
from datetime import datetime

import avin.const
from avin.logger import logger


class Cmd():# {{{
    @staticmethod  #path# {{{
    def path(*path_parts):
        logger.debug(f"Cmd.path({path_parts})")
        path = os.path.join(*path_parts)
        return path
    # }}}
    @staticmethod  #makeDirs# {{{
    def makeDirs(path):
        """ Создает все необходимые папки для этого пути """
        if not os.path.exists(path):
            os.makedirs(path)
    # }}}
    @staticmethod  #name# {{{
    def name(file_path, extension=False):
        """ -- Doc
        Отделяет имя файла из пути к файлу
        /home/file_name.txt -> file_name.txt  # extension=True
        /home/file_name.txt -> file_name  # extension=False
        """
        logger.debug(f"Cmd.name({file_path}, extension={extension}")
        file_name = os.path.basename(file_path)  # == somename.xxx
        if extension:
            return file_name
        else:
            name = os.path.splitext(file_name)[0]  # == somename
            return name
    # }}}
    @staticmethod  #dirName# {{{
    def dirName(file_path):
        logger.debug(f"Cmd.dirName({file_path}")
        assert Cmd.isFile(file_path)
        dir_path = os.path.dirname(file_path)
        dir_name = os.path.basename(dir_path)
        return dir_name
    # }}}
    @staticmethod  #dirPath# {{{
    def dirPath(file_path):
        logger.debug(f"Cmd.dirPath({file_path}")
        assert Cmd.isFile(file_path)
        dir_path = os.path.dirname(file_path)
        return dir_path
    # }}}
    @staticmethod  #isExist# {{{
    def isExist(path):
        logger.debug(f"Cmd.isExist({path})")
        return os.path.exists(path)
    # }}}
    @staticmethod  #isFile# {{{
    def isFile(path):
        logger.debug(f"Cmd.isFile({path})")
        return os.path.isfile(path)
    # }}}
    @staticmethod  #isDir# {{{
    def isDir(path):
        logger.debug(f"Cmd.isFile({path})")
        return os.path.isdir(path)
    # }}}
    @staticmethod  #content# {{{
    def content(dir_path, full_path=False) -> list[str]:
        logger.debug(f"Cmd.getFiles({dir_path}, full_path={full_path})")
        contents = list()
        shutil._get_gid
        names = os.listdir(dir_path)
        for name in names:
            if full_path:
                path = Cmd.path(dir_path, name)
                contents.append(path)
            else:
                contents.append(name)
        return contents
    # }}}
    @staticmethod  #getFiles# {{{
    def getFiles(dir_path, full_path=False, include_sub_dir=False):
        logger.debug(
            f"Cmd.getFiles({dir_path}, "
            f"full_path={full_path}, "
            f"include_sub_dir={include_sub_dir})"
            )
        if include_sub_dir:
            return Cmd.__getFilesInDirIncludeSubDir(dir_path, full_path)
        else:
            return Cmd.__getFilesInDir(dir_path, full_path)
    # }}}
    @staticmethod  #getDirs# {{{
    def getDirs(dir_path, full_path=False):
        """ -- Doc
        Возвращает список папок в каталоге 'dir_path' без обхода подпапок
        """
        logger.debug(f"Cmd.getDirs({dir_path}, full_path={full_path})")
        list_dirs = list()
        names = os.listdir(dir_path)
        for name in names:
            path = Cmd.path(dir_path, name)
            if os.path.isdir(path):
                if full_path:
                    list_dirs.append(path)
                else:
                    list_dirs.append(name)
        return list_dirs
    # }}}
    @staticmethod  #findFile# {{{
    def findFile(file_name, dir_path):
        logger.debug(f"Cmd.findFile({file_name}, {dir_path})")
        for root, dirs, files in os.walk(dir_path):
            if file_name in files:
                return os.path.join(root, file_name)
            else:
                raise FileNotFoundError(f"Файл '{file_name}' не найден "
                                         "в директории '{dir_path}'")
    # }}}
    @staticmethod  #findDir# {{{
    def findDir(dir_name, root_dir):
        logger.debug(f"Cmd.findDir({dir_name}, {root_dir})")
        for root, dirs, files in os.walk(root_dir):
            if dir_name in dirs:
                return os.path.join(root, dir_name)
        raise FileNotFoundError(f"Папка '{dir_name}' не найдена "
                                 "в директории '{root_dir}'")
    # }}}
    @staticmethod  #select# {{{
    def select(files, name=None, extension=None):
        """ Возвращает список файлов c расширением 'extension' """
        selected = list()
        for file in files:
            if name and name == Cmd.name(file):
                selected.append(file)
            if extension and file.endswith(extension):
                selected.append(file)
        return selected
    # }}}
    @staticmethod  #rename# {{{
    def rename(old_path, new_path):
        """ Переименовывает old_path в new_path"""
        os.rename(old_path, new_path)
    # }}}
    @staticmethod  #replace# {{{
    def replace(src, dest, createDirs=True):
        """ Перемещает src в dest """
        if createDirs:
            Cmd.__createDirsForFilePath(dest)
        os.replace(src, dest)
    # }}}
    @staticmethod  #copy# {{{
    def copy(src_file, dest_file):
        """ Копирует src в dest """
        shutil.copy(src_file, dest_file)
    # }}}
    @staticmethod  #copyDir# {{{
    def copyDir(src, dest):
        """ Копирует src в dest """
        shutil.copytree(src, dest)
    # }}}
    @staticmethod  #delete# {{{
    def delete(file_path):
        """ Удаляет файла по указанному пути """
        os.remove(file_path)
        logger.debug(f"Delete: {file_path}")
    # }}}
    @staticmethod  #deleteDir# {{{
    def deleteDir(path):
        shutil.rmtree(path)
        logger.debug(f"Delete dir: {path}")
    # }}}
    @staticmethod  #extract# {{{
    def extract(archive_path, dest_dir):
        with zipfile.ZipFile(archive_path, "r") as file:
            file.extractall(dest_dir)
        logger.debug(f"Extracted archive: '{archive_path}'")
    # }}}
    @staticmethod  #read# {{{
    def read(file_path: str) -> str:
        """Read file as one string"""
        with open(file_path, "r", encoding="utf-8") as file:
            string = file.read()
        logger.debug(f"Cmd.read: {file_path}")
        return string
    # }}}
    @staticmethod  #write# {{{
    def write(string: str, file_path: str, create_dirs=True) -> str:
        """ Write string in file (overwrite) """
        if create_dirs:
            Cmd.__createDirsForFilePath(file_path)
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(string)
        logger.debug(f"Cmd.write: {file_path}")
    # }}}
    @staticmethod  #append# {{{
    def append(text: list[str], file_path: str):
        """ Append text in file """
        with open(file_path, "a", encoding="utf-8") as file:
            for line in text:
                file.write(line)
        logger.debug(f"Cmd.append(text): {file_path}")
        return True
    # }}}
    @staticmethod  #getTail# {{{
    def getTail(file_path, n):
        """ идиотский способ на самом деле.
        по сути он же читает весь файл построчно и добавляет его в
        очередь, у которой максимальная длина n... таким образом
        дойдя до конца файла в очереди останется n последних строк
        """
        with open(file_path, "r", encoding="utf-8") as file:
            text = list(deque(file, n))
        return text
    # }}}
    @staticmethod  #save# {{{
    def saveText(text: list[str], file_path: str, create_dirs=True):
        if create_dirs:
            Cmd.__createDirsForFilePath(file_path)
        with open(file_path, "w", encoding="utf-8") as file:
            for line in text:
                file.write(line)
        logger.debug(f"Save file: {file_path}")
    # }}}
    @staticmethod  #load# {{{
    def loadText(file_path: str) -> list[str]:
        """Read file by row, return list[str]"""
        text = list()
        with open(file_path, "r", encoding="utf-8") as file:
            for line in file:
                text.append(line)
        logger.debug(f"Cmd.load: {file_path}")
        return text
    # }}}
    @staticmethod  #saveJson# {{{
    def saveJson(obj, file_path, encoder=None, indent=4, create_dirs=True):
        if create_dirs:
            Cmd.__createDirsForFilePath(file_path)
        with open(file_path, "w", encoding="utf-8") as file:
            json.dump(
                obj=obj,
                fp=file,
                indent=indent,
                default=encoder,
                ensure_ascii=False,
                )
        logger.debug(f"Save json: {file_path}")
    # }}}
    @staticmethod  #loadJson# {{{
    def loadJson(file_path, decoder=None) -> object:
        with open(file_path, "r", encoding="utf-8") as file:
            obj = json.load(
                fp=file,
                object_hook=decoder,
                )
        logger.debug(f"Load json: {file_path}")
        return obj
    # }}}
    @staticmethod  #saveBin# {{{
    def saveBin(obj: object, path: str, compres=False, create_dirs=True):
        if create_dirs:
            Cmd.__createDirsForFilePath(path)
        fh = None
        try:
            if compres:
                fh = gzip.open(file_path, "wb")
            else:
                fh = open(file_path, "wb")
            pickle.dump(obj, fh, pickle.HIGHEST_PROTOCOL)
        except (EnvironmentError, pickle.PicklingError) as err:
            logger.exception(err)
            exit(1)
        finally:
            if fh is not None:
                fh.close()
    # }}}
    @staticmethod  #loadBin# {{{
    def loadBin(file_path) -> object:
        GZIP_MAGIC = b"\x1F\x8B"  # метка .gzip файлов
        fh = None
        try:
            fh = open(file_path, "rb")
            magic = fh.read(len(GZIP_MAGIC))
            if magic == GZIP_MAGIC:
                fh.close()
                fh = gzip.open(file_path, "rb")
            else:
                fh.seek(0)
            obj = pickle.load(fh)
            return obj
        except (EnvironmentError, pickle.UnpicklingError) as err:
            logger.exception(err)
            exit(1)
        finally:
            if fh is not None:
                fh.close()
    # }}}
    @staticmethod  #subprocess# {{{
    def subprocess(command: list[str]):
        logger.debug(f"Cmd.subprocess({command})")
        """
        import platform
        import subprocess
        # define a command that starts new terminal
        if platform.system() == "Windows":
            new_window_command = "cmd.exe /c start".split()
        else:
            new_window_command = "x-terminal-emulator -e".split()
        subprocess.check_call(new_window_command + command)
        """
        # command = [program, file_path]
        # new_window_command = "x-terminal-emulator -e".split()
        # new_window_command = "xterm -e".split()
        # new_window_command = ("xfce4-terminal", "-x")
        subprocess.call(command)
    # }}}
    @staticmethod  #__getFilesInDir# {{{
    def __getFilesInDir(dir_path, full_path):
        all_files = list()
        names = os.listdir(dir_path)
        for name in names:
            path = Cmd.path(dir_path, name)
            if os.path.isfile(path):
                if full_path:
                    all_files.append(path)
                else:
                    all_files.append(name)
        return all_files
    # }}}
    @staticmethod  #__getFilesInDirIncludeSubDir# {{{
    def __getFilesInDirIncludeSubDir(dir_path, full_path):
        all_files = list()
        for root, dirs, files in os.walk(dir_path):
            if full_path:
                all_files += [(lambda f: Cmd.path(root, f))(f) for f in files]
            else:
                all_files += files
        return all_files
    # }}}
    @staticmethod  #__createDirsForFilePath# {{{
    def __createDirsForFilePath(file_path) -> object:
        dir_path = os.path.dirname(file_path)
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
# }}}
# }}}

def now():# {{{
    return datetime.utcnow().replace(tzinfo=avin.const.UTC)
# }}}
def binarySearch(vector, x, key=None):# {{{
    left = 0
    right = len(vector) - 1
    while left <= right:
        mid = (right - left) // 2 + left
        mid_val = vector[mid] if key is None else key(vector[mid])
        if x == mid_val:
            return mid
        if x < mid_val:
            right = mid - 1
        else:
            left = mid + 1
    return None
# }}}
def findLeft(vector, x, key=None):# {{{
    """ Возвращает индекс элемента меньше или равного 'x'
    Если 'x', меньше самого левого элемента в векторе, возвращает None
    """
    i = bisect.bisect_right(vector, x, key=key)
    if i:
        return i-1
    return None
# }}}
def findRight(vector, x, key=None):# {{{
    """ Возвращает индекс элемента больше или равного 'x'
    Если 'x', больше самого правого элемента в векторе, возвращает None
    """
    i = bisect.bisect_left(vector, x, key=key)
    if i != len(vector):
        return i
    return None
# }}}
def encodeJSON(obj):# {{{
    assert False
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    if isinstance(obj, avin.core.TimeFrame):
        return str(obj)
    if isinstance(obj, enum.Enum):
        return str(obj)
    if isinstance(obj, (avin.core.Asset)):
        return avin.core.Asset.toJSON(obj)
# }}}
def decodeJSON(obj):# {{{
    assert False
    for k, v in obj.items():
        if isinstance(v, str) and "+00:00" in v:
            obj[k] = datetime.fromisoformat(obj[k])
        if k == "timeframe_list":
            tmp = list()
            for string in obj["timeframe_list"]:
                timeframe = avin.core.TimeFrame(string)
                tmp.append(timeframe)
            obj["timeframe_list"] = tmp
        if k == "timeframe":
            obj["timeframe"] = avin.core.TimeFrame(obj["timeframe"])
        if k == "asset":
            obj["asset"] = avin.core.Asset.fromJSON(obj["asset"])
        if isinstance(v, str) and "Type.SHORT" in v:
            obj[k] = avin.core.Signal.Type.SHORT
        if isinstance(v, str) and "Type.LONG" in v:
            obj[k] = avin.core.Signal.Type.LONG
    return obj
# }}}
def codeCounter(dir_path):# {{{
    count_file = 0
    count_str = 0
    for root, dirs, files in os.walk(dir_path):
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                text = Cmd.load(file_path)
                n = len(text)
                count_str += n
                count_file += 1
    return count_file, count_str
# }}}

if __name__ == "__main__":
    ...

