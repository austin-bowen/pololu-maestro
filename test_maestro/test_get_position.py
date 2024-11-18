import pytest
from pytest import approx

from test_maestro.conftest import BaseMaestroTest


class TestMaestroSetTarget(BaseMaestroTest):
    @pytest.mark.parametrize('channel, suffix, read_bytes, position', [
        (0, b'\x00', b'\x07\x0A', 2567 / 4),
        (1, b'\x01', b'\x00\x00', 0),
        (2, b'\x02', b'\xFF\x3F', 4095.75),
    ])
    def test_valid_channel_and_target(self, channel: int, suffix: bytes, read_bytes: bytes, position: float):
        self.conn.read.side_effect = lambda n: {len(read_bytes): read_bytes}[n]

        actual = self.maestro.get_position(channel)

        assert actual == approx(position)

        self.assert_wrote(b'\xAA\x0C\x10' + suffix)
        self.conn.read.assert_called_once()

    @pytest.mark.parametrize('channel', [-1, 3])
    def test_invalid_channel_raises_ValueError(self, channel: int):
        with pytest.raises(ValueError):
            self.maestro.get_position(channel)

        self.assert_conn_not_used()
