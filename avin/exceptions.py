#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================


class AssetError(Exception): ...


class BrokerError(Exception): ...


class GuiError(Exception): ...


__all__ = (
    "AssetError",
    "BrokerError",
    "GuiError",
)
