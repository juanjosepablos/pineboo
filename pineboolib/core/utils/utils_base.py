# -*- coding: utf-8 -*-
"""
Collection of utility functions.

Just an assortment of functions that don't depend on externals and don't fit other modules.
"""


from PyQt5 import QtGui, QtCore

from pineboolib.core import utils, settings

import os
import re
import sys
import io
import os.path
import hashlib
import traceback
import types

from typing import Optional, Union, Any, List, cast, Callable, TypeVar, TYPE_CHECKING

from xml.etree import ElementTree

if TYPE_CHECKING:
    from pineboolib.application.qsatypes.date import Date  # noqa: F401

logger = utils.logging.getLogger(__name__)
T1 = TypeVar("T1")

# FIXME: Move commaSeparator to Pineboo internals, not aqApp
DECIMAL_SEPARATOR = (
    "," if QtCore.QLocale.system().toString(float(0.01), "f", 2).find(",") > -1 else "."
)

BASE_DIR = None


def auto_qt_translate_text(text: Optional[str]) -> str:
    """Remove QT_TRANSLATE from Eneboo XML files. This function does not translate."""
    if not isinstance(text, str):
        text = str(text)

    if isinstance(text, str):
        if text.find("QT_TRANSLATE") != -1:
            match = re.search(r"""QT_TRANSLATE\w*\(.+,["'](.+)["']\)""", text)
            text = match.group(1) if match else ""

    return text


aqtt = auto_qt_translate_text


def one(x: List[T1], default: Any = None) -> Optional[T1]:
    """
    Retrieve first element of the list or None/default.

    Useful to avoid try/except cluttering and clean code.
    """
    try:
        return x[0]
    except IndexError:
        return default


def traceit(
    frame: types.FrameType, event: str, arg: Any
) -> Callable[[types.FrameType, str, Any], Any]:
    """
    Print a trace line for each Python line executed or call.

    This function is intended to be the callback of sys.settrace.
    """

    # if event != "line":
    #    return traceit
    try:
        import linecache

        lineno = frame.f_lineno
        filename = frame.f_globals["__file__"]
        # if "pineboo" not in filename:
        #     return traceit
        if filename.endswith(".pyc") or filename.endswith(".pyo"):
            filename = filename[:-1]
        name = frame.f_globals["__name__"]
        line = linecache.getline(filename, lineno)
        print("%s:%s:%s %s" % (name, lineno, event, line.rstrip()))
    except Exception:
        pass
    return traceit


class TraceBlock:
    """
    With Decorator to add traces on a particular block.

    Use it like:

    with TraceBlock():
        code
    """

    def __enter__(self) -> Callable[[types.FrameType, str, Any], Any]:
        """Create tracing context on enter."""
        # NOTE: "sys.systrace" function could lead to arbitrary code execution
        sys.settrace(traceit)  # noqa: DUO111
        return traceit

    def __exit__(self, type: Any, value: Any, traceback: Any) -> None:
        """Remove tracing context on exit."""
        # NOTE: "sys.systrace" function could lead to arbitrary code execution
        sys.settrace(None)  # noqa: DUO111


def trace_function(f: Callable) -> Callable:
    """Add tracing to decorated function."""

    def wrapper(*args: Any) -> Any:
        with TraceBlock():
            return f(*args)

    return wrapper


def copy_dir_recursive(from_dir: str, to_dir: str, replace_on_conflict: bool = False) -> bool:
    """
    Copy a folder recursively.

    *** DEPRECATED ***
    Use python shutil.copytree for this.
    """
    dir = QtCore.QDir()
    dir.setPath(from_dir)

    from_dir += QtCore.QDir.separator()
    to_dir += QtCore.QDir.separator()

    if not os.path.exists(to_dir):
        os.makedirs(to_dir)

    for file_ in dir.entryList(QtCore.QDir.Files):
        from_ = from_dir + file_
        to_ = to_dir + file_
        if str(to_).endswith(".src"):
            to_ = str(to_).replace(".src", "")
            # print("Destino", to_)

        if os.path.exists(to_):
            if replace_on_conflict:
                os.remove(to_)
            else:
                continue

        if not QtCore.QFile.copy(from_, to_):
            return False

    for dir_ in dir.entryList(
        cast(QtCore.QDir.Filter, QtCore.QDir.Dirs | QtCore.QDir.NoDotAndDotDot)
    ):
        from_ = from_dir + dir_
        to_ = to_dir + dir_

        if not os.path.exists(to_):
            os.makedirs(to_)

        if not copy_dir_recursive(from_, to_, replace_on_conflict):
            return False

    return True


def text2bool(text: str) -> bool:
    """Convert input text into boolean, if possible."""
    text = str(text).strip().lower()
    if text.startswith("t"):
        return True
    if text.startswith("f"):
        return False

    if text.startswith("y"):
        return True
    if text.startswith("n"):
        return False

    if text.startswith("1"):
        return True
    if text.startswith("0"):
        return False

    if text == "on":
        return True
    if text == "off":
        return False

    if text.startswith("s"):
        return True
    raise ValueError("Valor booleano no comprendido '%s'" % text)


def ustr(*t1: Union[bytes, str, int, "Date", None, float]) -> str:
    """Convert and concatenate types to text."""

    def ustr1(t: Union[bytes, str, int, "Date", None, float]) -> str:

        if isinstance(t, str):
            return t

        if isinstance(t, float):
            t_float = t
            try:
                t = int(t)

                if not t_float == t:
                    t = str(t_float)

            except Exception:
                pass

        # if isinstance(t, QtCore.QString): return str(t)
        if isinstance(t, bytes):
            return str(t, "UTF-8")
        try:
            if t is None:
                t = ""

            return "%s" % t
        except Exception:
            logger.exception("ERROR Coercing to string: %s", repr(t))
            return repr(t)

    return "".join([ustr1(t) for t in t1])


class StructMyDict(dict):
    """Dictionary that can be read/written using properties."""

    def __getattr__(self, name: str) -> Any:
        """Get property."""
        try:
            return self[name]
        except KeyError as e:
            raise AttributeError(e)

    def __setattr__(self, name: str, value: Any) -> None:
        """Set property."""
        self[name] = value


def load2xml(form_path_or_str: str) -> ElementTree.ElementTree:
    """Parse a Eneboo style XML."""

    """
    class xml_parser(ET.TreeBuilder):


        def start(self, tag, attrs):
            return super(xml_parser, self).start(tag, attrs)

        def end(self, tag):
            return super(xml_parser, self).end(tag)

        def data(self, data):
            super(xml_parser, self).data(data)

        def close(self):
            return super(xml_parser, self).close()
    """

    file_ptr: Optional[io.StringIO] = None
    if form_path_or_str.find("KugarTemplate") > -1 or form_path_or_str.find("DOCTYPE") > -1:
        form_path_or_str = _parse_for_duplicates(form_path_or_str)
        file_ptr = io.StringIO(form_path_or_str)
    elif not os.path.exists(form_path_or_str):
        raise Exception("File %s not found" % form_path_or_str[:200])

    try:
        parser = ElementTree.XMLParser()
        return ElementTree.parse(file_ptr or form_path_or_str, parser)
    except Exception:
        try:
            parser = ElementTree.XMLParser(encoding="ISO-8859-15")
            return ElementTree.parse(file_ptr or form_path_or_str, parser)
        except Exception:
            logger.exception(
                "Error cargando UI después de intentar con UTF8 e ISO \n%s", form_path_or_str
            )
            raise


def _parse_for_duplicates(text: str) -> str:
    """load2xml helper for Kugar XML."""
    ret_ = ""
    text = text.replace("+", "__PLUS__")
    text = text.replace("(", "__LPAREN__")
    text = text.replace(")", "__RPAREN__")
    text = text.replace("*", "__ASTERISK__")

    for section_orig in text.split(">"):
        # print("section", section)
        duplicate_ = False
        attr_list: List[str] = []

        # print("--->", section_orig)
        ret2_ = ""
        section = ""
        for a in section_orig.split(" "):

            c = a.count("=")
            if c > 1:
                # part_ = ""
                text_to_process = a
                for m in range(c):
                    pos_ini = text_to_process.find('"')
                    pos_fin = text_to_process[pos_ini + 1 :].find('"')
                    # print("Duplicado", m, pos_ini, pos_fin, text_to_process, "***" , text_to_process[0:pos_ini + 2 + pos_fin])
                    ret2_ += " %s " % text_to_process[0 : pos_ini + 2 + pos_fin]
                    text_to_process = text_to_process[pos_ini + 2 + pos_fin :]

            else:
                ret2_ += "%s " % a

        section += ret2_
        if section.endswith(" "):
            section = section[0 : len(section) - 1]

        if section_orig.endswith("/") and not section.endswith("/"):
            section += "/"

        # print("***", section)
        section = section.replace(" =", "=")
        section = section.replace('= "', '="')

        for attribute_ in section.split(" "):

            # print("attribute", attribute_)
            if attribute_.find("=") > -1:
                attr_name = attribute_[0 : attribute_.find("=")]
                if attr_name not in attr_list:
                    attr_list.append(attr_name)
                else:
                    if attr_name != "":
                        # print("Eliminado attributo duplicado", attr_name)
                        duplicate_ = True

            if not duplicate_:
                if not section.endswith(attribute_):
                    ret_ += "%s " % attribute_
                else:
                    ret_ += "%s" % attribute_
            else:
                if attribute_.endswith("/"):
                    ret_ += "/"

            duplicate_ = False

        if (section.find(">") == -1 and section.find("<") > -1) or section.endswith("--"):
            ret_ += ">"

    # print(ret_)
    return ret_


def pretty_print_xml(elem: ElementTree.Element, level: int = 0) -> None:
    """
    Generate pretty-printed version of given XML.

    copy and paste from http://effbot.org/zone/element-lib.htm#prettyprint
    it basically walks your tree and adds spaces and newlines so the tree is
    printed in a nice way
    """
    i = "\n" + level * "  "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "  "
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for elem in elem:
            pretty_print_xml(elem, level + 1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i


def format_double(d: Union[int, str, float], part_integer: int, part_decimal: int) -> str:
    """Convert number into string with fixed point style."""
    if isinstance(d, str) and d == "":
        return d
    # import locale
    # p_int = field_meta.partInteger()
    # p_decimal = field_meta.partDecimal()
    comma_ = "."
    d = str(d)
    found_comma = True if d.find(comma_) > -1 else False
    # if aqApp.commaSeparator() == comma_:
    #    d = d.replace(",", "")
    # else:
    #    d = d.replace(".","")
    #    d = d.replace(",",".")

    d = round(float(d), part_decimal)

    str_d = str(d)
    str_integer = str_d[0 : str_d.find(comma_)] if str_d.find(comma_) > -1 else str_d
    str_decimal = "" if str_d.find(comma_) == -1 else str_d[str_d.find(comma_) + 1 :]

    if part_decimal > 0:
        while part_decimal > len(str_decimal):
            str_decimal += "0"

    str_integer = format_int(str_integer, part_integer)

    # Fixme: Que pasa cuando la parte entera sobrepasa el limite, se coge el maximo valor o
    ret_ = "%s%s%s" % (
        str_integer,
        DECIMAL_SEPARATOR if found_comma or part_decimal > 0 else "",
        str_decimal if part_decimal > 0 else "",
    )
    return ret_


def format_int(value: Union[str, int, float, None], part_integer: int = None) -> str:
    """Convert integer into string."""
    if value is None:
        return ""
    str_integer = "{:,d}".format(int(value))

    if DECIMAL_SEPARATOR == ",":
        str_integer = str_integer.replace(",", ".")
    else:
        str_integer = str_integer.replace(".", ",")

    return str_integer


# def unformat_number(new_str: str, old_str: Optional[str], type_: str) -> str:
#    """Undoes some of the locale formatting to ensure float(x) works."""
#    ret_ = new_str
#    if old_str is not None:

#        if type_ in ("int", "uint"):
#            new_str = new_str.replace(",", "")
#            new_str = new_str.replace(".", "")

#            ret_ = new_str

#        else:
#            end_comma = False
#            if new_str.endswith(",") or new_str.endswith("."):
# Si acaba en coma, lo guardo
#                end_comma = True

#            ret_ = new_str.replace(",", "")
#            ret_ = ret_.replace(".", "")
#            if end_comma:
#                ret_ = ret_ + "."
# else:
#    comma_pos = old_str.find(".")
#    if comma_pos > -1:
#            print("Desformateando", new_str, ret_)

# else:
# pos_comma = old_str.find(".")

# if pos_comma > -1:
#    if pos_comma > new_str.find("."):
#        new_str = new_str.replace(".", "")

#        ret_ = new_str[0:pos_comma] + "." + new_str[pos_comma:]

# print("l2", ret_)
#    return ret_


# FIXME: Belongs to RPC drivers
# def create_dict(method: str, fun: str, id: int, arguments: List[Any] = []) -> Dict[str, Union[str, int, List[Any], Dict[str, Any]]]:
#     data = [{"function": fun, "arguments": arguments, "id": id}]
#     return {"method": method, "params": data, "jsonrpc": "2.0", "id": id}


def is_deployed() -> bool:
    """Return wether we're running inside a PyInstaller bundle."""
    return getattr(sys, "frozen", False)


def get_base_dir() -> str:
    """Obtain pinebolib installation path."""
    global BASE_DIR
    if not BASE_DIR:
        BASE_DIR = "%s/../.." % os.path.dirname(__file__)

        if is_deployed():
            if BASE_DIR.startswith(":"):
                BASE_DIR = os.path.realpath(".%s" % BASE_DIR[1:])

            logger.info("BaseDir %s", BASE_DIR)
    return BASE_DIR


def filedir(*path: str) -> str:
    """
    Get file full path reltive to the project.

    filedir(path1[, path2, path3 , ...])
    @param array de carpetas de la ruta
    @return devuelve la ruta absoluta resultado de concatenar los paths que se le pasen y aplicarlos desde la ruta del proyecto.
    Es útil para especificar rutas a recursos del programa.
    """
    ruta_ = os.path.realpath(os.path.join(get_base_dir(), *path))
    return ruta_


def download_files() -> None:
    """Download data for PyInstaller bundles."""
    if os.path.exists(filedir("forms")):
        return

    if not os.path.exists(filedir("../pineboolib")):
        os.mkdir(filedir("../pineboolib"))

    copy_dir_recursive(":/pineboolib", filedir("../pineboolib"))

    tmp_dir = settings.config.value("ebcomportamiento/temp_dir")

    if not os.path.exists(tmp_dir):
        os.mkdir(tmp_dir)


def pixmap_fromMimeSource(name: str) -> Any:
    """Convert mime source into a pixmap."""
    file_name = filedir("./core/images/icons", name)
    return QtGui.QPixmap(file_name) if os.path.exists(file_name) else None


def sha1(x: str) -> str:
    """Get SHA1 hash from string in hex form."""
    return hashlib.sha1(str(x).encode("UTF-8")).hexdigest()


def print_stack(maxsize: int = 1) -> None:
    """Print Python stack, like a traceback."""
    for tb in traceback.format_list(traceback.extract_stack())[1:-2][-maxsize:]:
        print(tb.rstrip())
