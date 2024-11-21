from unittest.mock import Mock

import pytest

from test_maestro.conftest import BaseMaestroTest


class TestMaestroStop(BaseMaestroTest):
    @pytest.mark.parametrize('channel, suffix', [
        (0, b'\x00\x00\x00'),
        (2, b'\x02\x00\x00'),
    ])
    def test_stop_channel_with_valid_channel(self, channel: int, suffix: bytes):
        self.maestro.stop_channel(channel)
        self.assert_wrote(b'\xAA\x0C\x04' + suffix)

    @pytest.mark.parametrize('channel', [-1, 3])
    def test_stop_channel_with_invalid_channel_raises_ValueError(self, channel: int):
        with pytest.raises(ValueError):
            self.maestro.stop_channel(channel)

        self.assert_conn_not_used()

    def test_stop_all_channels(self):
        self.maestro.set_targets = Mock()

        self.maestro.stop()

        self.maestro.set_targets.assert_called_once_with([0, 0, 0])
