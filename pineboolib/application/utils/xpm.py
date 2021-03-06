"""Manage cached xpm."""

import os
import os.path

from pineboolib.core.settings import config
from pineboolib import logging, application

LOGGER = logging.getLogger("xpm")


def cache_xpm(value: str) -> str:
    """
    Return a path to a file with the content of the specified string.

    @param value. text string with the xpm or path to this.
    @return file path contains Xpm
    """

    if not value:
        LOGGER.warning("the value is empty!")
        return ""

    xpm_name = value[: value.find("[]")]
    xpm_name = xpm_name[xpm_name.rfind(" ") + 1 :]

    conn = application.PROJECT.conn_manager.mainConn()
    if conn is None:
        raise Exception("Project is not connected yet")

    cache_dir = "%s/cache/%s/cacheXPM" % (application.PROJECT.tmpdir, conn.DBName())
    if not os.path.exists(cache_dir):
        os.mkdir(cache_dir)

    if value.find("cacheXPM") > -1:
        file_name = value
    else:
        file_name = "%s/%s.xpm" % (cache_dir, xpm_name)

    if not os.path.exists(file_name) or config.value("ebcomportamiento/no_img_cached", False):
        file_ = open(file_name, "w")
        file_.write(value)
        file_.close()

    return file_name
