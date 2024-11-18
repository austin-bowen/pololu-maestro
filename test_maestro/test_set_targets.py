from unittest.mock import call

import pytest

from maestro import Maestro, MicroMaestro, MiniMaestro, SerialCommands
from test_maestro.conftest import BaseMaestroTest


class TestMicroMaestroSetTargets(BaseMaestroTest):
    def build_maestro(self) -> Maestro:
        return MicroMaestro(
            self.conn,
            device=SerialCommands.DEFAULT_DEVICE_NUMBER,
            safe_close=False,
        )

    def test_valid_channel_and_target(self):
        targets = {
            0: 1500,
            1: 0,
            5: 4095.75,
        }

        suffixes = [
            b'\x00\x70\x2E',
            b'\x01\x00\x00',
            b'\x05\x7F\x7F',
        ]

        self.maestro.set_targets(targets)

        self.conn.write.assert_has_calls([
            call(b'\xAA\x0C\x04' + suffix)
            for suffix in suffixes
        ])
        assert self.conn.flush.call_count == 3

    @pytest.mark.parametrize('channel', [-1, 6])
    def test_invalid_channel_raises_ValueError(self, channel: int):
        with pytest.raises(ValueError):
            self.maestro.set_targets({0: 1500, channel: 1500})

        self.assert_conn_not_used()

    @pytest.mark.parametrize('target_us', [-1, 4095.751])
    def test_invalid_target_raises_ValueError(self, target_us: float):
        with pytest.raises(ValueError):
            self.maestro.set_targets({0: 1500, 1: target_us})

        self.assert_conn_not_used()


class TestMiniMaestroSetTargets(BaseMaestroTest):
    def build_maestro(self) -> Maestro:
        return MiniMaestro(
            12,
            self.conn,
            device=SerialCommands.DEFAULT_DEVICE_NUMBER,
            safe_close=False,
        )

    def test_valid_channel_and_target(self):
        targets = {
            # These should be sorted and grouped
            2: 1000,
            1: 0,
            3: 1500,

            # This will be by itself and should use the single set_target command
            5: 4095.75,

            # These should be sorted and grouped
            7: 1,
            8: 2,
        }

        suffixes = [
            b'\x1F\x03\x01\x00\x00\x20\x1F\x70\x2E',
            b'\x04\x05\x7F\x7F',
            b'\x1F\x02\x07\x04\x00\x08\x00',
        ]

        self.maestro.set_targets(targets)

        self.conn.write.assert_has_calls([
            call(b'\xAA\x0C' + suffix)
            for suffix in suffixes
        ])
        assert self.conn.flush.call_count == 3

    @pytest.mark.parametrize('channel', [-1, 12])
    def test_invalid_channel_raises_ValueError(self, channel: int):
        with pytest.raises(ValueError):
            self.maestro.set_targets({0: 1500, channel: 1500})

        self.assert_conn_not_used()

    @pytest.mark.parametrize('target_us', [-1, 4095.751])
    def test_invalid_target_raises_ValueError(self, target_us: float):
        with pytest.raises(ValueError):
            self.maestro.set_targets({0: 1500, 1: target_us})

        self.assert_conn_not_used()
