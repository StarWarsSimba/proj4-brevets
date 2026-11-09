# ACP Brevet Controle Time Calculator

Ajax + Flask reimplementation of the RUSA ACP calculator (https://rusa.org/octime_acp.html). Computes open/close times for each controle and fills them via Ajax without page reloads.

Based on RUSA rules at https://rusa.org/pages/acp-brevet-control-times-calculator / https://rusa.org/octime_alg.html. Skeleton by Michal Young for CIS 322.

## Overview

Brevets are 200/300/400/600/1000 km. Each controle must be reached after its **open** time and before its **close** time. This app lets a rider select a brevet distance, start date/time, and controle distances (miles or km, 20 rows, bidirectional conversion at `brevets/templates/calc.html:148`), then displays open/close times via `GET /_calc_times` (`brevets/flask_brevets.py:47`) calling `brevets/acp_times.py:20` and `brevets/acp_times.py:51`. Times are ISO 8601 (Arrow) and rendered with `moment.js` as `ddd M/D H:mm`.

## ACP Controle Time Rules

All logic is in `brevets/acp_times.py`.

**Valid distances:** `brevet_dist_km` must be 200, 300, 400, 600, or 1000 else `ValueError`. `control_dist_km` must be > 0 else `ValueError`. Controls beyond the brevet are clamped (see below).

**Open time (max speed):** distance `d = min(control, brevet)`:
- 0–200 km: 34 km/h → `min(d,200)/34`
- 200–400 km: 32 km/h → `+ min(d-200,200)/32`
- 400–600 km: 30 km/h → `+ min(d-400,200)/30`
- 600–1000 km: 28 km/h → `+ min(d-600,400)/28`

Rounded to nearest minute: `arrow.get(start).shift(minutes=round(hours*60)).isoformat()`.

**Close time (min speed):**
- 0–60 km: `d/20 + 1` hour (1h grace; e.g., 20 km → 2:00, not 1:20)
- 60–600 km: 15 km/h → `min(d,200)/15 + min(d-200,200)/15 + min(d-400,200)/15`
- 600–1000 km: 11.428 km/h → `+ min(d-600,400)/11.428` (makes 1000 km = 75h)

**French finishing variations** — only when `control == brevet`:
- 200 km finish: 13:30 (not 13:20)
- 400 km finish: 27:00 (not 26:40)
- 300/600/1000 km finishes match the formula (20:00/40:00/75:00). An intermediate 200 km on a 300 km brevet closes at 13:20.

**Beyond brevet:** open clamps when `control > brevet`, close when `control >= brevet` (`brevets/acp_times.py:36`, `brevets/acp_times.py:67`). E.g., 205 km on a 200 km brevet → same as 200 km (open 5:53, close 13:30). Verified against https://rusa.org/octime_acp.html.

**Timezone/rounding:** Input is ISO 8601; Flask builds `begin_date + "T" + begin_time + "-00:00"`. Output preserves that timezone.

**Examples** (start `2024-01-01T00:00+00:00`):

| Brevet | Control | Open | Close | Note |
|--------|---------|------|-------|------|
| 200 | 60 km | 1:46 | 4:00 | 60/34, 60/15 |
| 200 | 200 km | 5:53 | 13:30 | special |
| 400 | 350 km | 10:34 | 23:20 | spans brackets |
| 1000 | 1000 km | 33:05 | 75:00 |  |

## Installation & Running

```bash
git clone https://github.com/StarWarsSimba/proj4-brevets.git
cd proj4-brevets
python3 -m venv brevets/.venv && source brevets/.venv/bin/activate
pip install -r brevets/requirements.txt  # arrow, Flask, pynose
cd brevets
python flask_brevets.py              # or: python flask_brevets.py --port 5001 --debug
# open http://localhost:5001
```

**Config** (`brevets/config.py:103`): `brevets/credentials.ini` (`PORT`, `SECRET_KEY`) overridden by CLI `-D`/`-P`/`-C`. `SECRET_KEY` required for Flask sessions.

**Using:** Select brevet distance and start date/time, enter miles or km — the other converts automatically and `calc_times()` (`brevets/templates/calc.html:125`) populates Open/Close.

## API

`GET /_calc_times?km=<float>&brevet_distance=<int>&begin_date=YYYY-MM-DD&begin_time=HH:MM` → `{"result":{"open":"...","close":"..."}}` (ISO 8601). Used at `brevets/templates/calc.html:133`.

```python
import acp_times
acp_times.open_time(100, 200, "2024-01-01T08:00:00-08:00")  # "2024-01-01T10:56:00-08:00"
```

## Project Structure

```
proj4-brevets/README.md
brevets/acp_times.py        # open_time / close_time
brevets/flask_brevets.py    # Flask app + /_calc_times
brevets/config.py           # INI + CLI layering
brevets/templates/calc.html # table + Ajax
brevets/tests.py            # nose suite
brevets/Dockerfile          # FROM python:3, pip install, CMD flask_brevets.py
```

## Testing

```bash
cd brevets && source .venv/bin/activate && nosetests -v  # 5 tests
```

Tests cover 60 km open, 200 km French close, multi-bracket 350 km, clamping beyond brevet, invalid distance (`brevets/tests.py:1`).

## Docker

```bash
cd brevets && docker build -t brevets . && docker run -p 5001:5001 brevets
```

## References

- https://rusa.org/octime_acp.html, https://rusa.org/octime_alg.html, https://rusa.org/pages/rulesForRiders

## Author

**Miles Gurney** — CIS 322, University of Oregon — `mgurney@uoregon.edu` — [@StarWarsSimba](https://github.com/StarWarsSimba) — https://github.com/StarWarsSimba/proj4-brevets