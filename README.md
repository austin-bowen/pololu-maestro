# pololu-maestro

Python driver for the [Pololu Maestro](https://www.pololu.com/category/102/maestro-usb-servo-controllers) series of servo controllers.

Originally cloned from: [FRC4564/Maestro](https://github.com/FRC4564/Maestro/)


# Usage

```python
from maestro import MicroMaestro, MiniMaestro

# Connect to a Mini Maestro and set the target of servo 0 to 1500 microseconds
with MicroMaestro.connect() as maestro:
    maestro.set_target(0, 1500)
# Signals stop being sent to the servos and the connection is automatically
# closed after leaving the block

# Connect to a Mini Maestro 12 and get the position of servo 1
with MiniMaestro.connect(channels=12) as maestro:
    print('Servo 1 position:', maestro.get_position(1))
```

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

```bash
python3 -m venv venv
source venv/bin/activate
pip install -e .
```
