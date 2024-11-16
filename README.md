# pololu-maestro

Python 3 driver for the Pololu Maestro series of servo controllers.

Originally cloned from: [FRC4564/Maestro](https://github.com/FRC4564/Maestro/)


# Usage

TODO: Add Python examples.

## Interactive Mode

The module can be run to interactively control the servo targets:

```bash
python -m maestro
```


# Installation

```bash
pip install git+https://github.com/austin-bowen/pololu-maestro.git
```

On Linux, to connect to serial ports without root permissions, you may need to add your user to the `dialout` group:

```bash
sudo usermod -aG dialout $USER
```

Then log out and back in.


# Local Development

```bash
python3 -m venv venv
source venv/bin/activate
pip install -e .
```
