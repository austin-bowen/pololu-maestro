# pololu-maestro

Python driver for the [Pololu Maestro](https://www.pololu.com/category/102/maestro-usb-servo-controllers) series of servo controllers.

Originally cloned from: [FRC4564/Maestro](https://github.com/FRC4564/Maestro/)


# Example Usage

```python
from maestro import MicroMaestro, MiniMaestro

# Connect to a Micro Maestro
with MicroMaestro.connect() as maestro:
    # Set targets of servos 0-3 to 1500, 1600, 1700, and 1800 us
    maestro.set_target(0, 1500)
    maestro[1] = 1600
    maestro[2:4] = [1700, 1800]

    # Get targets
    assert maestro.get_target(0) == 1500
    assert maestro[1] == 1600
    assert maestro[0:4] == [1500, 1600, 1700, 1800]

# After leaving the block, the Maestro is told to stop sending signals
# to the servos, and the connection is automatically closed

# Connect to a Mini Maestro 12
with MiniMaestro.connect(channels=12) as maestro:
    # Servo position may not equal the target
    # if speed or acceleration are set, e.g.:
    # Move servo 10 from 1000 to 2000 us at low speed
    maestro.set_target(10, 1000)
    maestro.set_speed(10, 1)
    maestro.set_target(10, 2000)

    assert maestro.is_moving(10)
    assert maestro.get_position(10) != maestro.get_target(10)
    
    maestro.wait_until_done_moving()
    
    assert not maestro.is_moving(10)
    assert maestro.get_position(10) == maestro.get_target(10)
```

## Methods

The `MicroMaestro` and `MiniMaestro` classes have the following methods:

### Positioning
- `set_target(channel: int, target_us: float)`: Set the target position of a servo.
- `get_target(channel: int) -> float`
- `set_targets(targets: dict[int, float])`: Set the target positions of multiple servos at once.
- `get_targets() -> list[float]`
- `get_position(channel: int) -> float`: Get the current position of a servo. May differ from the target if speed or acceleration is non-zero.
- `get_positions() -> list[float]`
- `set_limits(channel: int, min_us: float = None, max_us: float = None)`
- `get_limits(channel: int) -> tuple[Optional[float], Optional[float]]`
- `stop_channel(channel: int)`: Stop sending signals to a servo.
- `stop()`: Stop all channels.
- `go_home()`: Set all servos to their home positions.
- `is_moving(channel: int) -> bool`
- `any_are_moving() -> bool`
- `wait_until_done_moving(poll_period: float = 0.1)`

### Speed
- `set_speed(channel: int, speed: int)`
- `get_speed(channel: int) -> int`
- `get_speeds() -> list[int]`

### Acceleration
- `set_acceleration(channel: int, acceleration: int)`
- `get_acceleration(channel: int) -> int`
- `get_accelerations() -> list[int]`

### Scripting
- `run_script_subroutine(subroutine: int, parameter: int = None)`
- `script_is_running() -> bool`
- `stop_script()`

### Other
- `get_errors() -> int`
- `MiniMaestro` only:
  - `set_pwm(on_time_us: float, period_us: float)`

## Interactive Mode

The module can be run to interactively control the servo targets:

```bash
python -m maestro {micro,mini12,mini18,mini24} [--tty TTY]
```


# Installation & Setup

```bash
pip install git+https://github.com/austin-bowen/pololu-maestro.git
```

## Setup System

On Linux, to connect to serial ports without root permissions, you may need to add your user to the `dialout` group:

```bash
sudo usermod -aG dialout $USER
```

Then log out and back in. Do this step if you get "Permission denied" errors connecting to the Maestro.

## Setup Maestro

1. Open the [Maestro Control Center](https://www.pololu.com/docs/0J40/4) ([Windows](https://www.pololu.com/docs/0J40/3.a) / [Linux](https://www.pololu.com/docs/0J40/3.b)) and connect it to your Maestro.
2. Go to the [Serial Settings tab](https://www.pololu.com/docs/0J40/5.a), and make sure the Serial mode is set to either "USB Dual Port" or "USB Chained".


# Local Development

Setup:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -e .[test]
```

Run unit tests and view coverage:

```bash
./test
```
