import pytest

from test_maestro.conftest import BaseMaestroTest


class TestMaestroRunScriptSubroutine(BaseMaestroTest):
    @pytest.mark.parametrize('subroutine, parameter, suffix', [
        (1, None, b'\x27\x01'),
        (127, 1, b'\x28\x7F\x01\x00'),
        (0, 16383, b'\x28\x00\x7F\x7F'),
    ])
    def test_valid_channel_and_target(self, subroutine: int, parameter: int, suffix: bytes):
        self.maestro.run_script_subroutine(subroutine, parameter)
        self.assert_wrote(b'\xAA\x0C' + suffix)

    @pytest.mark.parametrize('subroutine', [-1, 128])
    def test_invalid_subroutine_raises_ValueError(self, subroutine: int):
        with pytest.raises(ValueError):
            self.maestro.run_script_subroutine(subroutine)

        self.assert_conn_not_used()

    @pytest.mark.parametrize("parameter", [-1, 16384])
    def test_invalid_parameter_raises_ValueError(self, parameter):
        with pytest.raises(ValueError):
            self.maestro.run_script_subroutine(0, parameter)

        self.assert_conn_not_used()
