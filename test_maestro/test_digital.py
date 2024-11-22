from unittest.mock import Mock

import pytest

from test_maestro.conftest import BaseMaestroTest


class TestMaestroDigital(BaseMaestroTest):
    @pytest.mark.parametrize('channel, position, expected', [
        (0, 0, False),
        (1, 511, False),
        (0, 512, True),
        (1, 1023, True),
    ])
    def test_get_digital(self, channel: int, position: int, expected: bool):
        self.maestro._get_position_raw = Mock(return_value=position)

        assert self.maestro.get_digital(channel) == expected

        self.maestro._get_position_raw.assert_called_once_with(channel)

    @pytest.mark.parametrize('channel, value, expected_target', [
        (1, False, 0),
        (2, False, 0),
        (1, True, 6000),
        (2, True, 6000),
    ])
    def test_set_digital(self, channel: int, value: bool, expected_target: int):
        self.maestro._set_target_raw = Mock()

        self.maestro.set_digital(channel, value)

        self.maestro._set_target_raw.assert_called_once_with(channel, expected_target)

    @pytest.mark.parametrize('channel', [-1, 3])
    def test_get_digital_with_invalid_channel_raises_ValueError(self, channel: int):
        with pytest.raises(ValueError):
            self.maestro.get_digital(channel)

    @pytest.mark.parametrize('channel', [-1, 3])
    def test_set_digital_with_invalid_channel_raises_ValueError(self, channel: int):
        with pytest.raises(ValueError):
            self.maestro.set_digital(channel, True)
