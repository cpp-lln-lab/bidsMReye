from __future__ import annotations

import logging

from rich.logging import RichHandler
from rich.traceback import install

from bidsmreye.defaults import default_log_level


def bidsmreye_log(name: str | None = None) -> logging.Logger:
    """Create log.

    :param name: _description_, defaults to None
    :type name: _type_, optional

    :return: _description_
    :rtype: _type_
    """
    # let rich print the traceback
    install(show_locals=True)

    FORMAT = "bidsMReye - %(asctime)s - %(message)s"

    log_level = default_log_level()

    if not name:
        name = "rich"

    logging.basicConfig(
        level=log_level, format=FORMAT, datefmt="[%X]", handlers=[RichHandler()]
    )

    return logging.getLogger(name)
