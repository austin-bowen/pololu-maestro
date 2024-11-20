import pytest
from pytest import approx

from test_maestro.conftest import BaseMaestroTest


class TestMaestroGetPosition(BaseMaestroTest):
    @pytest.mark.parametrize('channel, suffix, read_bytes, position', [
        (0, b'\x00', b'\x07\x0A', 2567 / 4),
        (1, b'\x01', b'\x00\x00', 0),
        (2, b'\x02', b'\xFF\x3F', 4095.75),
    ])
    def test_valid_channel_and_target(self, channel: int, suffix: bytes, read_bytes: bytes, position: float):
        self.set_conn_read_bytes(read_bytes)

        actual = self.maestro.get_position(channel)

        assert actual == approx(position)

        self.assert_wrote(b'\xAA\x0C\x10' + suffix)
        self.assert_read()

    def test_get_positions(self):
        self.conn.read.side_effect = [
            b'\x07\x0A',
            b'\x00\x00',
            b'\xFF\x3F',
        ]

        assert self.maestro.get_positions() == [2567 / 4, 0, 4095.75]

    @pytest.mark.parametrize('channel', [-1, 3])
    def test_invalid_channel_raises_ValueError(self, channel: int):
        with pytest.raises(ValueError):
            self.maestro.get_position(channel)

        self.assert_conn_not_used()
