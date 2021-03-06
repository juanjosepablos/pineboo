"""Test kugar parser module."""

import unittest
from . import fixture_path
from pineboolib.loader.main import init_testing, finish_testing
from pineboolib import application


class TestParser(unittest.TestCase):
    """Test Parsing KUT to PDF."""

    @classmethod
    def setUpClass(cls) -> None:
        """Init test project."""
        init_testing()

    def test_kugar_parser_1(self) -> None:
        """Test parser."""

        from pineboolib.qsa import qsa

        from pineboolib.plugins.mainform.eneboo import eneboo
        import os

        application.PROJECT.main_form = eneboo
        # application.project.main_form.mainWindow = application.project.main_form.MainForm()
        # application.project.main_form.mainWindow.initScript()
        # application.project.main_window = application.project.main_form.mainWindow

        application.PROJECT.main_window = application.PROJECT.main_form.MainForm()  # type: ignore
        application.PROJECT.main_window.initScript()

        qsa_sys = qsa.sys
        path = fixture_path("principal.eneboopkg")
        self.assertTrue(os.path.exists(path))
        qsa_sys.loadModules(path, False)
        qsa.from_project("flfactppal").iface.valoresIniciales()

        cur_paises = qsa.FLSqlCursor("paises")
        """
        cur_paises.setModeAccess(cur_paises.Insert)
        cur_paises.refreshBuffer()
        cur_paises.setValueBuffer("codpais", "ES")
        cur_paises.setValueBuffer("nombre", "ESPAÑA")
        self.assertTrue(cur_paises.commitBuffer())
        cur_paises.setModeAccess(cur_paises.Insert)
        cur_paises.refreshBuffer()
        cur_paises.setValueBuffer("codpais", "PT")
        cur_paises.setValueBuffer("nombre", "PORTUGAL")
        self.assertTrue(cur_paises.commitBuffer())
        """
        cur_paises.select("1=1")
        cur_paises.first()
        init_ = cur_paises.valueBuffer("codpais")
        cur_paises.last()
        last_ = cur_paises.valueBuffer("codpais")
        qry_paises = qsa.FLSqlQuery("paises")
        qry_paises.setValueParam("from", init_)
        qry_paises.setValueParam("to", last_)

        rpt_viewer_ = qsa.FLReportViewer()
        rpt_viewer_.setReportTemplate("paises")
        rpt_viewer_.setReportData(qry_paises)

        rpt_viewer_.renderReport()
        if rpt_viewer_.rptEngine_ and hasattr(rpt_viewer_.rptEngine_, "parser_"):
            pdf_file = rpt_viewer_.rptEngine_.parser_.get_file_name()

        self.assertTrue(pdf_file)

    def test_parser_tools_1(self) -> None:
        """Test parser tools."""
        from pineboolib.application.parsers.kugarparser import kparsertools
        from pineboolib.core.utils.utils_base import load2xml
        from pineboolib.application.database import pnsqlquery, pnsqlcursor
        from pineboolib.qsa import qsa
        import datetime
        import os

        qry = pnsqlquery.PNSqlQuery()
        qry.setTablesList("paises")
        qry.setSelect("codpais, bandera")
        qry.setFrom("paises")
        qry.setWhere("1=1")
        self.assertTrue(qry.exec_())
        self.assertTrue(qry.first())
        data = qsa.sys.toXmlReportData(qry)
        parser_tools = kparsertools.KParserTools()
        xml_data = load2xml(data.toString()).getroot()

        child = xml_data.findall("Row")[0]
        element = parser_tools.convertToNode(child)
        self.assertTrue(element)
        fecha_ = str(datetime.date.__format__(datetime.date.today(), "%d.%m.%Y"))

        self.assertEqual(parser_tools.getSpecial("Fecha"), fecha_)
        self.assertEqual(parser_tools.getSpecial("[Date]"), fecha_)
        self.assertEqual(parser_tools.getSpecial("NúmPágina", 1), "1")
        self.assertEqual(parser_tools.getSpecial("PageNo", 6), "6")
        self.assertEqual(parser_tools.getSpecial("[NÃºmPÃ¡gina]", 12), "12")
        from PyQt5 import QtCore

        ret_ = QtCore.QLocale.system().toString(float("11.22"), "f", 2)

        self.assertEqual(parser_tools.calculated("11.22", 2, 2), ret_)
        self.assertEqual(parser_tools.calculated("2019-01-31T00:01:02", 3), "31-01-2019")
        self.assertEqual(parser_tools.calculated("codpais", 1, None, child), "ES")

        cur = pnsqlcursor.PNSqlCursor("paises")
        cur.select("1=1")
        cur.first()
        buffer = cur.buffer()
        if buffer:
            bandera = buffer.value("bandera")

            self.assertEqual(
                parser_tools.parseKey(str(bandera)),
                os.path.abspath("%s/%s.png" % (application.PROJECT.tmpdir, bandera)),
            )

    def test_parser_tools_2(self) -> None:
        """Test parser tools."""
        from pineboolib.application.parsers.kugarparser import kparsertools
        from xml.etree import ElementTree as et
        from decimal import Decimal

        parser_tools = kparsertools.KParserTools()
        self.assertEqual(parser_tools.convertPageSize(0, 0), [595, 842])
        self.assertEqual(parser_tools.convertPageSize(1, 0), [709, 499])
        self.assertEqual(parser_tools.convertPageSize(2, 0), [612, 791])
        self.assertEqual(parser_tools.convertPageSize(3, 0), [612, 1009])
        self.assertEqual(parser_tools.convertPageSize(5, 0), [2384, 3370])
        self.assertEqual(parser_tools.convertPageSize(6, 0), [1684, 2384])
        self.assertEqual(parser_tools.convertPageSize(7, 0), [1191, 1684])
        self.assertEqual(parser_tools.convertPageSize(8, 0), [842, 1191])
        self.assertEqual(parser_tools.convertPageSize(9, 0), [420, 595])
        self.assertEqual(parser_tools.convertPageSize(10, 0), [298, 420])
        self.assertEqual(parser_tools.convertPageSize(11, 0), [210, 298])
        self.assertEqual(parser_tools.convertPageSize(12, 0), [147, 210])
        self.assertEqual(parser_tools.convertPageSize(13, 0), [105, 147])
        self.assertEqual(parser_tools.convertPageSize(14, 0), [4008, 2835])
        self.assertEqual(parser_tools.convertPageSize(15, 0), [2835, 2004])
        self.assertEqual(parser_tools.convertPageSize(16, 0), [125, 88])
        self.assertEqual(parser_tools.convertPageSize(17, 0), [2004, 1417])
        self.assertEqual(parser_tools.convertPageSize(18, 0), [1417, 1001])
        self.assertEqual(parser_tools.convertPageSize(19, 0), [1001, 709])
        self.assertEqual(parser_tools.convertPageSize(20, 0), [499, 354])
        self.assertEqual(parser_tools.convertPageSize(21, 0), [324, 249])
        self.assertEqual(parser_tools.convertPageSize(22, 0), [249, 176])
        self.assertEqual(parser_tools.convertPageSize(23, 0), [176, 125])
        self.assertEqual(parser_tools.convertPageSize(24, 0), [649, 459])
        self.assertEqual(parser_tools.convertPageSize(25, 0), [113, 79])
        self.assertEqual(parser_tools.convertPageSize(28, 0), [1255, 791])
        self.assertEqual(parser_tools.convertPageSize(29, 0), [791, 1255])
        self.assertEqual(parser_tools.convertPageSize(30, 0, [100, 200]), [100, 200])
        self.assertEqual(parser_tools.convertPageSize(100, 0), [595, 842])
        xml = et.Element("AllItems")
        item_1 = et.SubElement(xml, "Item")
        item_1.set("valor", "21.00")
        item_1.set("level", "1")
        item_2 = et.SubElement(xml, "Item")
        item_2.set("valor", "26.29")
        item_2.set("level", "2")
        item_3 = et.SubElement(xml, "Item")
        item_3.set("valor", "5.84")
        item_3.set("level", "1")

        ret_0 = float(
            parser_tools.calculate_sum("valor", et.Element("Empty"), xml.findall("Item"), 0)
        )
        ret_1 = float(
            parser_tools.calculate_sum("valor", et.Element("Empty"), xml.findall("Item"), 1)
        )
        self.assertEqual(float(Decimal(format(ret_0, ".2f"))), 53.13)  # level > 0
        self.assertEqual(float(Decimal(format(ret_1, ".2f"))), 26.29)  # level > 1

    @classmethod
    def tearDownClass(cls) -> None:
        """Ensure test clear all data."""
        finish_testing()
