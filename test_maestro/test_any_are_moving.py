from unittest.mock import Mock, call

import pytest

from test_maestro.conftest import BaseMicroMaestroTest, BaseMiniMaestroTest


class TestMicroMaestroAnyAreMoving(BaseMicroMaestroTest):
    @pytest.mark.parametrize('expected', [True, False])
    def test(self, expected: bool):
        # Make the last channel appear to be moving if expected is True
        self.maestro.is_moving = Mock(
            side_effect=lambda c: c == 5 and expected
        )

        assert self.maestro.any_are_moving() == expected

        self.maestro.is_moving.assert_has_calls([
            call(c) for c in range(6)
        ])


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
