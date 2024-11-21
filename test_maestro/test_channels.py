import pytest

from maestro import MicroMaestro, MiniMaestro, SerialCommands
from test_maestro.conftest import BaseMaestroTest


class TestMaestroChannels(BaseMaestroTest):
    def test_micro_maestro_channels(self):
        maestro = MicroMaestro(self.conn, device=SerialCommands.DEFAULT_DEVICE_NUMBER, safe_close=False)
        assert maestro.channels == 6

    # parameterized
    @pytest.mark.parametrize('channels', [12, 18, 24])
    def test_mini_maestro_channels(self, channels: int):
        maestro = MiniMaestro(channels, self.conn, device=SerialCommands.DEFAULT_DEVICE_NUMBER, safe_close=False)
        assert maestro.channels == channels
