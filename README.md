<div align="center">

# Bank HEIST

**A terminal-based stealth game. Rob the bank. Don't get caught.**

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Platform](https://img.shields.io/badge/Platform-Linux%20%7C%20macOS%20%7C%20WSL-lightgrey?style=for-the-badge)
![Library](https://img.shields.io/badge/Library-curses-informational?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-brightgreen?style=for-the-badge)

</div>

---

## 📋 Table of Contents

- [About](#-about)
- [Features](#-features)
- [Gameplay](#-gameplay)
- [Controls](#-controls)
- [Getting Started](#-getting-started)
- [Project Structure](#-project-structure)
- [Architecture](#-architecture)
- [Levels](#-levels)
- [Contributing](#-contributing)
- [License](#-license)

---

##  About

HEIST is a top-down terminal stealth game built entirely with Python's `curses` library — no external dependencies. Navigate a bank floor, crack open safes, evade patrolling guards and surveillance cameras, and escape through the exit. Every element — walls, characters, UI — is rendered with Unicode block characters directly in your terminal.

> Inspired by classic ASCII roguelikes, built for the modern terminal.

---

## ✨ Features

- 🗺️ **4 handcrafted levels** — Tutorial, Level 1, Level 2, and Level 3, each with a unique floor plan
- 👮 **Patrolling guards** — follow fixed routes shown at level start; trigger camera alerts to move at 2× speed
- 📷 **Security cameras** — detect the player from one tile ahead; can be broken from behind
- 🔒 **Doors & hatches** — vertical and horizontal doors that the player can open and close
- 💰 **Safes** — walk into them to collect cash; open all for a perfect run
- 📊 **HUD counters** — live turn count and cash total displayed in pixel-style block numerals
- ⏸️ **Pause menu** — Resume, Retry, or return to Main Menu mid-game
- 🏆 **End-of-level scoring** — rated on `(cash / turns) × 100`; distinguishes full clears from escapes
- ⚠️ **Terminal size check** — warns and quits gracefully if the window is too small

---

## 🎮 Gameplay

1. Navigate the bank floor using the arrow keys
2. Walk **into** safes to crack them and collect **$100** each
3. Use `X` when **facing** a door or camera to interact with it
4. Stay off patrol routes — patrollers detect you when adjacent with a clear line of sight
5. Cameras watching you (`◩◁` → `▧⯇`) make the patroller move twice per turn
6. Break a camera from **behind** (`░░`) to disable it permanently
7. Reach the `EXIT` (`╔═══\`) to end the level — open all safes first for maximum score

### Win / Lose conditions

| Outcome | Trigger |
|---|---|
| **SUCCESS** | Reached exit with all safes open (`score == MAX_SCORE`) |
| **ESCAPE** | Reached exit with safes remaining |
| **BUSTED** | Patroller entered the same tile or was adjacent with clear line of sight |

---

## 🕹️ Controls

| Key | Action |
|---|---|
| `↑` `↓` `←` `→` | Move player |
| `X` | Interact (open door / break camera) |
| `Q` | Open pause menu |
| `↑` / `↓` + `X` | Navigate and confirm menus |

---

## 🚀 Getting Started

### Prerequisites

- Python **3.10+** (uses `match`/`case` syntax)
- A Unix-like terminal: **Linux**, **macOS**, or **WSL** on Windows
- Terminal window at least **25 rows × 150 columns** (maximise before launching)

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/Fahim519-ui/Bank-Heist-Game.git
cd Bank-Heist-Game/Heist

# 2. No pip installs needed — standard library only
python main.py
```

> **Windows users:** Run inside WSL or a terminal emulator that supports the `curses` module (e.g. Windows Terminal with WSL2).

---

## 📁 Project Structure

```
Bank-Heist-Game/
└── Heist/
    ├── main.py              # Entry point — curses init, colour pairs, launches Title
    └── heist/
        ├── constants.py     # Colors, Keys, Displacements (all magic numbers live here)
        ├── graphics.py      # draw_box / draw_outline / draw_route + all sprite dictionaries
        ├── entity.py        # Entity class hierarchy (Entity → Movable/Interactable → Player/Patroller/Safe/Door/Camera…)
        ├── maps.py          # Map class hierarchy (Map → Game → First/Second/Third/Tutorial + Title + PauseMenu)
        └── user.py          # User — wraps stdscr, tracks terminal dimensions, handles resize
```

---

## 🏗️ Architecture

The game is built around two parallel class hierarchies that communicate through a shared curses pad.

### Entity hierarchy (`entity.py`)

```
Entity                      ← base: model dict, (y, x), color, show()/hide()
├── Counter                 ← HUD display for turn count and cash total
├── Exit                    ← static exit marker
├── Movable                 ← animated movement with smooth sub-step interpolation
│   ├── Player              ← user-controlled; holds score; interact_front()
│   └── Patroller           ← route-following AI; adjacent/overlap detection; camera-triggered speed
└── Interactable            ← objects with coordinate-keyed registry (Interactable.entities)
    ├── Safe                ← adds $100 to player.score on first interaction
    ├── Door                ← vertical; toggled open/closed
    ├── Hatch               ← horizontal; toggled open/closed
    └── Camera              ← directional; surveil(), interact() to break from rear
```

**Key design choices:**
- `Interactable.entities` is a class-level dict keyed by `(y, x)` — lets `Player.interact_front()` look up any interactable by coordinate without coupling entities together
- Movement is animated: `move_to()` interpolates 3 sub-steps with `sleep(0.05–0.06)` between each, giving smooth sliding motion
- `front_point()` computes the tile ahead of a `Movable` based on its current `state` (direction), used for both collision and interaction checks

### Map hierarchy (`maps.py`)

```
Map                         ← base: curses pad, render(), play() loop, entity cleanup
├── Title                   ← main menu; level select with hover-state buttons
├── PauseMenu               ← Resume / Retry / Main Menu; called from inside Game.loop()
└── Game                    ← HUD setup, unified game loop (input → move → patrol → camera → score)
    ├── Tutorial            ← 1 safe, 1 patroller, 1 camera; teaches core mechanics
    ├── First               ← 6 safes, 1 patroller, 2 cameras; long snaking route
    ├── Second              ← 6 safes, 2 patrollers, 1 camera; grid-style floor plan
    └── Third               ← 6 safes, 2 patrollers, 2 cameras; most complex layout
```

### Color system (`constants.py`)

Curses color pairs are initialised once in `main()` and referenced via integer offsets:

| Constant | Pair | Usage |
|---|---|---|
| `WHITE_BLACK` | 0 | Walls, doors, default |
| `BLACK_WHITE` | 256 | Background fill |
| `RED_BLACK` | 512 | Player, patrollers, patrol routes |
| `YELLOW_BLACK` | 768 | HUD, title, tutorial text |
| `YELLOW_RED` | 1024 | Alert state |
| `WHITE_RED` | 1280 | Danger overlay |

---

## 🗺️ Levels

| Level | Safes | Patrollers | Cameras | Max Score | Start position |
|---|---|---|---|---|---|
| Tutorial | 1 | 1 | 1 | $100 | Bottom-left area |
| Level 1 | 6 | 1 | 2 | $600 | Bottom-left |
| Level 2 | 6 | 2 | 1 | $600 | Top-right |
| Level 3 | 6 | 2 | 2 | $600 | Top-left |

Patrol routes are drawn on-screen at load time using `┊` (vertical) and `┄` (horizontal) characters so you can plan before moving.

