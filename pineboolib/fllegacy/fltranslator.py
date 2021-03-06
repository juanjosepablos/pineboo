"""Fltranslator module."""
# -*- coding: utf-8 -*-

import os
from pineboolib.core.utils.utils_base import filedir
from pineboolib.core.settings import config
from pineboolib import application

from PyQt5 import Qt
from pineboolib import logging
from typing import Dict, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from PyQt5 import QtWidgets  # noqa: F401


class FLTranslator(Qt.QTranslator):
    """FLTranspator class."""

    _multi_lang: bool
    _sys_trans: bool
    _id_module: str
    _lang: str
    _translation_from_qm: bool
    _ts_translation_contexts: Dict[str, Dict[str, str]]

    def __init__(
        self,
        parent: Optional["QtWidgets.QWidget"] = None,
        name: Optional[str] = None,
        multiLang: bool = False,
        sysTrans: bool = False,
    ) -> None:
        """Inicialize."""
        super(FLTranslator, self).__init__()
        self.logger = logging.getLogger("FLTranslator")
        self._prj = parent
        if not name:
            raise Exception("Name is mandatory")
        self._id_module = name[: name.rfind("_")]
        self._lang = name[name.rfind("_") + 1 :]
        self._multi_lang = multiLang
        self._sys_trans = sysTrans
        self._ts_translation_contexts = {}
        self._translation_from_qm = config.value("ebcomportamiento/translations_from_qm", False)

    def loadTsContent(self, key: str) -> bool:
        """
        Load the contents of an existing translation file into the disk cache into the translator.

        The file must be entered in the disk cache before calling this method, in
        Otherwise, nothing will be done.

        @param key Sha1 key that identifies the file in the disk cache
        @return TRUE if the operation was successful
        """
        if self._id_module == "sys":
            ts_file = filedir("./system_module/translations/%s.%s" % (self._id_module, self._lang))
        else:
            if application.PROJECT.conn_manager is None:
                raise Exception("Project is not connected yet")
            ts_file = filedir(
                "%s/cache/%s/%s/file.ts/%s.%s/%s"
                % (
                    application.PROJECT.tmpdir,
                    application.PROJECT.conn_manager.useConn("default").DBName(),
                    self._id_module,
                    self._id_module,
                    self._lang,
                    key,
                )
            )
        # qmFile = self.AQ_DISKCACHE_DIRPATH + "/" + key + ".qm"

        ret_ = False
        if not self._translation_from_qm:
            ret_ = self.load_ts("%s.ts" % ts_file)
            if not ret_:
                self.logger.warning("For some reason, i cannot load '%s.ts'", ts_file)
        else:

            qm_file = "%s.qm" % ts_file
            if os.path.exists(qm_file):
                if ts_file in (None, ""):
                    return False

            else:
                from . import fltranslations

                trans = fltranslations.FLTranslations()
                trans.lrelease("%s.ts" % ts_file, qm_file, not self._multi_lang)

            ret_ = self.load(qm_file)
            if not ret_:
                self.logger.warning("For some reason, i cannot load '%s'", qm_file)

        return ret_

    def translate(
        self, context: str, source_text: str, disambiguation: str = None, n: int = -1
    ) -> Optional[str]:
        """Return a translated text."""

        if context.endswith("PlatformTheme"):
            context = "QMessageBox"
        ret_ = None
        if self._translation_from_qm:
            ret_ = super().translate(context, source_text)
            if ret_ == "":
                ret_ = None
        else:
            if context in self._ts_translation_contexts.keys():
                if source_text in self._ts_translation_contexts[context]:
                    ret_ = self._ts_translation_contexts[context][source_text]

        return ret_

    def load_ts(self, file_name: str) -> bool:
        """Load a translation file from a path."""

        try:
            from pineboolib.core.utils.utils_base import load2xml

            root_ = load2xml(file_name)
            for context in root_.findall("context"):
                name_elem = context.find("name")
                if name_elem is None:
                    self.logger.warning("load_ts: <name> not found, skipping")
                    continue
                context_dict_key = name_elem.text
                if not context_dict_key:
                    continue
                if context_dict_key not in self._ts_translation_contexts.keys():
                    self._ts_translation_contexts[context_dict_key] = {}
                for message in context.findall("message"):
                    translation_elem, source_elem = (
                        message.find("translation"),
                        message.find("source"),
                    )
                    translation_text = translation_elem is not None and translation_elem.text
                    source_text = source_elem is not None and source_elem.text
                    if translation_text and source_text:
                        self._ts_translation_contexts[context_dict_key][
                            source_text
                        ] = translation_text

            return True
        except Exception:
            return False
