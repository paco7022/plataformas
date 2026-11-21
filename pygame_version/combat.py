from dataclasses import dataclass


@dataclass(frozen=True)
class EnemySpawn:
    x: int
    floor: int
    left: int
    right: int
    guardian: bool = False


# Patrol limits leave room to land and turn near the platform edges.
ENEMY_SPAWNS = {
    1: (EnemySpawn(632, 600, 550, 710), EnemySpawn(1060, 600, 1010, 1125)),
    2: (EnemySpawn(1040, 350, 1005, 1080),),
    4: (EnemySpawn(1095, 600, 1040, 1150),),
    5: (EnemySpawn(785, 600, 440, 1015, guardian=True),),
}


class Enemy:
    def __init__(self, spawn):
        self.spawn = spawn
        self.guardian = spawn.guardian
        self.width, self.height = (68, 90) if self.guardian else (40, 28)
        self.max_health = 5 if self.guardian else 2
        self.reset()

    def reset(self):
        self.x = self.spawn.x
        self.health = self.max_health
        self.facing = -1
        self.windup = self.recovery = self.flash = 0.0

    @property
    def center_y(self):
        return self.spawn.floor - self.height / 2

    @property
    def strike_bounds(self):
        edge = self.x + self.facing * 146
        return min(self.x, edge), max(self.x, edge)

    def hit(self):
        self.health -= 1
        self.flash = 0.16

    def update(self, step, player):
        """Return whether this frame's enemy attack touches the player."""
        self.flash = max(0, self.flash - step)
        if self.guardian:
            return self.update_guardian(step, player)
        self.x += self.facing * 77 * step
        if self.x <= self.spawn.left or self.x >= self.spawn.right:
            self.x = max(self.spawn.left, min(self.x, self.spawn.right))
            self.facing *= -1
        return (
            abs(player.x - self.x) < self.width / 2 + 12
            and abs(player.y - self.center_y) < self.height / 2 + 19
        )

    def update_guardian(self, step, player):
        floor = self.spawn.floor
        if self.windup:
            self.windup = max(0, self.windup - step)
            if not self.windup:
                self.recovery = 0.75
                left, right = self.strike_bounds
                return left - 10 < player.x < right + 10 and player.y + 18 > floor - 68
            return False
        if self.recovery:
            self.recovery = max(0, self.recovery - step)
            return False
        distance = player.x - self.x
        if abs(distance) > 275:
            return False
        if abs(distance) > 6:
            self.facing = 1 if distance > 0 else -1
        if abs(distance) < 115 and player.y + 18 > floor - 100:
            self.windup = 0.62
        elif abs(distance) > 48:
            self.x = max(self.spawn.left, min(self.x + self.facing * 105 * step, self.spawn.right))
        return False
