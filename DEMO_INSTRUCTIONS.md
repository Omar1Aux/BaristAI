# BaristAI Demo Shots Package

This package contains demo espresso machine processes for Project Day.

## Files

- `demo_shots.csv`
- `demo_live_streamer.py`

## Demo Processes

| process_id | Scenario | What it shows |
|---|---|---|
| 101 | Good extraction | Temperature, pressure, and time close to target |
| 102 | Low pressure / under-extraction | Pressure below target and extraction too short |
| 103 | High pressure / restricted puck | Pressure too high and extraction too long |
| 104 | Low temperature | Temperature below target |
| 105 | Too short extraction | Extraction time too short |
| 106 | Too long extraction | Extraction time too long |
| 107 | Heating / not a brew shot | Non-brew process to show process-aware logic |

## How to Run

1. Copy both files into your BaristAI project folder.

2. Start Flask:

```powershell
python app.py
```

3. Open dashboard:

```text
http://127.0.0.1:5000
```

4. Press **Real Live**.

5. In another terminal, run one demo process:

```powershell
python demo_live_streamer.py --process-id 101 --delay 0.5
```

## Recommended Project Day Demo Order

```powershell
python demo_live_streamer.py --process-id 101 --delay 0.5
python demo_live_streamer.py --process-id 102 --delay 0.5
python demo_live_streamer.py --process-id 103 --delay 0.5
python demo_live_streamer.py --process-id 104 --delay 0.5
python demo_live_streamer.py --process-id 107 --delay 0.5
```

## Talking Point

"We prepared several demo processes to show how BaristAI reacts to normal extraction, low pressure, high pressure, low temperature, short extraction, long extraction, and non-brewing machine processes."
