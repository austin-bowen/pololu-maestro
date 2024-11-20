from unittest.mock import Mock

import pytest

from test_maestro.conftest import BaseMaestroTest


class TestMaestroGetPosition(BaseMaestroTest):
    @pytest.mark.parametrize('expected', [False, True])
    def test_valid_channel_and_target(self, expected: bool):
        target = 2000.
        self.maestro.set_target(0, target)
        self.maestro.get_position = Mock(
            return_value=1000. if expected else target
        )

        assert self.maestro.is_moving(0) == expected

    @pytest.mark.parametrize('channel', [-1, 3])
    def test_invalid_channel_raises_ValueError(self, channel: int):
        with pytest.raises(ValueError):
            self.maestro.is_moving(channel)

        self.assert_conn_not_used()
