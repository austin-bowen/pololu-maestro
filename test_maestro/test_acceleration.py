import pytest

from test_maestro.conftest import BaseMaestroTest


class TestMaestroAcceleration(BaseMaestroTest):
    @pytest.mark.parametrize('channel, acceleration, suffix', [
        (0, 1, b'\x00\x01\x00'),
        (1, 0, b'\x01\x00\x00'),
        (2, 16383, b'\x02\x7f\x7f'),
    ])
    def test_set_acceleration_with_valid_channel_and_acceleration(
            self, channel: int, acceleration: int, suffix: bytes
    ):
        self.maestro.set_acceleration(channel, acceleration)
        self.assert_wrote(b'\xAA\x0C\x09' + suffix)

    @pytest.mark.parametrize('channel', [-1, 3])
    def test_set_acceleration_with_invalid_channel_raises_ValueError(self, channel: int):
        with pytest.raises(ValueError):
            self.maestro.set_acceleration(channel, 1)

        self.assert_conn_not_used()

    @pytest.mark.parametrize('acceleration', [-1, 16384])
    def test_set_acceleration_with_invalid_acceleration_raises_ValueError(self, acceleration: int):
        with pytest.raises(ValueError):
            self.maestro.set_acceleration(0, acceleration)

        self.assert_conn_not_used()

    @pytest.mark.parametrize('channel', [0, 2])
    def test_get_acceleration_with_valid_channel_returns_acceleration(self, channel: int):
        assert self.maestro.get_acceleration(channel) is None
        self.maestro.set_acceleration(channel, 42)
        assert self.maestro.get_acceleration(channel) == 42

    @pytest.mark.parametrize('channel', [-1, 3])
    def test_get_acceleration_with_invalid_channel_raises_ValueError(self, channel: int):
        with pytest.raises(ValueError):
            self.maestro.get_acceleration(channel)

    def test_get_accelerations(self):
        assert self.maestro.get_accelerations() == [None, None, None]

        self.maestro.set_acceleration(0, 42)
        self.maestro.set_acceleration(1, 43)
        self.maestro.set_acceleration(2, 44)

        assert self.maestro.get_accelerations() == [42, 43, 44]
