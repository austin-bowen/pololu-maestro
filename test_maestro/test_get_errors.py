import pytest

from maestro import MaestroError
from test_maestro.conftest import BaseMaestroTest

test_args = [
    (b'\x00\x00', set()),
    (b'\x01\x00', {MaestroError.SERIAL_SIGNAL_ERROR}),
    (b'\x02\x00', {MaestroError.SERIAL_OVERRUN_ERROR}),
    (b'\x04\x00', {MaestroError.SERIAL_BUFFER_FULL_ERROR}),
    (b'\x08\x00', {MaestroError.SERIAL_CRC_ERROR}),
    (b'\x10\x00', {MaestroError.SERIAL_PROTOCOL_ERROR}),
    (b'\x20\x00', {MaestroError.SERIAL_TIMEOUT_ERROR}),
    (b'\x40\x00', {MaestroError.SCRIPT_STACK_ERROR}),
    (b'\x80\x00', {MaestroError.SCRIPT_CALL_STACK_ERROR}),
    (b'\x00\x01', {MaestroError.SCRIPT_PROGRAM_COUNTER_ERROR}),
]


class TestMaestroGetErrors(BaseMaestroTest):
    @pytest.mark.parametrize('error_bytes, expected', test_args)
    def test(self, error_bytes: bytes, expected: set[MaestroError]):
        self.set_conn_read_bytes(error_bytes)

        assert self.maestro.get_errors() == expected

        self.assert_read()

    def test_all_errors_covered_by_test_args(self):
        all_errors = set(MaestroError)

        covered_errors = {error for _, errors in test_args for error in errors}

        assert all_errors == covered_errors
