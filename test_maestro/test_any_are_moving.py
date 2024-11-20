from unittest.mock import Mock

import pytest

from test_maestro.conftest import BaseMicroMaestroTest, BaseMiniMaestroTest


class TestMicroMaestroAnyAreMoving(BaseMicroMaestroTest):
    @pytest.mark.parametrize('moving_channels, expected', [
        ({}, False),
        ({0}, True),
        ({2, 5}, True),
    ])
    def test(self, moving_channels: set[int], expected: bool):
        self.maestro.is_moving = Mock(
            side_effect=lambda c: c in moving_channels
        )

        assert self.maestro.any_are_moving() == expected

        self.maestro.is_moving.assert_called()


class TestMiniMaestroAnyAreMoving(BaseMiniMaestroTest):
    @pytest.mark.parametrize('read_bytes, expected', [
        (b'\x01', True),
        (b'\x00', False),
    ])
    def test(self, read_bytes: bytes, expected: bool):
        self.set_conn_read_bytes(read_bytes)

        assert self.maestro.any_are_moving() == expected

        self.assert_wrote(b'\xAA\x0C\x13')
        self.assert_read()
