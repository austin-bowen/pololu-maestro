"""
Maestro Servo Controllers

Support for the Pololu Maestro line of servo controllers:
https://www.pololu.com/docs/0J40

These functions provide access to many of the Maestro's capabilities using the Pololu serial protocol.
"""

import argparse
import platform
import time
from abc import ABC, abstractmethod
from collections.abc import Sequence
from enum import Enum
from threading import RLock
from typing import Literal, Mapping, Optional, Union

import serial
from serial import Serial

DEFAULT_TTY = 'COM5' if platform.system() == 'Windows' else '/dev/ttyACM0'
DEFAULT_DEVICE_NUMBER = 0x0C


class Maestro(ABC):
    """
    When connected via USB, the Maestro creates two virtual serial ports
    /dev/ttyACM0 for commands and /dev/ttyACM1 for communications.
    Be sure the Maestro is configured for "USB Dual Port" serial mode.
    "USB Chained Mode" may work as well, but hasn't been tested.

    Pololu protocol allows for multiple Maestros to be connected to a single
    serial port. Each connected device is then indexed by number.
    This device number defaults to 0x0C (or 12 in decimal), which this module
    assumes.  If two or more controllers are connected to different serial
    ports, or you are using a Windows OS, you can provide the tty port.  For
    example, '/dev/ttyACM2' or for Windows, something like 'COM5'.

    This class is thread-safe.
    """

    @staticmethod
    def connect(
            model: Union[Literal['micro', 'mini12', 'mini18', 'mini24'], str],
            tty: str = DEFAULT_TTY,
            timeout: float = None,
            device: int = DEFAULT_DEVICE_NUMBER,
            safe_close: bool = True,
    ) -> Union['MicroMaestro', 'MiniMaestro']:
        """
        Connect to a Maestro servo controller.

        Args:
            model:
                The model of the Maestro to connect to.
                Must be one of 'micro', 'mini12', 'mini18', or 'mini24'.
            tty:
                The tty port to connect to.
            timeout:
                Timeout in seconds for serial communication.
            device:
                The device number.
            safe_close:
                If `True` (default), tells the Maestro to stop sending servo
                signals before closing the connection.
        """

        conn = serial.Serial(tty, timeout=timeout)

        if model == 'micro':
            return MicroMaestro(conn, device, safe_close)
        else:
            channels = int(model[-2:])
            return MiniMaestro(channels, conn, device, safe_close)

    def __init__(
            self,
            conn: Serial,
            device: int,
            safe_close: bool,
    ):
        """
        Args:
            conn:
                A serial.Serial instance to use for communication.
            device:
                The device number.
            safe_close:
                If `True`, tells the Maestro to stop sending servo signals before closing the connection.
        """

        self._conn = conn
        self._conn_lock = RLock()

        # Command lead-in and device number are sent for each Pololu serial command.
        self._pololu_cmd = bytes((SerialCommands.POLOLU_PROTOCOL, device))

        self.safe_close = safe_close

        # Track target position, speed, and acceleration for each servo
        self._targets: list[Optional[float]] = [None] * self.channels
        self._speeds: list[Optional[int]] = [None] * self.channels
        self._accels: list[Optional[int]] = [None] * self.channels

        # Servo minimum and maximum targets can be restricted to protect components
        self.target_limits_us: list[tuple[Optional[float], Optional[float]]] = [(None, None)] * self.channels

        self._closed = False

    @property
    @abstractmethod
    def channels(self) -> int:
        ...

    def _validate_channel(self, channel: int) -> None:
        if not (0 <= channel < self.channels):
            raise ValueError(f"Invalid channel: {channel}. Must be between 0 and {self.channels - 1}.")

    @staticmethod
    def _validate_channel_arg(method):
        def wrapper(self, channel, *args, **kwargs):
            self._validate_channel(channel)
            return method(self, channel, *args, **kwargs)

        return wrapper

    def _validate_target_us(self, target_us: float) -> None:
        if not (0. <= target_us <= 4095.75):
            raise ValueError(f'target_us must be in the range [0, 4095.75]; got {target_us}.')

    def __str__(self) -> str:
        targets = dict(enumerate(self.get_targets()))
        return f'{self.__class__.__name__}(targets={targets})'

    def __enter__(self) -> 'Maestro':
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def __getitem__(self, channel: Union[int, slice]) -> Union[float, list[float]]:
        if isinstance(channel, slice):
            return [self.get_target(c) for c in range(*channel.indices(self.channels))]
        else:
            return self.get_target(channel)

    def __setitem__(
            self,
            channel: Union[int, slice],
            target_us: Union[float, Sequence[float]],
    ) -> None:
        if not isinstance(channel, slice):
            self.set_target(channel, target_us)
            return

        channels = range(*channel.indices(self.channels))

        if isinstance(target_us, Sequence):
            if len(target_us) != len(channels):
                raise ValueError(
                    f'If target_us is a sequence, it must have the same length as the number of channels; '
                    f'got {len(target_us)} targets for {len(channels)} channels.'
                )

            targets = {c: t for c, t in zip(channels, target_us)}
        else:
            targets = {c: target_us for c in channels}

        self.set_targets(targets)

    def close(self) -> None:
        """Cleanup by closing USB serial port."""

        if self._closed:
            return

        if self.safe_close:
            self.stop()

        self._conn.close()

        self._closed = True

    @_validate_channel_arg
    def set_target(self, channel: int, target_us: float) -> None:
        """
        Set channel to a specified target value.  Servo will begin moving based
        on Speed and Acceleration parameters previously set.
        Target values will be constrained within Min and Max range, if set.
        For servos, target represents the pulse width in of quarter-microseconds
        Servo center is at 1500 microseconds, or 6000 quarter-microseconds
        Typically valid servo range is 3000 to 9000 quarter-microseconds
        If channel is configured for digital output, values < 6000 = Low output
        """

        self._validate_target_us(target_us)

        min_target_us, max_target_us = self.get_limits(channel)

        if min_target_us is not None and target_us < min_target_us:
            target_us = min_target_us

        if max_target_us is not None and target_us > max_target_us:
            target_us = max_target_us

        target = int(round(4 * target_us))
        self._set_target_raw(channel, target)

        self._targets[channel] = target_us

    def _set_target_raw(self, channel: int, target: int) -> None:
        lsb, msb = _get_lsb_msb(target)
        self.send_cmd(SerialCommands.SET_TARGET, channel, lsb, msb)

    @_validate_channel_arg
    def get_target(self, channel: int) -> float:
        """Return the target value for the specified channel."""
        return self._targets[channel]

    def set_targets(self, targets: Union[Sequence[float], Mapping[int, float]]) -> None:
        """
        Set multiple channel targets at once.

        Args:
            targets:
                Either a list of length `channels`, or a dict mapping channels
                to their targets (in microseconds).
        """

        if not isinstance(targets, Mapping):
            if len(targets) != self.channels:
                raise ValueError(
                    f'If targets is a sequence, it must have the same length as the number of channels; '
                    f'got {len(targets)} targets for {self.channels} channels.'
                )

            targets = dict(enumerate(targets))

        for channel, target_us in targets.items():
            self._validate_channel(channel)
            self._validate_target_us(target_us)

        self._set_targets(targets)

        for channel, target_us in targets.items():
            self._targets[channel] = target_us

    @abstractmethod
    def _set_targets(self, targets: Mapping[int, float]) -> None:
        ...

    def get_targets(self) -> list[float]:
        """Return a list of target values for all channels."""
        return list(self._targets)

    @_validate_channel_arg
    def get_position(self, channel: int) -> float:
        """
        Get the current position of the device on the specified channel
        The result is returned in a measure of quarter-microseconds, which mirrors
        the Target parameter of setTarget.
        This is not reading the true servo position, but the last target position sent
        to the servo. If the Speed is set to below the top speed of the servo, then
        the position result will align well with the actual servo position, assuming
        it is not stalled or slowed.

        Raises:
            TimeoutError: Connection timed out.
        """

        return self._get_position_raw(channel) / 4

    def _get_position_raw(self, channel: int) -> int:
        data = self.send_cmd(SerialCommands.GET_POSITION, channel, read=2)
        return data[1] << 8 | data[0]

    def get_positions(self) -> list[float]:
        return list(self.get_position(c) for c in range(self.channels))

    @_validate_channel_arg
    def set_limits(self, channel: int, min_us: float = None, max_us: float = None) -> None:
        """
        Set channels min and max value range.  Use this as a safety to protect from accidentally moving outside known
        safe parameters. A setting of 0 or None allows unrestricted movement.

        Note that the Maestro itself is configured to limit the range of servo travel which has precedence over these
        values. Use the Maestro Control Center to configure ranges that are saved to the controller. Use set_range for
        software controllable ranges.
        """

        if min_us is not None and max_us is not None and min_us > max_us:
            raise ValueError(
                f'min_us must be less than or equal to max_us; '
                f'got min_us={min_us} and max_us={max_us}.'
            )

        self.target_limits_us[channel] = (min_us, max_us)

    @_validate_channel_arg
    def get_limits(self, channel: int) -> tuple[Optional[float], Optional[float]]:
        """Return tuple of (min_us, max_us) for the specified channel."""
        return self.target_limits_us[channel]

    @_validate_channel_arg
    def stop_channel(self, channel: int) -> None:
        """
        Sets the target of the specified channel to 0, causing the Maestro to stop sending PWM signals on that channel.

        Args:
             channel: PWM channel to stop sending PWM signals to.
        """

        self.set_target(channel, 0)

    def stop(self) -> None:
        """Stops all servos."""
        self.set_targets([0] * self.channels)

    def go_home(self) -> None:
        """
        Sends all servos and outputs to their home positions, just as if an error had occurred.
        For servos and outputs set to "Ignore", the position will be unchanged.
        """

        self.send_cmd(SerialCommands.GO_HOME)

    @_validate_channel_arg
    def is_moving(self, channel: int) -> bool:
        """
        Test to see if a servo has reached the set target position.  This only provides
        useful results if the Speed parameter is set slower than the maximum speed of
        the servo.  Servo range must be defined first using setRange. See setRange comment.

        ***Note if target position goes outside of Maestro's allowable range for the
        channel, then the target can never be reached, so it will appear to always be
        moving to the target.
        """

        target = self._targets[channel]
        return (
                target is not None
                and target > 0
                and abs(target - self.get_position(channel)) > 0.01
        )

    @abstractmethod
    def any_are_moving(self) -> bool:
        ...

    def wait_until_done_moving(self, poll_period: float = 0.1) -> None:
        """
        Wait until all servos have reached their target positions.

        Args:
            poll_period: Time in seconds to wait between checking if servos are still moving.
        """

        while self.any_are_moving():
            time.sleep(poll_period)

    @_validate_channel_arg
    def set_speed(self, channel: int, speed: int) -> None:
        """
        Set speed of channel
        Speed is measured as 0.25microseconds/10milliseconds
        For the standard 1ms pulse width change to move a servo between extremes, a speed
        of 1 will take 1 minute, and a speed of 60 would take 1 second. Speed of 0 is unrestricted.
        """

        lsb, msb = _get_lsb_msb(speed)
        self.send_cmd(SerialCommands.SET_SPEED, channel, lsb, msb)
        self._speeds[channel] = speed

    @_validate_channel_arg
    def get_speed(self, channel: int) -> Optional[int]:
        """
        Get the last speed setting for the channel.
        0 = unrestricted. None if not yet set.
        """
        return self._speeds[channel]

    def get_speeds(self) -> list[Optional[int]]:
        return list(self._speeds)

    @_validate_channel_arg
    def set_acceleration(self, channel: int, acceleration: int) -> None:
        """
        Set acceleration of channel
        This provide soft starts and finishes when servo moves to target position.
        Valid values are from 0 to 255. 0 = unrestricted, 1 is slowest start.
        A value of 1 will take the servo about 3s to move between 1ms to 2ms range.
        """

        lsb, msb = _get_lsb_msb(acceleration)
        self.send_cmd(SerialCommands.SET_ACCELERATION, channel, lsb, msb)
        self._accels[channel] = acceleration

    @_validate_channel_arg
    def get_acceleration(self, channel: int) -> Optional[int]:
        """
        Get the last acceleration setting for the channel.
        0 = unrestricted. None if not yet set.
        """
        return self._accels[channel]

    def get_accelerations(self) -> list[Optional[int]]:
        return list(self._accels)

    @_validate_channel_arg
    def get_digital(self, channel: int) -> bool:
        """
        Returns the state of the specified digital channel.

        The channel must be configured as an input using the Maestro Control Center.
        """

        return self._get_position_raw(channel) >= 512

    @_validate_channel_arg
    def set_digital(self, channel: int, value: bool) -> None:
        """
        Sets the state of the specified digital channel.

        The channel must be configured as a digital output using the Maestro Control Center.
        """

        self._set_target_raw(channel, 6000 if value else 0)

    @_validate_channel_arg
    def get_analog(self, channel: int) -> float:
        """
        Returns the voltage on the specified analog input channel.

        The channel must be configured as an input using the Maestro Control Center.
        """

        if not (0 <= channel <= 11):
            raise ValueError(f'Analog channels must be in the range [0, 11]; got {channel}.')

        return self._get_position_raw(channel) * 5 / 1023

    def run_script_subroutine(self, subroutine: int, parameter: int = None) -> None:
        """
        Starts the script running at a location specified by the subroutine number argument. The subroutines are
        numbered in the order they are defined in your script, starting with 0 for the first subroutine. The first
        subroutine is sent as 0x00 for this command, the second as 0x01, etc. To find the number for a particular
        subroutine, click the "View Compiled Code..." button and look at the list below. Subroutines used this way
        should not end with the RETURN command, since there is no place to return to — instead, they should contain
        infinite loops or end with a QUIT command.

        Args:
            subroutine: The subroutine number to run. Range: 0 to 127.
            parameter: (Optional) The integer parameter to pass to the subroutine (range: 0 to 16383).
        """

        if not (0 <= subroutine <= 127):
            raise ValueError(f'subroutine must be in the range [0, 127]; got {subroutine}.')

        if parameter is None:
            self.send_cmd(SerialCommands.RESTART_SCRIPT_AT_SUBROUTINE, subroutine)
        else:
            parameter_lsb, parameter_msb = _get_lsb_msb(parameter)
            self.send_cmd(
                SerialCommands.RESTART_SCRIPT_AT_SUBROUTINE_WITH_PARAMETER,
                subroutine,
                parameter_lsb,
                parameter_msb,
            )

    def script_is_running(self) -> bool:
        """
        Returns True if a script is running; False otherwise.

        Raises:
            TimeoutError: Connection timed out.
        """

        response = self.send_cmd(SerialCommands.GET_SCRIPT_STATUS, read=1)

        is_running = 0
        return response[0] == is_running

    def stop_script(self) -> None:
        """Causes the script to stop, if it is currently running."""
        self.send_cmd(SerialCommands.STOP_SCRIPT)

    def get_errors(self) -> set['MaestroError']:
        """
        Returns a set of the errors that have occurred on the Maestro.
        This also clears the error codes.

        Raises:
            TimeoutError: Connection timed out.
        """

        data = self.send_cmd(SerialCommands.GET_ERRORS, read=2)
        error_code = data[1] << 8 | data[0]

        return MaestroError.from_error_code(error_code)

    def send_cmd(self, *args: int, read: int = 0) -> bytes:
        """Send a Pololu command to the Maestro, and optionally read response bytes back."""
        return self.send_cmd_bytes(bytes(args), read=read)

    def send_cmd_bytes(self, cmd: Union[bytes, bytearray], read: int = 0) -> bytes:
        with self._conn_lock:
            self._conn.write(self._pololu_cmd + cmd)
            self._conn.flush()
            return self._read(read)

    def _read(self, byte_count: int) -> bytes:
        """
        Raises:
            TimeoutError: Connection timed out waiting to read the specified number of bytes.
        """

        if not byte_count:
            return b''

        data = self._conn.read(byte_count)
        if len(data) != byte_count:
            raise TimeoutError(f'Tried to read {byte_count} bytes, but only got {len(data)}.')

        return data


class MicroMaestro(Maestro):
    @property
    def channels(self) -> int:
        return 6

    def _set_targets(self, targets: Mapping[int, float]) -> None:
        for channel, target_us in targets.items():
            self.set_target(channel, target_us)

    def any_are_moving(self) -> bool:
        return any(self.is_moving(c) for c in range(self.channels))


class MiniMaestro(Maestro):
    def __init__(
            self,
            channels: int,
            conn: Serial,
            device: int,
            safe_close: bool,
    ):
        if channels not in (12, 18, 24):
            raise ValueError(f'channels must be 12, 18, or 24; got {channels}.')

        self._channels = channels
        super().__init__(conn, device, safe_close)

    @property
    def channels(self) -> int:
        return self._channels

    def _set_targets(self, targets: Mapping[int, float]) -> None:
        # Use targets to build a structure of target blocks
        channels = sorted(targets.keys())
        prev_channel = first_channel = channels[0]
        target = targets[first_channel]
        # Structure: {channelM: [targetM, targetM+1, ..., targetN], ...}
        target_blocks = {first_channel: [target]}
        for channel in channels[1:]:
            target = targets[channel]

            if channel - 1 == prev_channel:
                target_blocks[first_channel].append(target)
            else:
                first_channel = channel
                target_blocks[first_channel] = [target]

            prev_channel = channel

        for first_channel, target_block in target_blocks.items():
            target_count = len(target_block)

            # If there is only one target in the block, use the single "set target" command
            if target_count == 1:
                self.set_target(first_channel, target_block[0])

            # If there is more than one target in the block, set them all at once with the
            # "set multiple targets" command.
            else:
                cmd = bytearray((SerialCommands.SET_MULTIPLE_TARGETS, target_count, first_channel))
                for target in target_block:
                    target = int(float(4 * target))
                    cmd += bytes(_get_lsb_msb(target))
                self.send_cmd_bytes(cmd)

    def set_pwm(self, on_time_us: float, period_us: float) -> None:
        """
        Sets the PWM output to the specified on time and period.
        This command is not available on the Micro Maestro.

        Args:
            on_time_us: PWM on-time in microseconds.
            period_us: PWM period in microseconds.
        """

        if on_time_us > period_us:
            raise ValueError(
                f'on_time_us must be less than or equal to period_us; '
                f'got on_time_us={on_time_us} and period_us={period_us}.'
            )
        if period_us > 341.3125:
            raise ValueError(
                f'period_us must be less than or equal to 341.3125; '
                f'got period_us={period_us}.'
            )

        # The command uses 1/48th us intervals
        on_time = int(round(48 * on_time_us))
        period = int(round(48 * period_us))

        self.send_cmd(
            SerialCommands.SET_PWM,
            *_get_lsb_msb(on_time),
            *_get_lsb_msb(period),
        )

    def any_are_moving(self) -> bool:
        """
        Determines whether the servo outputs have reached their targets or are still changing, and will return True as
        long as there is at least one servo that is limited by a speed or acceleration setting still moving. Using this
        command together with the set_target command, you can initiate several servo movements and wait for all the
        movements to finish before moving on to the next step of your program.

        Returns True if the Maestro reports that servos are still moving; False otherwise.

        Raises:
            TimeoutError: Connection timed out.
        """

        response = self.send_cmd(SerialCommands.GET_MOVING_STATE, read=1)
        return response[0] != 0


class SerialCommands:
    # Headers
    POLOLU_PROTOCOL = 0xAA

    # Commands
    SET_TARGET = 0x04
    SET_SPEED = 0x07
    SET_ACCELERATION = 0x09
    GET_POSITION = 0x10
    GET_ERRORS = 0x21
    GO_HOME = 0x22
    STOP_SCRIPT = 0x24
    RESTART_SCRIPT_AT_SUBROUTINE = 0x27
    RESTART_SCRIPT_AT_SUBROUTINE_WITH_PARAMETER = 0x28
    GET_SCRIPT_STATUS = 0x2E
    # - Not available on the Micro
    SET_PWM = 0x0A
    GET_MOVING_STATE = 0x13
    SET_MULTIPLE_TARGETS = 0x1F


class MaestroError(Enum):
    """
    See the documentation for descriptions of these errors:
    https://www.pololu.com/docs/0J40/4.e
    """

    SERIAL_SIGNAL_ERROR = 1 << 0
    SERIAL_OVERRUN_ERROR = 1 << 1
    SERIAL_BUFFER_FULL_ERROR = 1 << 2
    SERIAL_CRC_ERROR = 1 << 3
    SERIAL_PROTOCOL_ERROR = 1 << 4
    SERIAL_TIMEOUT_ERROR = 1 << 5
    SCRIPT_STACK_ERROR = 1 << 6
    SCRIPT_CALL_STACK_ERROR = 1 << 7
    SCRIPT_PROGRAM_COUNTER_ERROR = 1 << 8

    @classmethod
    def from_error_code(cls, error_code: int) -> set['MaestroError']:
        return {error for error in cls if error.value & error_code}


def _get_lsb_msb(value: int) -> tuple[int, int]:
    if not (0 <= value <= 16383):
        raise ValueError(f'value was {value}; must be in the range [0, 16383].')
    lsb = value & 0x7F  # 7 bits for least significant byte
    msb = (value >> 7) & 0x7F  # shift 7 and take next 7 bits for msb
    return lsb, msb


def main() -> None:
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument(
        'model',
        choices=('micro', 'mini12', 'mini18', 'mini24'),
        help='The Maestro model to connect to.',
    )
    arg_parser.add_argument(
        '--tty',
        default=DEFAULT_TTY,
        help=f'The tty port to connect to. Default: {DEFAULT_TTY!r}',
    )
    args = arg_parser.parse_args()

    print(f'Connecting to {args.model} Maestro on {args.tty!r}...')
    with Maestro.connect(args.model, tty=args.tty) as maestro:
        print('Connected!')

        if maestro.script_is_running():
            print('Stopping running script... ', end='', flush=True)
            maestro.stop_script()
            print('Done')

        print()
        print('Set servo position targets by typing "<channel> <target_us>" below.')
        print('A target of 1500 (us) is typically the center position.')
        print('A target of 0 will turn off the servo.')
        print()
        print('Press Ctrl+C to exit.')
        print()

        def handle_command() -> None:
            command = input('<channel> <target_us>: ')
            if not command:
                return

            channel, target_us = command.split()

            channel = int(channel)
            target_us = float(target_us)

            maestro.set_target(channel, target_us)

        while True:
            try:
                handle_command()
            except KeyboardInterrupt:
                print()
                print('Exiting')
                return
            except Exception as e:
                print(f'Error: {e!r}')


if __name__ == '__main__':
    main()
