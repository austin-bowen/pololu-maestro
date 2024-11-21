import pytest

from test_maestro.conftest import BaseMaestroTest


class TestMaestroSpeed(BaseMaestroTest):
    @pytest.mark.parametrize('channel, speed, suffix', [
        (0, 1, b'\x00\x01\x00'),
        (1, 0, b'\x01\x00\x00'),
        (2, 16383, b'\x02\x7f\x7f'),
    ])
    def test_set_speed_with_valid_channel_and_speed(self, channel: int, speed: int, suffix: bytes):
        self.maestro.set_speed(channel, speed)
        self.assert_wrote(b'\xAA\x0C\x07' + suffix)

    @pytest.mark.parametrize('channel', [-1, 3])
    def test_set_speed_with_invalid_channel_raises_ValueError(self, channel: int):
        with pytest.raises(ValueError):
            self.maestro.set_speed(channel, 1)

        self.assert_conn_not_used()

    @pytest.mark.parametrize('speed', [-1, 16384])
    def test_set_speed_with_invalid_speed_raises_ValueError(self, speed: int):
        with pytest.raises(ValueError):
            self.maestro.set_speed(0, speed)

        self.assert_conn_not_used()

    @pytest.mark.parametrize('channel', [0, 2])
    def test_get_speed_with_valid_channel_returns_speed(self, channel: int):
        assert self.maestro.get_speed(channel) is None
        self.maestro.set_speed(channel, 42)
        assert self.maestro.get_speed(channel) == 42

    @pytest.mark.parametrize('channel', [-1, 3])
    def test_get_speed_with_invalid_channel_raises_ValueError(self, channel: int):
        with pytest.raises(ValueError):
            self.maestro.get_speed(channel)

    def test_get_speeds(self):
        assert self.maestro.get_speeds() == [None, None, None]

        self.maestro.set_speed(0, 42)
        self.maestro.set_speed(1, 43)
        self.maestro.set_speed(2, 44)

        assert self.maestro.get_speeds() == [42, 43, 44]
