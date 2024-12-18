from unittest.mock import Mock, call

import pytest

from test_maestro.conftest import BaseMicroMaestroTest, BaseMiniMaestroTest


class TestMicroMaestroSetTargets(BaseMicroMaestroTest):
    def test_valid_target_dict(self):
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

    def test_valid_target_list(self):
        targets = [0, 1, 2, 4, 8, 16]

        suffixes = [
            b'\x00\x00\x00',
            b'\x01\x04\x00',
            b'\x02\x08\x00',
            b'\x03\x10\x00',
            b'\x04\x20\x00',
            b'\x05\x40\x00',
        ]

        self.maestro.set_targets(targets)

        self.conn.write.assert_has_calls([
            call(b'\xAA\x0C\x04' + suffix)
            for suffix in suffixes
        ])
        assert self.conn.flush.call_count == 6

    def test_setattr_with_valid_channel_and_target(self):
        self.maestro.set_targets = Mock()

        self.maestro[:3] = [1500, 0, 4095.75]

        self.maestro.set_targets.assert_called_once_with({0: 1500, 1: 0, 2: 4095.75})

    def test_setattr_with_single_target(self):
        self.maestro.set_targets = Mock()

        self.maestro[:3] = 1500

        self.maestro.set_targets.assert_called_once_with({0: 1500, 1: 1500, 2: 1500})

    @pytest.mark.parametrize('channel', [-1, 6])
    def test_set_targets_with_invalid_channel_raises_ValueError(self, channel: int):
        with pytest.raises(ValueError):
            self.maestro.set_targets({0: 1500, channel: 1500})

        self.assert_conn_not_used()

    @pytest.mark.parametrize('target_us', [-1, 4095.751])
    def test_set_targets_with_invalid_target_raises_ValueError(self, target_us: float):
        with pytest.raises(ValueError):
            self.maestro.set_targets({0: 1500, 1: target_us})

        self.assert_conn_not_used()

    def test_set_targets_with_invalid_number_of_targets_raises_ValueError(self):
        with pytest.raises(ValueError):
            self.maestro.set_targets([0, 1, 2, 3])

        self.assert_conn_not_used()

    def test_setattr_with_invalid_number_of_targets_raises_ValueError(self):
        with pytest.raises(ValueError):
            self.maestro[:2] = [0, 1, 2]

        self.assert_conn_not_used()


class TestMiniMaestroSetTargets(BaseMiniMaestroTest):
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
