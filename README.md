# ❄️ Snow Simulator

A terminal-based snow simulator built with Python and curses.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)
![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)

## Features

- **Dynamic Snowfall** - Snow intensity varies over time
- **Snow Piling** - Snow accumulates on the ground
- **Collapse Mechanics** - Tall snow piles collapse under their own weight
- **Melting** - At temperatures above 2°C, snow melts
- **Temperature System** - Cold snow is lighter, warm snow melts faster
- **Wind Effects** - Snowflakes drift with wind

## Installation

```bash
git clone https://github.com/comShadowHarvy/snowsim.git
cd snowsim

uv run python -m snow_sim
```

Or with pip:
```bash
pip install .
snow-sim
```

## Controls

| Key | Action |
|-----|--------|
| `+` / `=` | Increase snow intensity |
| `-` | Decrease snow intensity |
| `T` | Cycle temperature |
| `W` | Toggle wind |
| `Q` | Quit |

## Temperature States

- **< -5°C**: Freezing - Snow accumulates quickly
- **-5 to 2°C**: Accumulating - Normal snowfall
- **> 2°C**: Melting - Snow begins to melt

## Requirements

- Python 3.10+
- Terminal with 256-color support
- curses (included with Python)

## License

MIT License - See LICENSE file for details.

---

Made with ❤️ by [comShadowHarvy](https://github.com/comShadowHarvy)