import pytest

from test_maestro.conftest import BaseMaestroTest


class TestMaestroStopChannel(BaseMaestroTest):
    @pytest.mark.parametrize('channel, suffix', [
        (0, b'\x00\x00\x00'),
        (2, b'\x02\x00\x00'),
    ])
    def test_valid_channel(self, channel: int, suffix: bytes):
        self.maestro.stop_channel(channel)
        self.assert_wrote(b'\xAA\x0C\x04' + suffix)

    @pytest.mark.parametrize('channel', [-1, 3])
    def test_set_target_invalid_channel(self, channel: int):
        with pytest.raises(ValueError):
            self.maestro.stop_channel(channel)

        self.assert_conn_not_used()
