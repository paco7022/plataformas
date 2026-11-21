from math import hypot

from combat import ENEMY_SPAWNS, Enemy
from rooms import PICKUPS, ROOMS, Portal


STEP = 1 / 60
WIDTH, HEIGHT = 1280, 720
HALF_WIDTH, HALF_HEIGHT = 13, 21
SEED_ROOMS = tuple(room_id for room_id, items in PICKUPS.items() if any(
    kind == "seed" for kind, _, _ in items
))
ATTACK_REACH = 76


def clamp(value, low, high):
    return max(low, min(value, high))


class Player:
    def __init__(self):
        self.dash_unlocked = False
        self.facing = 1
        self.reset((240, 570))

    def reset(self, spawn):
        self.x, self.y = spawn
        self.vx = self.vy = 0.0
        self.grounded = False
        self.dash_available = True
        self.coyote = self.jump_buffer = self.drop_time = 0.0
        self.dash_frames = 0
        self.dash_cooldown = 0.0
        self.trail = []

    def update(self, platforms, axis=0, jump=False, release=False, down=False, dash=False):
        if axis:
            self.facing = axis
        self.trail = [(x, y, life - STEP) for x, y, life in self.trail if life > STEP]
        self.coyote = 0.11 if self.grounded else max(0, self.coyote - STEP)
        self.jump_buffer = max(0, self.jump_buffer - STEP)
        self.dash_cooldown = max(0, self.dash_cooldown - STEP)
        self.drop_time = max(0, self.drop_time - STEP)
        if self.grounded and not self.dash_frames:
            self.dash_available = True
        if jump:
            if down and self.grounded:
                self.drop_time = 0.22
                self.vy = 80
                self.coyote = self.jump_buffer = 0.0
            else:
                self.jump_buffer = 0.13
        if dash and self.dash_unlocked and self.dash_available and not self.dash_cooldown:
            self.dash_frames = 12
            self.dash_available = False
            self.dash_cooldown = 0.38
        if self.dash_frames:
            self.dash_frames -= 1
            self.vx, self.vy = self.facing * 880, 0
            self.trail.append((self.x, self.y, 0.22))
        else:
            acceleration = (2600 if self.grounded else 1700) * STEP
            self.vx += clamp(axis * 310 - self.vx, -acceleration, acceleration)
            self.vy = min(self.vy + 1500 * STEP, 950)
            if self.jump_buffer and self.coyote:
                self.vy = -650
                self.jump_buffer = self.coyote = 0.0
            if release and self.vy < -180:
                self.vy = -180
        self.move(platforms)

    def move(self, platforms):
        next_x = clamp(self.x + self.vx * STEP, 16, WIDTH - 16)
        for x, y, width, height, *thin in platforms:
            if thin or self.y + HALF_HEIGHT <= y or self.y - HALF_HEIGHT >= y + height:
                continue
            if self.x + HALF_WIDTH <= x < next_x + HALF_WIDTH:
                next_x, self.vx = x - HALF_WIDTH, 0
            if next_x - HALF_WIDTH < x + width <= self.x - HALF_WIDTH:
                next_x, self.vx = x + width + HALF_WIDTH, 0
        self.x = next_x

        next_y = self.y + self.vy * STEP
        grounded = False
        for x, y, width, height, *thin in platforms:
            if self.x + HALF_WIDTH <= x or self.x - HALF_WIDTH >= x + width:
                continue
            if thin and self.drop_time:
                continue
            if self.y + HALF_HEIGHT <= y <= next_y + HALF_HEIGHT:
                next_y = y - HALF_HEIGHT
                grounded = True
            elif not thin and next_y - HALF_HEIGHT < y + height <= self.y - HALF_HEIGHT:
                next_y = y + height + HALF_HEIGHT
        if grounded or next_y != self.y + self.vy * STEP:
            self.vy = 0
        self.y, self.grounded = next_y, grounded


class Game:
    def __init__(self):
        self.player = Player()
        self.max_health = self.health = 4
        self.enemies_by_room = {
            room_id: [Enemy(spawn) for spawn in spawns]
            for room_id, spawns in ENEMY_SPAWNS.items()
        }
        self.collected = set()
        self.seeds = set()
        self.memory_returned = False
        self.visited = set()
        self.shortcut_open = self.secret_found = self.finished = False
        self.map_open = self.paused = False
        self.age = self.message_time = 0.0
        self.message = ""
        self.enter(0, (240, 570))

    @property
    def room(self):
        return ROOMS[self.room_id]

    @property
    def frozen(self):
        return self.map_open or self.paused

    @property
    def enemies(self):
        return self.enemies_by_room.get(self.room_id, ())

    @property
    def guardian(self):
        return self.enemies_by_room[5][0]

    @property
    def pickups(self):
        return [item for item in PICKUPS.get(self.room_id, ())
                if (self.room_id, item) not in self.collected]

    @property
    def objective(self):
        if self.finished:
            return "Misión cumplida · Santuario restaurado"
        missing = [ROOMS[i].name for i in SEED_ROOMS if i not in self.seeds]
        if missing:
            return f"Semillas de luz {len(self.seeds)}/{len(SEED_ROOMS)} · {' / '.join(missing)}"
        if self.guardian.health:
            return "Semillas de luz reunidas · Derrota al guardián del Patio"
        return "Guardián vencido · Activa el sello con E"

    @property
    def side_objective(self):
        if self.memory_returned:
            return "Memoria de la raíz · Entregada (+1 corazón)"
        if self.secret_found:
            return "Memoria de la raíz · Llévala al altar del Refugio"
        return "Memoria de la raíz · Busca en el balcón oeste del Pozo"

    def enter(self, room_id, spawn):
        if room_id == 5 and self.guardian.health:
            self.guardian.reset()
        self.room_id = room_id
        self.visited.add(room_id)
        self.spawn = spawn
        self.place_player()

    def place_player(self):
        self.player.reset(self.spawn)
        self.camera = self.camera_target()
        self.transition = 0.9
        self.portal_cooldown = 0.35
        self.invulnerable = 0.9
        self.hurt_flash = self.attack_cooldown = self.attack_time = 0.0

    def camera_target(self):
        return clamp(self.player.y - 425, 0, self.room.height - HEIGHT)

    def toggle_map(self):
        self.map_open = not self.map_open
        self.paused = False

    def escape(self):
        if self.map_open:
            self.map_open = False
        else:
            self.paused = not self.paused

    def respawn(self):
        if self.room_id == 5 and self.guardian.health:
            self.guardian.reset()
        self.place_player()
        self.notify("Las raíces te devuelven al último acceso seguro.", 3)

    def notify(self, message, duration=4.5):
        self.message, self.message_time = message, duration

    def update(self, attack=False, **controls):
        if self.frozen:
            return
        self.player.update(self.room.platforms, **controls)
        self.age += STEP
        self.transition = max(0, self.transition - STEP * 2)
        self.message_time = max(0, self.message_time - STEP)
        self.portal_cooldown = max(0, self.portal_cooldown - STEP)
        self.invulnerable = max(0, self.invulnerable - STEP)
        self.hurt_flash = max(0, self.hurt_flash - STEP)
        self.attack_cooldown = max(0, self.attack_cooldown - STEP)
        self.attack_time = max(0, self.attack_time - STEP)
        self.camera += (self.camera_target() - self.camera) * STEP * 6
        if self.player.y > self.room.height + 70:
            self.respawn()
            return
        if attack and not self.attack_cooldown:
            self.swing()
        for enemy in self.enemies:
            if enemy.health and enemy.update(STEP, self.player) and not self.invulnerable:
                if self.take_hit(enemy):
                    return
        self.collect_pickups()

    def swing(self):
        self.attack_time, self.attack_cooldown = 0.17, 0.4
        self.attack_facing = self.player.facing
        for enemy in self.enemies:
            distance = (enemy.x - self.player.x) * self.attack_facing
            half_width = enemy.width / 2
            if (enemy.health and -half_width <= distance <= ATTACK_REACH + half_width
                    and abs(self.player.y - enemy.center_y) < enemy.height / 2 + 21):
                enemy.hit()
                if not enemy.health and enemy.guardian:
                    self.notify("GUARDIÁN VENCIDO  ·  Activa el sello con E.", 6)

    def take_hit(self, enemy):
        self.health -= 1
        if not self.health:
            self.health = self.max_health
            self.respawn()
            self.notify("Has caído. Las raíces restauran tu fuerza en el acceso seguro.", 4)
            return True
        self.invulnerable = 0.95
        self.hurt_flash = 0.4
        player = self.player
        player.dash_frames = 0
        player.grounded = False
        player.vx = -380 if player.x < enemy.x else 380
        player.vy = -225
        return False

    def collect_pickups(self):
        for item in self.pickups:
            kind, x, y = item
            if abs(self.player.x - x) > 25 or abs(self.player.y - y) > 29:
                continue
            if kind == "seed":
                self.seeds.add(self.room_id)
                self.notify(f"SEMILLA DE LUZ  ·  {len(self.seeds)}/{len(SEED_ROOMS)} reunidas.", 3)
            elif self.health < self.max_health:
                self.health += 1
                self.notify("ROCÍO VITAL  ·  Recuperaste un corazón.", 3)
            else:
                continue
            self.collected.add((self.room_id, item))

    def portal_requirement(self, portal):
        if portal.locked and not self.player.dash_unlocked:
            return "Despierta el impulso en el altar antes de continuar."
        if portal.target == 5 and len(self.seeds) < len(SEED_ROOMS):
            return f"El arco pide las semillas de luz  ·  {len(self.seeds)}/{len(SEED_ROOMS)}"
        return ""

    def seal_requirement(self):
        if len(self.seeds) < len(SEED_ROOMS):
            return "El sello necesita las tres semillas de luz."
        if self.guardian.health:
            return "Derrota al guardián para activar el sello."
        return ""

    def nearby(self):
        foot_x, foot_y = self.player.x, self.player.y + HALF_HEIGHT
        for portal in self.room.portals:
            if hypot(foot_x - portal.x, foot_y - portal.y) < 75:
                return portal
        for kind, x, y in self.room.objects:
            if hypot(foot_x - x, foot_y - y) < 80:
                return kind
        return None

    def prompt(self):
        target = self.nearby()
        if isinstance(target, Portal):
            return self.portal_requirement(target) or f"E  ·  {ROOMS[target.target].name}"
        return {
            "checkpoint": "E  ·  Entregar la memoria de la raíz"
                          if self.secret_found and not self.memory_returned
                          else "E  ·  Descansar en el refugio",
            "shrine": "E  ·  Descansar antes del combate",
            "dash": "El impulso te acompaña  ·  Shift" if self.player.dash_unlocked
                    else "E  ·  Despertar el impulso",
            "shortcut": "E  ·  Volver al Refugio" if self.shortcut_open
                        else "E  ·  Abrir el atajo al Refugio",
            "shortcut_return": "E  ·  Atajo al Puente Roto" if self.shortcut_open
                               else "Un camino dormido. Se abre desde el otro lado.",
            "secret": "La memoria está contigo" if self.secret_found
                      else "E  ·  Recoger la memoria de la raíz",
            "finish": self.seal_requirement() or (
                "El sello del santuario está restaurado" if self.finished else "E  ·  Activar el sello"
            ),
        }.get(target, "")

    def interact(self):
        if self.frozen or self.portal_cooldown:
            return
        target = self.nearby()
        if isinstance(target, Portal):
            requirement = self.portal_requirement(target)
            if requirement:
                self.notify(requirement)
            else:
                self.enter(target.target, target.spawn)
        elif target == "checkpoint":
            self.spawn = (240, 570)
            if self.secret_found and not self.memory_returned:
                self.memory_returned = True
                self.max_health += 1
                self.notify("MISIÓN CUMPLIDA  ·  Memoria de la raíz devuelta. +1 corazón máximo.", 6)
            else:
                self.notify("Refugio activado. Las raíces restauran tu salud.")
            self.health = self.max_health
        elif target == "shrine":
            self.spawn = (245, 570)
            self.health = self.max_health
            self.notify("Altar activado. Salud restaurada.")
        elif target == "dash" and not self.player.dash_unlocked:
            self.player.dash_unlocked = self.player.dash_available = True
            self.notify("IMPULSO DESPERTADO  ·  Pulsa Shift. Se recarga al tocar el suelo.", 7)
        elif target == "shortcut":
            if self.shortcut_open:
                self.enter(0, (905, 570))
            else:
                self.shortcut_open = True
                self.notify("ATAJO ABIERTO  ·  El puente y el refugio vuelven a estar unidos.", 6)
        elif target == "shortcut_return" and self.shortcut_open:
            self.enter(4, (925, 570))
        elif target == "secret" and not self.secret_found:
            self.secret_found = True
            self.notify("MEMORIA DE LA RAÍZ  ·  Devuélvela al altar del Refugio.", 6)
        elif target == "finish":
            requirement = self.seal_requirement()
            if requirement:
                self.notify(requirement)
            elif not self.finished:
                self.finished = True
                self.notify("CAPÍTULO COMPLETADO  ·  Las raíces del santuario vuelven a brillar.", 8)
