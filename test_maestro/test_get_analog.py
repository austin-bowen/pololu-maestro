from math import isclose
from unittest.mock import Mock

import pytest

from test_maestro.conftest import BaseMaestroTest, MaestroTestImpl


class TestMaestroGetAnalog(BaseMaestroTest):
    @pytest.mark.parametrize('channel, position, expected', [
        (0, 0, 0.0),
        (1, 1023, 5.0),
        (2, 512, 5 * 512 / 1023),
    ])
    def test_get_analog(self, channel: int, position: int, expected: float):
        self.maestro._get_position_raw = Mock(return_value=position)

        assert isclose(self.maestro.get_analog(channel), expected)

        self.maestro._get_position_raw.assert_called_once_with(channel)

    @pytest.mark.parametrize('channels, channel', [
        (6, -1),
        (6, 6),
        (18, -1),
        (18, 12),  # Even though there are 18 channels, only 0..11 are valid
    ])
    def test_get_analog_with_invalid_channel_raises_ValueError(self, channels: int, channel: int):
        assert isinstance(self.maestro, MaestroTestImpl)
        self.maestro.channels = channels

        with pytest.raises(ValueError):
            self.maestro.get_analog(channel)
