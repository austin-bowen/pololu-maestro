import pytest

from test_maestro.conftest import BaseMaestroTest


class TestMaestroSetTarget(BaseMaestroTest):
    @pytest.mark.parametrize('channel, target_us, suffix', [
        (0, 1500, b'\x00\x70\x2E'),
        (1, 0, b'\x01\x00\x00'),
        (2, 4095.75, b'\x02\x7F\x7F'),
    ])
    def test_valid_channel_and_target(self, channel: int, target_us: int, suffix: bytes):
        self.maestro.set_target(channel, target_us)
        self.assert_wrote(b'\xAA\x0C\x04' + suffix)

    @pytest.mark.parametrize('channel', [-1, 3])
    def test_invalid_channel_raises_ValueError(self, channel: int):
        with pytest.raises(ValueError):
            self.maestro.set_target(channel, 1500)

        self.assert_conn_not_used()

    @pytest.mark.parametrize('target_us', [-1, 4095.751])
    def test_invalid_target_raises_ValueError(self, target_us: float):
        with pytest.raises(ValueError):
            self.maestro.set_target(0, target_us)

        self.assert_conn_not_used()
