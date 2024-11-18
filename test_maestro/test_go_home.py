from test_maestro.conftest import BaseMaestroTest


class TestMaestroGoHome(BaseMaestroTest):
    def test_stop_script(self):
        self.maestro.go_home()
        self.assert_wrote(b'\xAA\x0C\x22')
