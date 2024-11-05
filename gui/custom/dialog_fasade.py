#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

from avin.utils import logger
from gui.custom.dialog_confirm import ConfirmDialog
from gui.custom.dialog_info import InfoDialog
from gui.custom.dialog_name import NameDialog


class Dialog:
    @staticmethod  # confirm  # {{{
    def confirm(
        msg: str = "Are you serious?\nThen don't say that I didn't warn you!",
    ) -> bool:
        logger.debug("Dialog.confirm()")

        dial = ConfirmDialog()
        result = dial.confirm(message)
        return result

    # }}}
    @staticmethod  # info  # {{{
    def info(msg: str) -> None:
        logger.debug("Dialog.info()")

        dial = InfoDialog()
        dial.info(message)

    # }}}
    @staticmethod  # name  # {{{
    def name(default_name: str = "Enter name") -> str | None:
        logger.debug("Dialog.name()")

        dial = NameDialog()
        name = dial.enterName(default_name)
        return name

    # }}}


if __name__ == "__main__":
    ...
