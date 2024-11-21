from unittest.mock import Mock

from test_maestro.conftest import BaseMaestroTest


class TestMaestroWaitUntilDoneMoving(BaseMaestroTest):
    def test(self):
        self.maestro.any_are_moving = Mock(
            side_effect=[True, True, False, False]
        )

        self.maestro.wait_until_done_moving()
        assert not self.maestro.any_are_moving()

        assert self.maestro.any_are_moving.call_count == 4
