"""Test_pnsqlquery module."""

import unittest
from pineboolib.loader.main import init_testing
from pineboolib.application.database import pnsqlquery


class TestPNSqlQuery(unittest.TestCase):
    """TestPNSqlDrivers Class."""

    @classmethod
    def setUpClass(cls) -> None:
        """Ensure pineboo is initialized for testing."""
        init_testing()

    def test_basic_1(self) -> None:
        """Test basic_1."""
        from pineboolib.application.database import pnparameterquery
        from pineboolib.application.database import pngroupbyquery

        qry = pnsqlquery.PNSqlQuery("fltest2")

        from_param = pnparameterquery.PNParameterQuery("from", "from", 2)
        to_param = pnparameterquery.PNParameterQuery("to", "to", 2)
        from_param.setValue(0)
        to_param.setValue(1)
        qry.addParameter(from_param)
        qry.addParameter(to_param)
        d_ = {}
        d_[from_param.name()] = from_param.value()
        d_[to_param.name()] = to_param.value()
        qry.setParameterDict(d_)

        self.assertEqual(qry.valueParam("to"), 1)
        qry.setValueParam("to", 2)
        self.assertEqual(qry.valueParam("to"), 2)
        self.assertEqual(
            qry.sql(),
            "SELECT id,string_field,date_field,time_field,double_field,bool_field,uint_field,bloqueo FROM fltest"
            + " WHERE id>='0' AND id<='2' ORDER BY fltest.id",
        )

        gr_01 = pngroupbyquery.PNGroupByQuery(0, "string_field")

        qry.addGroup(gr_01)
        g_ = {}
        g_[gr_01.level()] = gr_01.field()

        qry2 = pnsqlquery.PNSqlQuery("fltest")
        qry2.setSelect(
            "id,string_field,date_field,time_field,double_field,bool_field,uint_field,bloqueo"
        )
        qry2.setFrom("fltest")
        qry2.setWhere("id>='0' AND id<='1'")
        qry2.setGroupDict(g_)

        self.assertEqual(
            qry2.sql(),
            "SELECT id,string_field,date_field,time_field,double_field,bool_field,uint_field,bloqueo FROM fltest"
            + " WHERE id>='0' AND id<='1' ORDER BY string_field",
        )

        self.assertEqual(qry.name(), "fltest2")
        self.assertEqual(qry.where(), "id>=[from] AND id<=[to]")
        self.assertEqual(qry.orderBy(), "fltest.id")
        qry.setSelect(["id", "fltest.string_field"])
        self.assertEqual(len(qry.parameterDict()), 2)
        self.assertEqual(len(qry.groupDict()), 1)
        self.assertEqual(qry.fieldList(), ["id", "fltest.string_field"])
        self.assertEqual(qry.posToFieldName(0), "id")
        self.assertEqual(qry.posToFieldName(1), "fltest.string_field")
        self.assertEqual(qry.fieldNameToPos("fltest.string_field"), 1)
        self.assertEqual(qry.fieldNameToPos("string_field"), 1)
        qry.setName("fltest2_dos")

        self.assertEqual(qry.name(), "fltest2_dos")
        self.assertEqual(len(qry.fieldMetaDataList()), 2)

    def test_basic_2(self) -> None:
        """Test basic_2."""

        qry = pnsqlquery.PNSqlQuery("fake")
        qry.setTablesList("fake_table")
        self.assertEqual(qry.tablesList(), ["fake_table"])
        qry.setTablesList(["fake_table_1", "fake_table_2"])
        self.assertEqual(qry.tablesList(), ["fake_table_1", "fake_table_2"])
        qry.setSelect("field_01")
        qry.setFrom("fake_table")
        qry.setWhere("1=1")
        qry.setOrderBy("field_01 ASC")
        self.assertEqual(
            qry.sql(), "SELECT field_01 FROM fake_table WHERE 1=1 ORDER BY field_01 ASC"
        )

        self.assertEqual(qry.fieldNameToPos("field_01"), 0)

        self.assertFalse(qry.exec_())
        self.assertEqual(qry.fieldList(), ["field_01"])
        self.assertFalse(qry.isValid())
        self.assertTrue(qry.isNull("field_01"))
        self.assertEqual(qry.value("field_01"), None)

    def test_basic_3(self) -> None:
        """Test basic_3."""

        qry = pnsqlquery.PNSqlQuery("fake")
        qry.setTablesList("fake_table")
        qry.setSelect("field_01")
        qry.setFrom("fake_table")
        qry.setWhere("1=1")
        qry.setOrderBy("field_01 ASC")
        self.assertEqual(
            qry.sql(), "SELECT field_01 FROM fake_table WHERE 1=1 ORDER BY field_01 ASC"
        )
        self.assertFalse(qry.isForwardOnly())
        qry.setForwardOnly(True)
        self.assertTrue(qry.isForwardOnly())
        qry.setForwardOnly(False)
        self.assertFalse(qry.isForwardOnly())
        self.assertFalse(qry.lastError())
        qry2 = pnsqlquery.PNSqlQuery("fake")
        self.assertFalse(qry2.exec_("SELEFT * FROM DDD"))
        self.assertTrue(qry.lastError())
        self.assertEqual(qry2.driver(), qry2.db().driver())
        self.assertEqual(qry2.numRowsAffected(), 0)
        self.assertTrue(qry2.lastQuery(), "SELEFT * FROM DDD")
        self.assertFalse(qry2.isValid())
        self.assertFalse(qry2.isActive())

    def test_move(self) -> None:
        """Test move functions."""
        qry = pnsqlquery.PNSqlQuery("")
        qry.setTablesList("flareas")
        qry.setSelect("idarea")
        qry.setFrom("flareas")
        qry.setWhere("1=1")
        qry.setOrderBy("idarea ASC")
        self.assertTrue(qry.exec_())
        self.assertTrue(qry.first())
        val_first = qry.value(0)
        size_ = qry.size()
        self.assertTrue(qry.last())
        val_last = qry.value(0)
        self.assertNotEqual(qry.value("idarea"), val_first)
        self.assertEqual(qry.value("idarea"), qry.value(0))
        self.assertTrue(qry.prev())
        self.assertTrue(qry.seek(0))
        self.assertFalse(qry.isNull("idarea"))
        self.assertEqual(qry.value(0), val_first)
        self.assertFalse(qry.seek(1000))
        self.assertFalse(qry.seek(1000, True))
        self.assertTrue(qry.seek(size_ - 1, True))  # last
        self.assertEqual(qry.value(0), val_last)

    def test_only_inspector(self) -> None:
        """Test only inspector."""

        qry = pnsqlquery.PNSqlQuery("fake")
        qry.exec_(
            "SELECT SUM(munitos), dia, noche FROM dias WHERE astro = 'sol' GROUP BY dias.minutos ORDER BY dia ASC, noche DESC"
        )
        self.assertEqual(qry.tablesList(), ["dias"])
        self.assertEqual(qry.from_(), "dias")
        self.assertEqual(qry.fieldList(), ["sum(munitos)", "dia", "noche"])
        self.assertEqual(qry.select(), "sum(munitos),dia,noche")
        self.assertEqual(qry.orderBy(), "dia asc, noche desc")
        self.assertEqual(qry.where(), "astro = 'sol'")

        qry_2 = pnsqlquery.PNSqlQuery("fake")
        qry_2.exec_(
            "SELECT SUM(munitos), dia, noche, p.nombre FROM dias INNER JOIN planetas AS "
            + "p ON p.id = dias.id WHERE astro = 'sol' GROUP BY dias.minutos ORDER BY dia ASC, noche DESC"
        )
        self.assertEqual(qry_2.tablesList(), ["dias", "planetas"])
        self.assertEqual(qry_2.fieldNameToPos("planetas.nombre"), 3)
        self.assertEqual(qry_2.fieldList(), ["sum(munitos)", "dia", "noche", "p.nombre"])
        self.assertEqual(qry_2.fieldNameToPos("nombre"), 3)
        self.assertEqual(qry_2.fieldNameToPos("p.nombre"), 3)
        self.assertEqual(qry_2.posToFieldName(3), "p.nombre")
        self.assertEqual(qry_2.posToFieldName(2), "noche")
        self.assertEqual(qry_2.where(), "astro = 'sol'")
        self.assertEqual(qry_2.from_(), "dias inner join planetas as p on p.id = dias.id")