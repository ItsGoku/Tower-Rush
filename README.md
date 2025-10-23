# Tower Rush

Tower Rush is a fast-paced, top-down arena shooter built with Pygame. Climb endless tower floors, survive escalating enemy waves, and fine-tune your build between runs with permanent upgrades.

## Features

- **Floor-based progression** – fight through increasingly challenging floors with mini-waves and milestone boss encounters.
- **Enemy variety** – melee bruisers, long-range artillery, speedy skirmishers, and bosses that evolve as you climb.
- **Dynamic bosses** – milestone bosses unleash homing core projectiles you can shoot down, plus special bonuses at Floors 25/50/75/100.
- **Power-ups** – collect timed boosts like Piercing Shots, Heavy Rounds, Rapid Fire, Multi Shot, and Speed Boost to adapt on the fly.
- **Meta-upgrades** – invest coins in the upgrade workshop for permanent movement, fire-rate, damage, economy, and auto-fire boosts.
- **Hidden admin key** – press `G` to instantly max out all workshop upgrades (handy for testing or casual play).

## Requirements

- Python 3.9+
- [Pygame](https://www.pygame.org/) 2.1+

Install dependencies:

```bash
pip install pygame
```

## Getting Started

Clone or download the project, then launch the game from the root directory:

```bash
python tower_rush.py
```

## Controls

| Action                | Key / Mouse |
|-----------------------|-------------|
| Move                  | `W` `A` `S` `D` |
| Aim                   | Mouse       |
| Fire                  | Left mouse button |
| Pause / Resume        | `ESC`       |
| Restart run           | `R` (in-game or paused) |
| Upgrade workshop      | `U` (from menu, paused, or game over) |
| Admin max-upgrade key | `G`         |

## Gameplay Tips

- **Piercing Shots** let bullets pass through enemies *and* enemy projectiles when active—chain it with Multi Shot for crowd control.
- **Auto-fire upgrades** drastically shorten their cooldown at higher levels. Prioritize them if you want semi-idle support damage.
- **Homing cores** fired by bosses can be destroyed; focus them down before they corner you.
- **Coin management** – floor clear and boss rewards scale with progression. Bank coins regularly to unlock more workshop tiers.
- **Use pause wisely** – pausing (`ESC`) freezes power-up timers, so you can strategize without wasting buffs.

Enjoy the climb, and may your run reach the highest floor!
