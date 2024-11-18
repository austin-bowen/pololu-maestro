from test_maestro.conftest import BaseMaestroTest


class TestMaestroStopScript(BaseMaestroTest):
    def test_stop_script(self):
        self.maestro.stop_script()
        self.assert_wrote(b'\xAA\x0C\x24')
