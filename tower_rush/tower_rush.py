"""Tower Rush - top-down arena shooter built with Pygame."""

import math
import random
import sys
from array import array

import pygame

WIDTH, HEIGHT = 1600, 900
FPS = 60

PLAYER_SPEED = 240
PLAYER_RADIUS = 20
PLAYER_COLOR = (80, 160, 255)
INVULNERABILITY_DURATION = 2000
HIT_FLASH_DURATION = 200

BULLET_SPEED = 600
BULLET_BASE_RADIUS = 6
BULLET_BIG_MULTIPLIER = 1.6
BULLET_SPREAD_ANGLE = 14
BULLET_COLOR = (255, 220, 120)
BULLET_DAMAGE = 1
BIG_BULLET_BONUS = 1
MULTI_SHOT_COUNT = 3
AUTO_FIRE_BASE_COOLDOWN = 2.2
AUTO_FIRE_COOLDOWN_STEP = 0.3

ENEMY_RADIUS = 24
ENEMY_BASE_SPEED = 100
ENEMY_SPEED_INCREMENT = 4
ENEMY_SPAWN_MARGIN = 40
BASE_LIVES = 3

ENEMY_VARIANTS = (
    {
        "name": "raider",
        "color": (220, 70, 70),
        "speed_mult": 1.0,
        "health": 1,
        "radius": ENEMY_RADIUS,
        "score": 1,
        "reward": 2,
    },
    {
        "name": "brute",
        "color": (240, 150, 70),
        "speed_mult": 0.72,
        "health": 3,
        "radius": ENEMY_RADIUS + 4,
        "score": 2,
        "reward": 3,
    },
    {
        "name": "warden",
        "color": (120, 200, 150),
        "speed_mult": 0.55,
        "health": 5,
        "radius": ENEMY_RADIUS + 6,
        "score": 3,
        "reward": 4,
    },
    {
        "name": "speedster",
        "color": (255, 230, 120),
        "speed_mult": 1.35,
        "health": 2,
        "radius": ENEMY_RADIUS - 4,
        "score": 3,
        "reward": 2,
        "random_move": True,
    },
    {
        "name": "artillery",
        "color": (180, 120, 255),
        "speed_mult": 0.45,
        "health": 4,
        "radius": ENEMY_RADIUS + 2,
        "score": 4,
        "reward": 3,
        "ranged": True,
        "fire_interval": 1800,
        "projectile_speed": 420,
        "projectile_damage": 1,
        "projectile_color": (255, 160, 90),
    },
)

BOSS_FLOOR_INTERVAL = 5
BOSS_BASE_SPEED = 80
BOSS_SPEED_INCREMENT = 4
BOSS_BASE_HEALTH = 24
BOSS_HEALTH_INCREMENT = 6
BOSS_RADIUS = 52
BOSS_COLOR = (255, 90, 160)
BOSS_SCORE_VALUE = 10
BOSS_REWARD_BASE = 40
BOSS_REWARD_INCREMENT = 12

POWERUP_SIZE = 26
POWERUP_DURATION = 8000
POWERUP_INTERVAL = 25000
NORMAL_POWERUPS = ("speed", "fire_rate", "big_bullet", "multi_shot", "piercing")
SESSION_POWERUPS = ("perma_fire_rate", "perma_damage")
POWERUP_WEIGHTS = {
    "speed": 3,
    "fire_rate": 3,
    "big_bullet": 2,
    "multi_shot": 2,
    "piercing": 2,
}
POWERUP_COLORS = {
    "speed": (120, 220, 255),
    "fire_rate": (255, 200, 90),
    "big_bullet": (255, 150, 120),
    "multi_shot": (190, 160, 255),
    "piercing": (140, 255, 200),
    "perma_fire_rate": (255, 110, 180),
    "perma_damage": (255, 90, 120),
}
POWERUP_LABELS = {
    "speed": "Speed Boost",
    "fire_rate": "Rapid Fire",
    "big_bullet": "Heavy Rounds",
    "multi_shot": "Multi Shot",
    "piercing": "Piercing Shots",
    "perma_fire_rate": "Session Fire Rate",
    "perma_damage": "Session Damage",
}

FIRE_COOLDOWN = 0.25
SPEED_MULTIPLIER = 1.5
FIRE_RATE_MULTIPLIER = 0.6
PERMA_FIRE_RATE_MULTIPLIER = 0.9
PERMA_DAMAGE_BONUS = 1

FLOOR_REWARD_BASE = 12
FLOOR_REWARD_SCALE = 4
FLOOR_DELAY = 2000

BG_COLOR = (18, 18, 22)
HUD_COLOR = (240, 240, 240)
ACCENT_COLOR = (90, 200, 250)
PAUSE_OVERLAY = (0, 0, 0, 150)

META_UPGRADE_DEFS = {
    "speed": {
        "label": "Agility",
        "base_cost": 120,
        "cost_scale": 1.65,
        "max_level": 8,
        "description": "+5% move speed",
    },
    "fire_rate": {
        "label": "Trigger Discipline",
        "base_cost": 130,
        "cost_scale": 1.7,
        "max_level": 8,
        "description": "+8% fire rate",
    },
    "starting_hp": {
        "label": "Reserves",
        "base_cost": 160,
        "cost_scale": 1.8,
        "max_level": 5,
        "description": "+1 starting heart",
    },
    "money": {
        "label": "Spoils Bonus",
        "base_cost": 140,
        "cost_scale": 1.7,
        "max_level": 6,
        "description": "+12% more coins",
    },
    "damage": {
        "label": "Ballistics",
        "base_cost": 150,
        "cost_scale": 1.75,
        "max_level": 6,
        "description": "+1 base damage",
    },
    "auto_fire": {
        "label": "Auto Salvo",
        "base_cost": 220,
        "cost_scale": 1.85,
        "max_level": 5,
        "description": "Unlocks auto fire, higher levels shorten cooldown",
    },
}

META_UPGRADE_ORDER = [
    "speed",
    "fire_rate",
    "starting_hp",
    "money",
    "damage",
    "auto_fire",
]


def generate_beep(frequency=440, duration=0.1, volume=0.5):
    """Create a short sine-wave beep for placeholder audio."""
    mixer_init = pygame.mixer.get_init()
    if mixer_init is None:
        raise pygame.error("Mixer not initialised")
    sample_rate = mixer_init[0]
    sample_count = int(sample_rate * duration)
    amplitude = int(32767 * volume)
    samples = array("h", [0] * sample_count)
    for i in range(sample_count):
        angle = 2 * math.pi * frequency * i / sample_rate
        samples[i] = int(amplitude * math.sin(angle))
    return pygame.mixer.Sound(buffer=samples.tobytes())


def circle_collision(pos_a, radius_a, pos_b, radius_b):
    return (pos_a - pos_b).length_squared() <= (radius_a + radius_b) ** 2

class Player:
    def __init__(self, position):
        self.position = pygame.math.Vector2(position)
        self.radius = PLAYER_RADIUS
        self.color = PLAYER_COLOR
        self.base_speed = PLAYER_SPEED
        self.speed = PLAYER_SPEED
        self.base_cooldown = FIRE_COOLDOWN
        self.cooldown = FIRE_COOLDOWN
        self.next_shot_time = 0
        self.base_bullet_radius = BULLET_BASE_RADIUS
        self.bullet_radius = BULLET_BASE_RADIUS
        self.base_bullet_damage = BULLET_DAMAGE
        self.bullet_damage = BULLET_DAMAGE
        self.shot_count = 1
        self.power_timers = {}
        self.permanent_upgrades = {
            "fire_rate": 0,
            "damage": 0,
        }
        self.invulnerable_until = 0
        self.hit_flash_end = 0
        self.piercing_active = False

    def update(self, dt, keys):
        direction = pygame.math.Vector2(0, 0)
        if keys[pygame.K_w]:
            direction.y -= 1
        if keys[pygame.K_s]:
            direction.y += 1
        if keys[pygame.K_a]:
            direction.x -= 1
        if keys[pygame.K_d]:
            direction.x += 1
        if direction.length_squared() > 0:
            direction = direction.normalize()
        self.position += direction * self.speed * dt
        self.position.x = max(
            self.radius, min(WIDTH - self.radius, self.position.x)
        )
        self.position.y = max(
            self.radius, min(HEIGHT - self.radius, self.position.y)
        )

    def update_powerups(self, now):
        expired = [
            name
            for name, end in self.power_timers.items()
            if now >= end
        ]
        for name in expired:
            if name == "speed":
                self.speed = self.base_speed
            elif name == "fire_rate":
                self.cooldown = self.base_cooldown
            elif name == "big_bullet":
                self.bullet_radius = self.base_bullet_radius
                self.bullet_damage = self.base_bullet_damage
            elif name == "multi_shot":
                self.shot_count = 1
            elif name == "piercing":
                self.piercing_active = False
            del self.power_timers[name]

    def apply_powerup(self, name, now):
        if name == "speed":
            self.speed = self.base_speed * SPEED_MULTIPLIER
            self.power_timers[name] = now + POWERUP_DURATION
        elif name == "fire_rate":
            self.cooldown = self.base_cooldown * FIRE_RATE_MULTIPLIER
            self.power_timers[name] = now + POWERUP_DURATION
        elif name == "big_bullet":
            self.bullet_radius = int(
                self.base_bullet_radius * BULLET_BIG_MULTIPLIER
            )
            self.bullet_damage = self.base_bullet_damage + BIG_BULLET_BONUS
            self.power_timers[name] = now + POWERUP_DURATION
        elif name == "multi_shot":
            self.shot_count = MULTI_SHOT_COUNT
            self.power_timers[name] = now + POWERUP_DURATION
        elif name == "piercing":
            self.piercing_active = True
            self.power_timers[name] = now + POWERUP_DURATION
        elif name == "perma_fire_rate":
            self.permanent_upgrades["fire_rate"] += 1
            self.base_cooldown *= PERMA_FIRE_RATE_MULTIPLIER
            self.cooldown = self.base_cooldown
        elif name == "perma_damage":
            self.permanent_upgrades["damage"] += 1
            self.base_bullet_damage += PERMA_DAMAGE_BONUS
            if "big_bullet" in self.power_timers:
                self.bullet_damage = (
                    self.base_bullet_damage + BIG_BULLET_BONUS
                )
            else:
                self.bullet_damage = self.base_bullet_damage

    def draw(self, surface, now):
        color = self.color
        if now < self.hit_flash_end:
            color = (255, 120, 120)
        elif now < self.invulnerable_until and (now // 120) % 2 == 0:
            color = (200, 200, 255)
        center = (int(self.position.x), int(self.position.y))
        pygame.draw.circle(surface, color, center, self.radius)
        if now < self.invulnerable_until:
            pygame.draw.circle(
                surface,
                (255, 255, 255),
                center,
                self.radius + 4,
                width=2,
            )


class Bullet:
    def __init__(self, position, direction, radius, damage, piercing=False):
        self.position = pygame.math.Vector2(position)
        if direction.length_squared() > 0:
            self.velocity = direction.normalize() * BULLET_SPEED
        else:
            self.velocity = pygame.math.Vector2()
        self.radius = radius
        self.damage = damage
        self.piercing = piercing

    def update(self, dt):
        self.position += self.velocity * dt

    def draw(self, surface):
        center = (int(self.position.x), int(self.position.y))
        pygame.draw.circle(surface, BULLET_COLOR, center, self.radius)

    def is_offscreen(self):
        return (
            self.position.x < -self.radius
            or self.position.x > WIDTH + self.radius
            or self.position.y < -self.radius
            or self.position.y > HEIGHT + self.radius
        )


class EnemyProjectile:
    def __init__(
        self,
        position,
        velocity,
        damage,
        color,
        radius=8,
        destroyable=False,
        hit_points=0,
        homing=False,
        owner=None,
        speed=None,
    ):
        self.position = pygame.math.Vector2(position)
        self.velocity = velocity
        self.damage = damage
        self.radius = radius
        self.color = color
        self.destroyable = destroyable
        self.hit_points = hit_points
        self.homing = homing
        self.owner = owner
        self.speed = speed if speed is not None else (self.velocity.length() if self.velocity.length_squared() > 0 else 0)

    def update(self, dt):
        self.position += self.velocity * dt

    def draw(self, surface):
        center = (int(self.position.x), int(self.position.y))
        pygame.draw.circle(surface, self.color, center, self.radius)

    def is_offscreen(self):
        return (
            self.position.x < -self.radius
            or self.position.x > WIDTH + self.radius
            or self.position.y < -self.radius
            or self.position.y > HEIGHT + self.radius
        )


class Enemy:
    def __init__(
        self,
        position,
        speed,
        color,
        health,
        radius,
        name,
        score_value,
        reward_value=0,
        is_boss=False,
        ranged=False,
        fire_interval=0,
        projectile_speed=0,
        projectile_damage=0,
        projectile_color=(255, 160, 90),
        random_move=False,
        special_shot_interval=0,
        special_shot_speed=0,
        special_shot_damage=0,
        special_shot_hp=0,
        special_shot_radius=12,
        special_projectile_color=(255, 205, 140),
    ):
        self.position = pygame.math.Vector2(position)
        self.speed = speed
        self.color = color
        self.health = health
        self.max_health = health
        self.radius = radius
        self.name = name
        self.score_value = score_value
        self.coin_value = reward_value
        self.is_boss = is_boss or name == "boss"
        self.ranged = ranged
        self.fire_interval = fire_interval
        self.projectile_speed = projectile_speed
        self.projectile_damage = projectile_damage
        self.projectile_color = projectile_color
        self.next_shot_time = 0
        self.active_special_projectile = None
        self.random_move = random_move
        self.direction = pygame.math.Vector2()
        self.direction_timer = 0.0
        self.special_shot_interval = special_shot_interval
        self.special_shot_speed = special_shot_speed
        self.special_shot_damage = special_shot_damage
        self.special_shot_hp = special_shot_hp
        self.special_shot_radius = special_shot_radius
        self.special_projectile_color = special_projectile_color
        self.next_special_shot_time = 0

    def _pick_random_direction(self):
        angle = random.uniform(0.0, 2 * math.pi)
        self.direction = pygame.math.Vector2(math.cos(angle), math.sin(angle))
        if self.direction.length_squared() == 0:
            self.direction = pygame.math.Vector2(1, 0)
        else:
            self.direction.normalize_ip()
        self.direction_timer = random.uniform(0.4, 1.0)

    def update(self, dt, target):
        if self.random_move:
            if self.direction.length_squared() == 0 or self.direction_timer <= 0:
                self._pick_random_direction()
            self.direction_timer -= dt
            self.position += self.direction * self.speed * dt
            clamped_x = max(self.radius, min(WIDTH - self.radius, self.position.x))
            clamped_y = max(self.radius, min(HEIGHT - self.radius, self.position.y))
            if clamped_x != self.position.x:
                self.direction.x *= -1
            if clamped_y != self.position.y:
                self.direction.y *= -1
            self.position.update(clamped_x, clamped_y)
            return
        direction = target - self.position
        if direction.length_squared() > 0:
            direction = direction.normalize()
            self.position += direction * self.speed * dt

    def try_shoot(self, now, target):
        if not self.ranged or now < self.next_shot_time:
            return None
        direction = target - self.position
        if direction.length_squared() == 0:
            return None
        direction = direction.normalize()
        velocity = direction * self.projectile_speed
        self.next_shot_time = now + self.fire_interval
        return EnemyProjectile(
            self.position,
            velocity,
            self.projectile_damage,
            self.projectile_color,
        )

    def draw(self, surface, now):
        center = (int(self.position.x), int(self.position.y))
        pygame.draw.circle(surface, self.color, center, self.radius)
        if self.is_boss:
            width = 220
            height = 18
            x = WIDTH / 2 - width / 2
            y = 20
            pygame.draw.rect(
                surface,
                (80, 80, 80),
                (x, y, width, height),
                border_radius=6,
            )
            ratio = max(0, self.health) / self.max_health
            pygame.draw.rect(
                surface,
                (255, 120, 150),
                (x + 2, y + 2, (width - 4) * ratio, height - 4),
                border_radius=5,
            )

    def take_damage(self, amount):
        self.health -= amount
        return self.health <= 0


class PowerUp:
    def __init__(self, name, position):
        self.name = name
        self.position = pygame.math.Vector2(position)
        self.size = POWERUP_SIZE

    def draw(self, surface):
        color = POWERUP_COLORS[self.name]
        rect = pygame.Rect(0, 0, self.size, self.size)
        rect.center = (int(self.position.x), int(self.position.y))
        pygame.draw.rect(surface, color, rect, border_radius=6)

class TowerRushGame:
    def __init__(self):
        pygame.init()
        try:
            pygame.mixer.init(frequency=44100, size=-16, channels=1)
            self.sound_enabled = True
        except pygame.error:
            self.sound_enabled = False
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Tower Rush")
        self.clock = pygame.time.Clock()
        self.title_font = pygame.font.SysFont("arial", 64)
        self.ui_font = pygame.font.SysFont("arial", 28)
        self.hud_font = pygame.font.SysFont("arial", 22)
        self.fire_sound = self.safe_beep(880, 0.05, 0.4)
        self.hit_sound = self.safe_beep(660, 0.08, 0.5)
        self.power_sound = self.safe_beep(520, 0.12, 0.4)
        self.damage_sound = self.safe_beep(220, 0.1, 0.6)
        self.state = "menu"
        self.player = None
        self.bullets = []
        self.enemies = []
        self.enemy_projectiles = []
        self.powerups = []
        self.score = 0
        self.lives = BASE_LIVES
        self.floor_number = 1
        self.waiting_for_floor = False
        self.floor_cleared_time = 0
        self.last_powerup_spawn = pygame.time.get_ticks()
        self.game_over_time = 0
        self.active_boss = None
        self.run_currency = 0
        self.currency = 0
        self.meta_upgrades = {
            name: 0 for name in META_UPGRADE_ORDER
        }
        self.meta_effects = {}
        self.state_before_shop = "menu"
        self.money_multiplier = 1.0
        self.auto_fire_level = 0
        self.auto_fire_cooldown = AUTO_FIRE_BASE_COOLDOWN
        self.auto_fire_shots = 0
        self.auto_fire_timer = 0.0
        self.pause_started_at = None
        self.update_meta_effects()

    def safe_beep(self, frequency, duration, volume):
        if not self.sound_enabled:
            return None
        try:
            return generate_beep(frequency, duration, volume)
        except pygame.error:
            return None

    def update_meta_effects(self):
        speed_level = self.meta_upgrades["speed"]
        fire_rate_level = self.meta_upgrades["fire_rate"]
        hp_level = self.meta_upgrades["starting_hp"]
        money_level = self.meta_upgrades["money"]
        damage_level = self.meta_upgrades["damage"]
        auto_level = self.meta_upgrades["auto_fire"]
        self.meta_effects = {
            "speed_multiplier": 1.0 + 0.05 * speed_level,
            "fire_rate_multiplier": 0.92 ** fire_rate_level,
            "starting_lives": BASE_LIVES + hp_level,
            "money_multiplier": 1.0 + 0.12 * money_level,
            "damage_bonus": damage_level,
            "auto_fire_level": auto_level,
            "auto_fire_cooldown": max(
                0.35,
                AUTO_FIRE_BASE_COOLDOWN * (0.82 ** auto_level),
            ),
            "auto_fire_shots": (
                0 if auto_level == 0 else min(3, 1 + auto_level // 2)
            ),
        }
        self.money_multiplier = self.meta_effects["money_multiplier"]
        self.auto_fire_level = self.meta_effects["auto_fire_level"]
        self.auto_fire_cooldown = self.meta_effects["auto_fire_cooldown"]
        self.auto_fire_shots = self.meta_effects["auto_fire_shots"]
        if self.auto_fire_level == 0:
            self.auto_fire_timer = float("inf")


    def extend_powerup_timers(self, offset_ms):
        if offset_ms <= 0:
            return
        if self.player:
            self.player.power_timers = {
                name: end_time + offset_ms
                for name, end_time in self.player.power_timers.items()
            }

    def max_out_meta_upgrades(self):
        for name, data in META_UPGRADE_DEFS.items():
            self.meta_upgrades[name] = data["max_level"]
        self.update_meta_effects()
        if self.state == "playing":
            self.apply_meta_to_player()
        self.play_sound(self.power_sound)

    def reset_game(self):
        self.player = Player((WIDTH / 2, HEIGHT / 2))
        self.apply_meta_to_player()
        self.bullets = []
        self.enemies = []
        self.enemy_projectiles = []
        self.powerups = []
        self.score = 0
        self.run_currency = 0
        self.floor_number = 1
        self.waiting_for_floor = False
        self.floor_cleared_time = 0
        now = pygame.time.get_ticks()
        self.last_powerup_spawn = now
        self.active_boss = None
        self.pause_started_at = None
        self.spawn_floor()

    def apply_meta_to_player(self):
        if self.player is None:
            return
        stats = self.meta_effects
        self.player.base_speed = PLAYER_SPEED * stats["speed_multiplier"]
        self.player.speed = self.player.base_speed
        self.player.base_cooldown = FIRE_COOLDOWN * (
            stats["fire_rate_multiplier"]
        )
        self.player.cooldown = self.player.base_cooldown
        self.player.base_bullet_damage = BULLET_DAMAGE + (
            stats["damage_bonus"]
        )
        self.player.bullet_damage = self.player.base_bullet_damage
        self.player.base_bullet_radius = BULLET_BASE_RADIUS
        self.player.bullet_radius = BULLET_BASE_RADIUS
        self.player.shot_count = 1
        self.player.power_timers.clear()
        self.player.permanent_upgrades = {
            "fire_rate": 0,
            "damage": 0,
        }
        self.lives = stats["starting_lives"]
        if stats["auto_fire_level"]:
            self.auto_fire_timer = self.auto_fire_cooldown
        else:
            self.auto_fire_timer = float("inf")
    def spawn_floor(self):
        if self.player is None:
            return
        self.enemies.clear()
        self.enemy_projectiles.clear()
        if self.floor_number % BOSS_FLOOR_INTERVAL == 0:
            boss = self.create_boss()
            self.enemies.append(boss)
            self.active_boss = boss
            return
        self.active_boss = None
        count = max(4, int(4 + self.floor_number * 1.4))
        for _ in range(count):
            enemy = self.create_enemy()
            self.enemies.append(enemy)

    def create_enemy(self):
        margin = ENEMY_SPAWN_MARGIN
        while True:
            side = random.choice(("top", "bottom", "left", "right"))
            if side == "top":
                x = random.uniform(0, WIDTH)
                y = -margin
            elif side == "bottom":
                x = random.uniform(0, WIDTH)
                y = HEIGHT + margin
            elif side == "left":
                x = -margin
                y = random.uniform(0, HEIGHT)
            else:
                x = WIDTH + margin
                y = random.uniform(0, HEIGHT)
            position = pygame.math.Vector2(x, y)
            if (
                self.player
                and (position - self.player.position).length() > 180
            ):
                break
        variant_pool = [ENEMY_VARIANTS[0]]
        if self.floor_number >= 3:
            variant_pool.append(ENEMY_VARIANTS[1])
        if self.floor_number >= 5:
            variant_pool.append(ENEMY_VARIANTS[2])
        if self.floor_number >= 4:
            variant_pool.append(ENEMY_VARIANTS[3])
        if self.floor_number >= 6:
            variant_pool.append(ENEMY_VARIANTS[4])
        variant = random.choice(variant_pool)
        boss_clears = max(0, (self.floor_number - 1) // BOSS_FLOOR_INTERVAL)
        base_speed = ENEMY_BASE_SPEED + boss_clears * ENEMY_SPEED_INCREMENT
        speed = base_speed * variant.get("speed_mult", 1.0)
        base_health = variant["health"] + boss_clears
        if variant["name"] == "speedster":
            base_health = 1
            speed *= 1.1
        return Enemy(
            position,
            speed,
            variant["color"],
            base_health,
            variant["radius"],
            variant["name"],
            variant["score"],
            reward_value=variant.get("reward", 2),
            ranged=variant.get("ranged", False),
            fire_interval=variant.get("fire_interval", 0),
            projectile_speed=variant.get("projectile_speed", 0),
            projectile_damage=variant.get("projectile_damage", 0),
            projectile_color=variant.get("projectile_color", (255, 160, 90)),
            random_move=variant.get("random_move", False),
        )


    def create_boss(self):
        margin = ENEMY_SPAWN_MARGIN + 60
        while True:
            x = random.uniform(margin, WIDTH - margin)
            y = random.uniform(margin, HEIGHT - margin)
            position = pygame.math.Vector2(x, y)
            if (position - self.player.position).length() > 260:
                break
        boss_cycle_index = max(0, self.floor_number // BOSS_FLOOR_INTERVAL - 1)
        floor_health_bonus = max(0, self.floor_number - 1) * (BOSS_HEALTH_INCREMENT // 2 + 1)
        health = BOSS_BASE_HEALTH + floor_health_bonus + boss_cycle_index * (BOSS_HEALTH_INCREMENT + 10)
        speed = BOSS_BASE_SPEED + boss_cycle_index * (BOSS_SPEED_INCREMENT + 2)
        fire_interval = max(700, 1400 - boss_cycle_index * 130)
        projectile_speed = 480 + boss_cycle_index * 20
        projectile_damage = 2 + boss_cycle_index // 2
        milestone = self.floor_number in {25, 50, 75, 100}
        if milestone:
            health += 80
            speed += 18
            fire_interval = max(600, fire_interval - 200)
            projectile_damage += 1
        special_interval = max(1500, 2400 - boss_cycle_index * 180)
        special_speed = 180 + boss_cycle_index * 20
        special_damage = 2 + (1 if milestone else 0)
        special_hp = 3 + boss_cycle_index // 2 + (2 if milestone else 0)
        special_radius = 16 if milestone else 12
        special_color = (255, 220, 140) if milestone else (255, 205, 140)
        if milestone:
            special_interval = max(1200, special_interval - 200)
            special_speed = min(360, special_speed + 60)
        enemy = Enemy(
            position,
            speed,
            BOSS_COLOR,
            health,
            BOSS_RADIUS,
            "boss",
            BOSS_SCORE_VALUE,
            reward_value=0,
            is_boss=True,
            ranged=True,
            fire_interval=fire_interval,
            projectile_speed=projectile_speed,
            projectile_damage=projectile_damage,
            projectile_color=(255, 120, 180),
            special_shot_interval=special_interval,
            special_shot_speed=special_speed,
            special_shot_damage=special_damage,
            special_shot_hp=special_hp,
            special_shot_radius=special_radius,
            special_projectile_color=special_color,
        )
        enemy.next_shot_time = 0
        enemy.next_special_shot_time = 0
        enemy.active_special_projectile = None
        return enemy


    def spawn_powerup(self):
        margin = 80
        x = random.uniform(margin, WIDTH - margin)
        y = random.uniform(margin, HEIGHT - margin)
        names = list(NORMAL_POWERUPS)
        weights = [POWERUP_WEIGHTS[name] for name in names]
        name = random.choices(names, weights=weights, k=1)[0]
        position = pygame.math.Vector2(x, y)
        if self.player and (position - self.player.position).length() < 120:
            position += pygame.math.Vector2(140, 0)
            position.x = min(max(position.x, margin), WIDTH - margin)
            position.y = min(max(position.y, margin), HEIGHT - margin)
        self.powerups.append(PowerUp(name, position))

    def reward_currency(self, base_amount):
        amount = int(round(base_amount * self.money_multiplier))
        if amount <= 0:
            return
        self.run_currency += amount
        self.currency += amount

    def floor_clear_reward(self):
        return FLOOR_REWARD_BASE + (self.floor_number - 1) * FLOOR_REWARD_SCALE

    def handle_boss_drop(self, position):
        reward = BOSS_REWARD_BASE + (
            max(0, self.floor_number // BOSS_FLOOR_INTERVAL - 1)
        ) * BOSS_REWARD_INCREMENT
        self.reward_currency(reward)
        offsets = [
            pygame.math.Vector2(
                random.uniform(-50, 50),
                random.uniform(-50, 50),
            )
            for _ in SESSION_POWERUPS
        ]
        for offset, name in zip(offsets, SESSION_POWERUPS):
            drop_pos = position + offset
            drop_pos.x = max(60, min(WIDTH - 60, drop_pos.x))
            drop_pos.y = max(60, min(HEIGHT - 60, drop_pos.y))
            self.powerups.append(PowerUp(name, drop_pos))
    def handle_shooting(self, now):
        if self.player is None:
            return
        mouse_pressed = pygame.mouse.get_pressed()
        if not mouse_pressed[0]:
            return
        if now < self.player.next_shot_time:
            return
        target = pygame.math.Vector2(pygame.mouse.get_pos())
        direction = target - self.player.position
        if direction.length_squared() == 0:
            return
        base_direction = direction.normalize()
        shot_count = self.player.shot_count
        bullets_to_add = []
        if shot_count == 1:
            bullets_to_add.append(base_direction)
        else:
            spread_half = (shot_count - 1) / 2
            for index in range(shot_count):
                offset = index - spread_half
                angle = offset * BULLET_SPREAD_ANGLE
                bullets_to_add.append(base_direction.rotate(angle))
        for shot_dir in bullets_to_add:
            self.bullets.append(
                Bullet(
                    self.player.position,
                    shot_dir,
                    self.player.bullet_radius,
                    self.player.bullet_damage,
                    piercing=self.player.piercing_active,
                )
            )
        self.player.next_shot_time = now + int(self.player.cooldown * 1000)
        self.play_sound(self.fire_sound)

    def handle_auto_fire(self, dt):
        if self.player is None or self.auto_fire_level == 0:
            return
        if not self.enemies:
            self.auto_fire_timer = min(
                self.auto_fire_timer + dt,
                self.auto_fire_cooldown,
            )
            return
        self.auto_fire_timer -= dt
        if self.auto_fire_timer > 0:
            return
        sorted_enemies = sorted(
            self.enemies,
            key=lambda enemy: (
                enemy.position - self.player.position
            ).length_squared(),
        )
        shots = min(self.auto_fire_shots, len(sorted_enemies))
        fired = False
        for index in range(shots):
            target = sorted_enemies[index]
            direction = target.position - self.player.position
            if direction.length_squared() == 0:
                continue
            self.bullets.append(
                Bullet(
                    self.player.position,
                    direction,
                    self.player.bullet_radius,
                    self.player.bullet_damage,
                    piercing=self.player.piercing_active,
                )
            )
            fired = True
        if fired:
            self.play_sound(self.fire_sound)
        self.auto_fire_timer = self.auto_fire_cooldown

    def update_enemies(self, dt, now):
        if self.player is None:
            return
        for enemy in list(self.enemies):
            enemy.update(dt, self.player.position)
            projectile = enemy.try_shoot(now, self.player.position)
            if projectile is not None:
                self.enemy_projectiles.append(projectile)
            if enemy.special_shot_interval > 0:
                active_special = (
                    enemy.active_special_projectile is not None
                    and enemy.active_special_projectile in self.enemy_projectiles
                )
                if (
                    not active_special
                    and now >= enemy.next_special_shot_time
                ):
                    direction = self.player.position - enemy.position
                    if direction.length_squared() == 0:
                        direction = pygame.math.Vector2(1, 0)
                    else:
                        direction = direction.normalize()
                    special_projectile = EnemyProjectile(
                        enemy.position,
                        direction * enemy.special_shot_speed,
                        enemy.special_shot_damage,
                        enemy.special_projectile_color,
                        radius=enemy.special_shot_radius,
                        destroyable=True,
                        hit_points=enemy.special_shot_hp,
                        homing=True,
                        owner=enemy,
                        speed=enemy.special_shot_speed,
                    )
                    enemy.active_special_projectile = special_projectile
                    self.enemy_projectiles.append(special_projectile)
                    enemy.next_special_shot_time = now + enemy.special_shot_interval
            if circle_collision(
                self.player.position,
                self.player.radius,
                enemy.position,
                enemy.radius,
            ):
                collision_damage = 2 if enemy.is_boss else 1
                took_damage = self.handle_player_hit(
                    enemy, now, collision_damage
                )
                if took_damage:
                    if enemy.is_boss:
                        offset = enemy.position - self.player.position
                        if offset.length_squared() > 0:
                            offset = offset.normalize() * (
                                enemy.radius + self.player.radius + 12
                            )
                            enemy.position = self.player.position + offset
                    else:
                        if enemy in self.enemies:
                            self.enemies.remove(enemy)
                if self.state == "game_over":
                    break
        if self.state == "game_over":
            return


    def update_bullets(self, dt):
        for bullet in list(self.bullets):
            bullet.update(dt)
            removed = False
            for enemy in list(self.enemies):
                if circle_collision(
                    bullet.position,
                    bullet.radius,
                    enemy.position,
                    enemy.radius,
                ):
                    killed = enemy.take_damage(bullet.damage)
                    self.play_sound(self.hit_sound)
                    if killed:
                        if enemy.coin_value:
                            self.reward_currency(enemy.coin_value)
                        self.enemies.remove(enemy)
                        self.score += enemy.score_value
                        if enemy is self.active_boss:
                            special = getattr(enemy, "active_special_projectile", None)
                            if special and special in self.enemy_projectiles:
                                self.enemy_projectiles.remove(special)
                            enemy.active_special_projectile = None
                            self.active_boss = None
                            self.handle_boss_drop(enemy.position)
                    if not bullet.piercing:
                        removed = True
                    break
            if removed and bullet in self.bullets:
                self.bullets.remove(bullet)
                continue
            for projectile in list(self.enemy_projectiles):
                if circle_collision(
                    bullet.position,
                    bullet.radius,
                    projectile.position,
                    projectile.radius,
                ):
                    remove_bullet = True
                    if projectile.destroyable:
                        projectile.hit_points -= bullet.damage
                        if projectile.hit_points <= 0 and projectile in self.enemy_projectiles:
                            owner = getattr(projectile, "owner", None)
                            if owner and getattr(owner, "active_special_projectile", None) is projectile:
                                owner.active_special_projectile = None
                            projectile.owner = None
                            self.enemy_projectiles.remove(projectile)
                        if bullet.piercing:
                            remove_bullet = False
                    elif bullet.piercing:
                        remove_bullet = False
                    removed = remove_bullet
                    break
            if removed and bullet in self.bullets:
                self.bullets.remove(bullet)
                continue
            if bullet.is_offscreen() and bullet in self.bullets:
                self.bullets.remove(bullet)


    def handle_player_hit(self, source, now, damage=1):
        if self.player is None:
            return False
        if now < self.player.invulnerable_until:
            return False
        self.lives -= damage
        self.player.invulnerable_until = now + INVULNERABILITY_DURATION
        self.player.hit_flash_end = now + HIT_FLASH_DURATION
        self.play_sound(self.damage_sound)
        if self.lives <= 0:
            self.state = "game_over"
            self.game_over_time = now
            self.bullets.clear()
            self.enemy_projectiles.clear()
        return True


    def update_enemy_projectiles(self, dt, now):
        if self.player is None:
            return
        for projectile in list(self.enemy_projectiles):
            owner = getattr(projectile, "owner", None)
            if owner is not None and owner not in self.enemies:
                if getattr(owner, "active_special_projectile", None) is projectile:
                    owner.active_special_projectile = None
                projectile.owner = None
            if getattr(projectile, "homing", False) and self.player is not None:
                direction = self.player.position - projectile.position
                if direction.length_squared() > 0:
                    direction = direction.normalize()
                    projectile.velocity = direction * getattr(projectile, "speed", projectile.velocity.length())
            projectile.update(dt)
            if circle_collision(
                projectile.position,
                projectile.radius,
                self.player.position,
                self.player.radius,
            ):
                took_damage = self.handle_player_hit(
                    projectile, now, projectile.damage
                )
                if projectile.destroyable or took_damage:
                    owner = getattr(projectile, "owner", None)
                    if owner and getattr(owner, "active_special_projectile", None) is projectile:
                        owner.active_special_projectile = None
                    projectile.owner = None
                    if projectile in self.enemy_projectiles:
                        self.enemy_projectiles.remove(projectile)
                continue
            if projectile.destroyable and projectile.hit_points <= 0:
                owner = getattr(projectile, "owner", None)
                if owner and getattr(owner, "active_special_projectile", None) is projectile:
                    owner.active_special_projectile = None
                projectile.owner = None
                if projectile in self.enemy_projectiles:
                    self.enemy_projectiles.remove(projectile)
                continue
            if projectile.is_offscreen():
                owner = getattr(projectile, "owner", None)
                if owner and getattr(owner, "active_special_projectile", None) is projectile:
                    owner.active_special_projectile = None
                projectile.owner = None
                if projectile in self.enemy_projectiles:
                    self.enemy_projectiles.remove(projectile)


    def handle_powerups(self, now):
        if self.player is None:
            return
        if (
            now - self.last_powerup_spawn >= POWERUP_INTERVAL
            and not self.powerups
        ):
            self.spawn_powerup()
            self.last_powerup_spawn = now
        for powerup in list(self.powerups):
            radius = POWERUP_SIZE / 2
            if circle_collision(
                self.player.position,
                self.player.radius,
                powerup.position,
                radius,
            ):
                self.powerups.remove(powerup)
                self.player.apply_powerup(powerup.name, now)
                self.play_sound(self.power_sound)

    def update_floors(self, now):
        if self.state != "playing":
            return
        if not self.enemies and not self.waiting_for_floor:
            self.waiting_for_floor = True
            self.floor_cleared_time = now
            self.reward_currency(self.floor_clear_reward())
        if (
            self.waiting_for_floor
            and now - self.floor_cleared_time >= FLOOR_DELAY
        ):
            self.floor_number += 1
            self.spawn_floor()
            self.waiting_for_floor = False

    def update_gameplay(self, dt):
        if self.player is None:
            return
        keys = pygame.key.get_pressed()
        now = pygame.time.get_ticks()
        self.player.update(dt, keys)
        self.player.update_powerups(now)
        self.handle_shooting(now)
        self.handle_auto_fire(dt)
        self.update_bullets(dt)
        self.update_enemies(dt, now)
        if self.state != "game_over":
            self.update_enemy_projectiles(dt, now)
            self.handle_powerups(now)
            self.update_floors(now)
    def draw_hud(self):
        score_text = self.ui_font.render(f"Score: {self.score}", True, HUD_COLOR)
        hearts_text = self.ui_font.render(f"Hearts: {self.lives}", True, HUD_COLOR)
        floor_text = self.ui_font.render(f"Floor: {self.floor_number}", True, HUD_COLOR)
        coins_text = self.ui_font.render(f"Coins: {self.run_currency}", True, HUD_COLOR)
        bank_text = self.hud_font.render(f"Bank: {self.currency}", True, HUD_COLOR)
        self.screen.blit(score_text, (24, 24))
        self.screen.blit(hearts_text, (24, 60))
        self.screen.blit(floor_text, (24, 96))
        self.screen.blit(coins_text, (24, 132))
        self.screen.blit(bank_text, (28, 168))
        if self.player and self.player.power_timers:
            if self.state == "paused" and self.pause_started_at is not None:
                now = self.pause_started_at
            else:
                now = pygame.time.get_ticks()
            y = 90
            for name, end_time in self.player.power_timers.items():
                remaining = max(0.0, (end_time - now) / 1000)
                label = POWERUP_LABELS.get(name, name.replace("_", " ").title())
                info = self.hud_font.render(
                    f"{label}: {remaining:0.1f}s",
                    True,
                    HUD_COLOR,
                )
                rect = info.get_rect(topright=(WIDTH - 24, y))
                self.screen.blit(info, rect)
                y += 26
        if self.player:
            buffs = []
            fire_boost = self.player.permanent_upgrades.get("fire_rate", 0)
            damage_boost = self.player.permanent_upgrades.get("damage", 0)
            if fire_boost:
                buffs.append(f"Fire +{fire_boost}")
            if damage_boost:
                buffs.append(f"Damage +{damage_boost}")
            if buffs:
                buff_text = self.hud_font.render(
                    "Session buffs: " + " | ".join(buffs),
                    True,
                    HUD_COLOR,
                )
                rect = buff_text.get_rect(bottomleft=(24, HEIGHT - 24))
                self.screen.blit(buff_text, rect)
    def draw_gameplay(self):
        self.screen.fill(BG_COLOR)
        now = pygame.time.get_ticks()
        for powerup in self.powerups:
            powerup.draw(self.screen)
        for projectile in self.enemy_projectiles:
            projectile.draw(self.screen)
        for enemy in self.enemies:
            enemy.draw(self.screen, now)
        for bullet in self.bullets:
            bullet.draw(self.screen)
        if self.player:
            self.player.draw(self.screen, now)
        self.draw_hud()
        if self.waiting_for_floor and not self.active_boss:
            next_floor = self.floor_number + 1
            banner = self.ui_font.render(
                f"Entering Floor {next_floor}",
                True,
                HUD_COLOR,
            )
            banner_rect = banner.get_rect(center=(WIDTH / 2, HEIGHT / 2))
            self.screen.blit(banner, banner_rect)
        if self.floor_number % BOSS_FLOOR_INTERVAL == 0 and self.active_boss:
            boss_text = self.ui_font.render(
                "Boss Floor! Hold the line.",
                True,
                HUD_COLOR,
            )
            rect = boss_text.get_rect(center=(WIDTH / 2, HEIGHT - 72))
            self.screen.blit(boss_text, rect)
        if self.player and self.player.invulnerable_until > now:
            remaining = (self.player.invulnerable_until - now) / 1000
            shield = self.hud_font.render(
                f"Barrier: {remaining:0.1f}s",
                True,
                HUD_COLOR,
            )
            rect = shield.get_rect(topright=(WIDTH - 24, HEIGHT - 48))
            self.screen.blit(shield, rect)
    def draw_menu(self):
        self.screen.fill(BG_COLOR)
        title = self.title_font.render("Tower Rush", True, HUD_COLOR)
        rect = title.get_rect(center=(WIDTH / 2, HEIGHT / 2 - 120))
        self.screen.blit(title, rect)
        prompt = self.ui_font.render(
            "Press Enter to start",
            True,
            HUD_COLOR,
        )
        rect = prompt.get_rect(center=(WIDTH / 2, HEIGHT / 2 - 30))
        self.screen.blit(prompt, rect)
        info = self.hud_font.render(
            "WASD to move  |  Mouse to aim  |  Left click to fire",
            True,
            HUD_COLOR,
        )
        rect = info.get_rect(center=(WIDTH / 2, HEIGHT / 2 + 20))
        self.screen.blit(info, rect)
        workshop = self.hud_font.render(
            "Press U for the upgrade workshop",
            True,
            HUD_COLOR,
        )
        rect = workshop.get_rect(center=(WIDTH / 2, HEIGHT / 2 + 60))
        self.screen.blit(workshop, rect)
        bank = self.hud_font.render(
            f"Total coins: {self.currency}",
            True,
            HUD_COLOR,
        )
        rect = bank.get_rect(center=(WIDTH / 2, HEIGHT / 2 + 100))
        self.screen.blit(bank, rect)
    def draw_pause(self):
        self.draw_gameplay()
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill(PAUSE_OVERLAY)
        self.screen.blit(overlay, (0, 0))
        title = self.title_font.render("Paused", True, HUD_COLOR)
        rect = title.get_rect(center=(WIDTH / 2, HEIGHT / 2 - 40))
        self.screen.blit(title, rect)
        resume = self.ui_font.render("Press ESC to resume", True, HUD_COLOR)
        restart = self.hud_font.render("Press R to restart", True, HUD_COLOR)
        self.screen.blit(resume, resume.get_rect(center=(WIDTH / 2, HEIGHT / 2 + 16)))
        self.screen.blit(restart, restart.get_rect(center=(WIDTH / 2, HEIGHT / 2 + 56)))
    def draw_game_over(self):
        self.screen.fill(BG_COLOR)
        title = self.title_font.render("Run Over", True, HUD_COLOR)
        self.screen.blit(title, title.get_rect(center=(WIDTH / 2, HEIGHT / 2 - 100)))
        score_text = self.ui_font.render(f"Score: {self.score}", True, HUD_COLOR)
        self.screen.blit(score_text, score_text.get_rect(center=(WIDTH / 2, HEIGHT / 2 - 20)))
        floor_text = self.hud_font.render(f"Highest Floor: {self.floor_number}", True, HUD_COLOR)
        self.screen.blit(floor_text, floor_text.get_rect(center=(WIDTH / 2, HEIGHT / 2 + 20)))
        coin_text = self.hud_font.render(f"Coins Earned: {self.run_currency}", True, HUD_COLOR)
        self.screen.blit(coin_text, coin_text.get_rect(center=(WIDTH / 2, HEIGHT / 2 + 50)))
        bank_text = self.hud_font.render(f"Total Coins: {self.currency}", True, HUD_COLOR)
        self.screen.blit(bank_text, bank_text.get_rect(center=(WIDTH / 2, HEIGHT / 2 + 80)))
        prompt = self.hud_font.render(
            "Press Enter to retry, U for workshop, M for menu, Esc to quit",
            True,
            HUD_COLOR,
        )
        self.screen.blit(prompt, prompt.get_rect(center=(WIDTH / 2, HEIGHT / 2 + 120)))
    def draw_meta_shop(self):
        self.screen.fill(BG_COLOR)
        title = self.title_font.render("Upgrade Workshop", True, HUD_COLOR)
        self.screen.blit(title, title.get_rect(center=(WIDTH / 2, 120)))
        bank = self.ui_font.render(f"Available coins: {self.currency}", True, HUD_COLOR)
        self.screen.blit(bank, bank.get_rect(center=(WIDTH / 2, 170)))
        tips = self.hud_font.render("Press 1-6 to purchase, ESC to return", True, HUD_COLOR)
        self.screen.blit(tips, tips.get_rect(center=(WIDTH / 2, 210)))
        start_y = 260
        for index, name in enumerate(META_UPGRADE_ORDER, start=1):
            data = META_UPGRADE_DEFS[name]
            level = self.meta_upgrades[name]
            max_level = data["max_level"]
            cost = self.meta_upgrade_cost(name)
            status = "MAX" if level >= max_level else f"Cost: {cost}"
            label = self.ui_font.render(
                f"{index}. {data['label']} (Lv {level}/{max_level})",
                True,
                HUD_COLOR,
            )
            self.screen.blit(label, (140, start_y))
            info_text = self.hud_font.render(data["description"], True, HUD_COLOR)
            self.screen.blit(info_text, (160, start_y + 34))
            cost_color = (
                (120, 120, 120)
                if status == "MAX"
                else (ACCENT_COLOR if self.currency >= cost else (200, 120, 120))
            )
            cost_text = self.hud_font.render(status, True, cost_color)
            self.screen.blit(cost_text, (WIDTH - 260, start_y))
            start_y += 72


    def play_sound(self, sound):
        if sound is not None:
            sound.play()

    def meta_upgrade_cost(self, name):
        level = self.meta_upgrades[name]
        data = META_UPGRADE_DEFS[name]
        if level >= data["max_level"]:
            return 0
        cost = data["base_cost"] * (data["cost_scale"] ** level)
        return int(round(cost))

    def buy_meta_upgrade(self, name):
        data = META_UPGRADE_DEFS[name]
        level = self.meta_upgrades[name]
        if level >= data["max_level"]:
            return False
        cost = self.meta_upgrade_cost(name)
        if self.currency < cost:
            return False
        self.currency -= cost
        self.meta_upgrades[name] += 1
        self.update_meta_effects()
        self.play_sound(self.power_sound)
        if self.state == "playing":
            self.apply_meta_to_player()
        return True
    def handle_event(self, event):
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type != pygame.KEYDOWN:
            return
        key = event.key
        if key == pygame.K_g:
            self.max_out_meta_upgrades()
            return
        if self.state == "menu":
            if key in (pygame.K_RETURN, pygame.K_SPACE):
                self.reset_game()
                self.state = "playing"
            elif key == pygame.K_u:
                self.state_before_shop = "menu"
                self.state = "meta_shop"
            elif key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()
        elif self.state == "meta_shop":
            if key == pygame.K_ESCAPE:
                if self.state_before_shop != "paused":
                    self.pause_started_at = None
                self.state = self.state_before_shop
            elif pygame.K_1 <= key <= pygame.K_9:
                index = key - pygame.K_1
                if index < len(META_UPGRADE_ORDER):
                    name = META_UPGRADE_ORDER[index]
                    self.buy_meta_upgrade(name)
        elif self.state == "playing":
            if key == pygame.K_ESCAPE:
                self.pause_started_at = pygame.time.get_ticks()
                self.state = "paused"
            elif key == pygame.K_r:
                self.reset_game()
        elif self.state == "paused":
            if key == pygame.K_ESCAPE:
                if self.pause_started_at is not None:
                    resumed = pygame.time.get_ticks()
                    self.extend_powerup_timers(resumed - self.pause_started_at)
                self.pause_started_at = None
                self.state = "playing"
            elif key == pygame.K_r:
                self.reset_game()
                self.state = "playing"
        elif self.state == "game_over":
            if key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_r):
                self.reset_game()
                self.state = "playing"
            elif key == pygame.K_u:
                self.state_before_shop = "game_over"
                self.state = "meta_shop"
            elif key == pygame.K_m:
                self.state = "menu"
            elif key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()
    def run(self):
        while True:
            dt = self.clock.tick(FPS) / 1000.0
            for event in pygame.event.get():
                self.handle_event(event)
            if self.state == "menu":
                self.draw_menu()
            elif self.state == "meta_shop":
                self.draw_meta_shop()
            elif self.state == "playing":
                self.update_gameplay(dt)
                if self.state == "game_over":
                    self.draw_game_over()
                else:
                    self.draw_gameplay()
            elif self.state == "paused":
                self.draw_pause()
            elif self.state == "game_over":
                self.draw_game_over()
            pygame.display.flip()


if __name__ == "__main__":
    TowerRushGame().run()
