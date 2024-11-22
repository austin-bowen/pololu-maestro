import pytest

from test_maestro.conftest import BaseMiniMaestroTest


class TestMiniMaestroSetPwm(BaseMiniMaestroTest):
    @pytest.mark.parametrize('period_us, duty_cycle, suffix', [
        (341.3125, 0., b'\x00\x00\x7F\x7F'),
        (341.3125, 1., b'\x7F\x7F\x7F\x7F'),
        (100, .5, b'\x60\x12\x40\x25'),
    ])
    def test_valid_on_time_and_period(self, period_us: float, duty_cycle: float, suffix: bytes):
        # noinspection PyUnresolvedReferences
        self.maestro.set_pwm(period_us, duty_cycle)
        self.assert_wrote(b'\xAA\x0C\x0A' + suffix)

    @pytest.mark.parametrize('period_us, duty_cycle', [
        (100, -0.01),
        (100, 1.01),
        (-100, .5),
        (341.3126, .5),
    ])
    def test_invalid_args_raises_ValueError(self, period_us: float, duty_cycle: float):
        with pytest.raises(ValueError):
            # noinspection PyUnresolvedReferences
            self.maestro.set_pwm(period_us, duty_cycle)

        self.assert_conn_not_used()
