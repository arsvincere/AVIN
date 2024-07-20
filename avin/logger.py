#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

import logging
import os
from datetime import date

from avin.const import Dir, Usr

__all__ = ("logger",)

_CONFIGURED = False
_NAME = "avin-logger"
_LOG_DIR = Dir.LOG
_HISTORY = Usr.LOG_HISTORY

logger = logging.getLogger(_NAME)


def configure(logger):  # {{{
    if not _CONFIGURED:
        _configStreamLog(logger)

        debug_log_path = os.path.join(_LOG_DIR, "debug.log")
        _configDebugLog(logger, debug_log_path)

        info_log_path = os.path.join(_LOG_DIR, f"{date.today()}.log")
        _configInfoLog(logger, info_log_path)

        _deleteOldLogfiles(_LOG_DIR, _HISTORY)
        __CONFIGURED = True


# }}}
def _configStreamLog(logger):  # {{{
    stream_formatter = logging.Formatter(
        "%(module)s: %(asctime)s [%(levelname)s] %(message)s",
        datefmt="%H:%M:%S",
    )
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(stream_formatter)
    stream_handler.setLevel(logging.INFO)
    logger.addHandler(stream_handler)
    logger.setLevel(logging.DEBUG)


# }}}
def _configDebugLog(logger, file_path):  # {{{
    file_formatter = logging.Formatter(
        "%(module)s: %(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    file_handler = logging.FileHandler(file_path, mode="w")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)


# }}}
def _configInfoLog(logger, file_path):  # {{{
    file_formatter = logging.Formatter(
        "%(module)s: %(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    file_handler = logging.FileHandler(file_path, mode="a")
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)


# }}}
def _deleteOldLogfiles(log_dir: str, max_files: int) -> None:  # {{{
    contents = os.listdir(log_dir)
    contents = [os.path.join(log_dir, i) for i in contents]
    files = [i for i in contents if os.path.isfile(i)]
    log_files = sorted([i for i in files if i.endswith(".log")])
    while len(log_files) > max_files:
        os.remove(log_files[0])  # remove oldest file in sorted file list
        log_files.pop(0)


# }}}

if __name__ == "avin.logger":
    configure(logger)
