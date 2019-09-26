"""Test_flformrecorddb module."""
import unittest
from pineboolib.loader.main import init_testing, finish_testing


class TestFLFormDB(unittest.TestCase):
    """TestFLFormDB Class."""

    @classmethod
    def setUpClass(cls) -> None:
        """Ensure pineboo is initialized for testing."""
        init_testing()

    def test_close_again(self) -> None:
        """Test closed 2 times."""
        from pineboolib.fllegacy import flformdb
        from pineboolib import application

        action = application.project.conn.manager().action("flareas")
        form = flformdb.FLFormDB(None, action)
        self.assertTrue(form)
        form.load()
        self.assertTrue(form._loaded)
        form.close()
        self.assertFalse(form._loaded)
        form.close()
        self.assertFalse(form._loaded)

    @classmethod
    def tearDownClass(cls) -> None:
        """Ensure test clear all data."""
        finish_testing()


if __name__ == "__main__":
    unittest.main()
