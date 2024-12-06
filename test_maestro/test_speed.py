from typing import Optional

import pytest

from test_maestro.conftest import BaseMaestroTest


class TestMaestroSpeed(BaseMaestroTest):
    @pytest.mark.parametrize('channel, speed, suffix', [
        (0, 1, b'\x00\x01\x00'),
        (0, 25, b'\x00\x01\x00'),
        (1, None, b'\x01\x00\x00'),
        (2, 409575, b'\x02\x7f\x7f'),
    ])
    def test_set_speed_with_valid_channel_and_speed(
            self,
            channel: int,
            speed: Optional[int],
            suffix: bytes,
    ):
        self.maestro.set_speed(channel, speed)
        self.assert_wrote(b'\xAA\x0C\x07' + suffix)

    @pytest.mark.parametrize('channel', [-1, 3])
    def test_set_speed_with_invalid_channel_raises_ValueError(self, channel: int):
        with pytest.raises(ValueError):
            self.maestro.set_speed(channel, 1)

        self.assert_conn_not_used()

    @pytest.mark.parametrize('speed', [-1, 0])
    def test_set_speed_with_invalid_speed_raises_ValueError(self, speed: int):
        with pytest.raises(ValueError):
            self.maestro.set_speed(0, speed)

        self.assert_conn_not_used()

    @pytest.mark.parametrize('channel, speed, expected', [
        (0, 24, 25),
        (1, 25, 25),
        (2, 26, 26),
        (0, 409574, 409574),
        (1, 409575, 409575),
        (2, 409576, 409575),
    ])
    def test_get_speed(
            self,
            channel: int,
            speed: int,
            expected: int,
    ):
        assert self.maestro.get_speed(channel) is None
        self.maestro.set_speed(channel, speed)
        assert self.maestro.get_speed(channel) == expected

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
