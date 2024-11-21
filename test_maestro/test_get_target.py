import pytest

from test_maestro.conftest import BaseMaestroTest


class TestMaestroGetTarget(BaseMaestroTest):
    def setup_method(self) -> None:
        super().setup_method()

        self.maestro.set_target(0, 1500)
        self.maestro.set_target(1, 1600)

    def test_get_target(self):
        assert self.maestro.get_target(0) == 1500
        assert self.maestro.get_target(1) == 1600
        assert self.maestro.get_target(2) is None

    def test_get_targets(self):
        assert self.maestro.get_targets() == [1500, 1600, None]

    def test_getitem_with_int(self):
        assert self.maestro[0] == 1500
        assert self.maestro[1] == 1600
        assert self.maestro[2] is None

    def test_getitem_with_slice(self):
        assert self.maestro[0:2] == [1500, 1600]

    @pytest.mark.parametrize('channel', [-1, 3])
    def test_get_target_with_invalid_channel_raises_ValueError(self, channel: int):
        with pytest.raises(ValueError):
            self.maestro.get_target(channel)

        self.conn.read.assert_not_called()

    @pytest.mark.parametrize('channel', [-1, 3])
    def test_getitem_with_invalid_channel_raises_ValueError(self, channel: int):
        with pytest.raises(ValueError):
            # noinspection PyStatementEffect
            self.maestro[channel]

        self.conn.read.assert_not_called()
