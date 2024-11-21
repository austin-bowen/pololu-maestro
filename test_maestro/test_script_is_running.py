import pytest

from test_maestro.conftest import BaseMaestroTest


class TestMaestroScriptIsRunning(BaseMaestroTest):
    @pytest.mark.parametrize('read_bytes, expected', [
        (b'\x00', True),
        (b'\x01', False),
    ])
    def test(self, read_bytes: bytes, expected: bool):
        self.set_conn_read_bytes(read_bytes)

        assert self.maestro.script_is_running() == expected

        self.assert_wrote(b'\xAA\x0C\x2E')
        self.assert_read()
