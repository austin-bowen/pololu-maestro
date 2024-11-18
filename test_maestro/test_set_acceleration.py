import pytest

from test_maestro.conftest import BaseMaestroTest


class TestMaestroSetAcceleration(BaseMaestroTest):
    @pytest.mark.parametrize('channel, acceleration, suffix', [
        (0, 1, b'\x00\x01\x00'),
        (1, 0, b'\x01\x00\x00'),
        (2, 16383, b'\x02\x7f\x7f'),
    ])
    def test_valid_channel_and_acceleration(self, channel: int, acceleration: int, suffix: bytes):
        self.maestro.set_acceleration(channel, acceleration)
        self.assert_wrote(b'\xAA\x0C\x09' + suffix)

    @pytest.mark.parametrize('channel', [-1, 3])
    def test_invalid_channel_raises_ValueError(self, channel: int):
        with pytest.raises(ValueError):
            self.maestro.set_acceleration(channel, 1)

        self.assert_conn_not_used()

    @pytest.mark.parametrize('acceleration', [-1, 16384])
    def test_invalid_acceleration_raises_ValueError(self, acceleration: int):
        with pytest.raises(ValueError):
            self.maestro.set_acceleration(0, acceleration)

        self.assert_conn_not_used()
