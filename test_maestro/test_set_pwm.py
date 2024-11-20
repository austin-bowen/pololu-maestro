import pytest

from test_maestro.conftest import BaseMiniMaestroTest


class TestMiniMaestroSetPwm(BaseMiniMaestroTest):
    @pytest.mark.parametrize('on_time_us, period_us, suffix', [
        (0, 341.3125, b'\x00\x00\x7F\x7F'),
        (341.3125, 341.3125, b'\x7F\x7F\x7F\x7F'),
        (50, 100, b'\x60\x12\x40\x25'),
    ])
    def test_valid_on_time_and_period(self, on_time_us: float, period_us: float, suffix: bytes):
        # noinspection PyUnresolvedReferences
        self.maestro.set_pwm(on_time_us, period_us)
        self.assert_wrote(b'\xAA\x0C\x0A' + suffix)

    @pytest.mark.parametrize('on_time_us, period_us', [
        (-1, 100),
        (101, 100),
        (100, 341.3126),
    ])
    def test_invalid_args_raises_ValueError(self, on_time_us: float, period_us: float):
        with pytest.raises(ValueError):
            # noinspection PyUnresolvedReferences
            self.maestro.set_pwm(on_time_us, period_us)

        self.assert_conn_not_used()
