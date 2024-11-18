from typing import Mapping
from unittest.mock import Mock

import serial

from maestro import Maestro, SerialCommands


class MaestroTestImpl(Maestro):
    @property
    def channels(self) -> int:
        return 3

    def _set_targets(self, targets: Mapping[int, float]) -> None:
        raise NotImplementedError()

    def any_are_moving(self) -> bool:
        raise NotImplementedError()


class BaseMaestroTest:
    conn: Mock
    maestro: Maestro

    def setup_method(self) -> None:
        self.conn = Mock(serial.Serial)

        self.maestro = MaestroTestImpl(
            self.conn,
            device=SerialCommands.DEFAULT_DEVICE_NUMBER,
            safe_close=False,
        )

    def assert_wrote(self, data: bytes) -> None:
        self.conn.write.assert_called_once_with(data)
        self.conn.flush.assert_called_once()

    def assert_conn_not_used(self) -> None:
        self.conn.write.assert_not_called()