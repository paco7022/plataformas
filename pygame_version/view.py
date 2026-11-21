from functools import lru_cache
from math import pi, sin
from pathlib import Path
import sys

import pygame as pg

from game import ATTACK_REACH, HEIGHT, WIDTH
from rooms import ROOMS


INK, MUTED, GOLD, TEAL = "#e1e9da", "#8baaa5", "#d5b97b", "#92d7be"
MAP_BUTTON = pg.Rect(1060, 30, 176, 40)
RESOURCE_ROOT = Path(sys._MEIPASS) if getattr(sys, "frozen", False) else Path(__file__).resolve().parents[1]
BACKGROUND = RESOURCE_ROOT / "assets" / "sanctuary.png"


@lru_cache(maxsize=20)
def font(size, serif):
    families = ("georgia", "timesnewroman") if serif else ("segoeui", "arial")
    return pg.font.SysFont(families, size)


class View:
    def __init__(self, screen):
        self.screen = screen
        self.overlay = pg.Surface(screen.get_size(), pg.SRCALPHA)
        image = pg.image.load(str(BACKGROUND)).convert()
        image = pg.transform.smoothscale(image, (1312, 920))
        self.backgrounds = []
        for room in ROOMS:
            background = image.copy()
            background.fill(room.tint, special_flags=pg.BLEND_RGB_MULT)
            self.backgrounds.append(background)
        self.shade = pg.Surface(screen.get_size(), pg.SRCALPHA)
        self.shade.fill((4, 9, 14, 54))
        for i in range(8):
            pg.draw.rect(self.shade, (3, 7, 10, 160 - 13 * i), (0, 18 * i, WIDTH, 18))
            pg.draw.rect(self.shade, (3, 7, 10, 240 - 23 * i),
                         (0, HEIGHT - 10 * (i + 1), WIDTH, 10))

    def text(self, value, x, y, size=16, color=INK, serif=False, center=False):
        label = font(size, serif).render(value, True, color)
        if center:
            x -= label.get_width() // 2
        self.screen.blit(label, (x, y))

    def panel(self, rect, fill="#101f28", border="#426760"):
        pg.draw.rect(self.screen, fill, rect, border_radius=4)
        pg.draw.rect(self.screen, border, rect, 1, border_radius=4)

    def veil(self, color):
        self.overlay.fill(color)
        self.screen.blit(self.overlay, (0, 0))

    def draw(self, game):
        self.screen.blit(self.backgrounds[game.room_id], (-16, round(-135 - game.camera * 0.12)))
        self.screen.blit(self.shade, (0, 0))
        camera = round(game.camera)
        for x, y, width, height, *thin in game.room.platforms:
            self.platform(x, y - camera, width, height, bool(thin))
        for portal in game.room.portals:
            sealed = bool(game.portal_requirement(portal))
            self.arch(portal.x, portal.y - camera, GOLD if sealed else TEAL, sealed, game.age)
        for kind, x, y in game.room.objects:
            self.object(game, kind, x, y - camera)
        for kind, x, y in game.pickups:
            self.pickup(kind, x, y - camera, game.age)
        for enemy in game.enemies:
            if enemy.health:
                self.enemy(enemy, camera, game.age)
        self.overlay.fill((0, 0, 0, 0))
        for i in range(48):
            x = (i * 179.7 + sin(game.age * 0.23 + i) * 24) % WIDTH
            y = (i * 67.3 - game.age * (6 + i % 5)) % HEIGHT
            alpha = round(55 + 28 * sin(game.age + i))
            pg.draw.circle(self.overlay, (158, 242, 212, alpha), (x, y), 1 + (i % 3 == 0))
        for x, y, life in game.player.trail:
            pg.draw.circle(self.overlay, (122, 247, 214, round(life * 380)), (x, y - camera), 15)
        self.screen.blit(self.overlay, (0, 0))
        if int(game.hurt_flash * 16) % 2 == 0:
            self.traveller(game.player, camera, game.age)
        if game.attack_time:
            self.swing(game, camera)
        if game.transition:
            self.veil((3, 6, 10, round(game.transition * 150)))
        self.hud(game)
        if game.map_open:
            self.map(game)
        elif game.paused:
            self.veil((3, 8, 12, 232))
            self.text("Un momento de quietud", 640, 268, 40, serif=True, center=True)
            self.text("Esc para volver al santuario", 640, 340, 17, GOLD, center=True)
            self.text("Tu progreso se conserva durante esta sesión.", 640, 387, 14, MUTED, center=True)
        self.panel(MAP_BUTTON)
        self.text("TAB   Cartografía", MAP_BUTTON.centerx, 39, 15, center=True)

    def platform(self, x, y, width, height, thin):
        pg.draw.rect(self.screen, "#15292e" if thin else "#101e27", (x, y, width, height))
        pg.draw.rect(self.screen, "#35504c", (x, y + 5, width, 9))
        pg.draw.line(self.screen, "#89bda0", (x, y), (x + width - 1, y), 3)
        pg.draw.line(self.screen, "#497e70", (x, y + 3), (x + width - 1, y + 3), 3)
        for blade in range(x + 12, x + width - 8, 21):
            tip = (blade - 3, y - 4 - (blade * 7) % 9)
            pg.draw.line(self.screen, "#528e78", (blade, y), tip)
            if blade % 3 == 0:
                pg.draw.circle(self.screen, "#a7d4ae", tip, 2)
        for root in range(x + 24, x + width, 55):
            depth = 18 if thin else 34 + root % 37
            pg.draw.line(self.screen, "#294044", (root, y + 14), (root - 4, y + depth))
        if not thin:
            for fern in range(x + 40, x + width - 20, 150):
                for side in (-1, 1):
                    pg.draw.line(self.screen, "#34645a", (fern, y), (fern + 26 * side, y - 30), 2)
                    for step in range(1, 5):
                        a, b = fern + 5 * step * side, y - 6 * step
                        pg.draw.line(self.screen, "#427767", (a, b), (a + 10 * side, b - 2), 2)
                        pg.draw.line(self.screen, "#427767", (a, b), (a - 3 * side, b - 9), 2)

    def arch(self, x, y, color, sealed, age):
        for side in (-1, 1):
            pillar = x + side * 35
            pg.draw.rect(self.screen, "#263b40", (pillar - 8, y - 83, 16, 83))
            pg.draw.line(self.screen, color, (x + side * 28, y - 82), (x + side * 28, y - 2))
        pg.draw.arc(self.screen, "#3b5555", (x - 43, y - 126, 86, 86), 0, pi, 14)
        pg.draw.arc(self.screen, color, (x - 35, y - 118, 70, 70), 0, pi, 2)
        if sealed:
            for bar in range(x - 22, x + 23, 11):
                pg.draw.line(self.screen, "#796d51", (bar, y - 95), (bar, y), 3)
        else:
            pg.draw.circle(self.screen, color, (x, y - 51), round(4 + sin(age * 2)))

    def object(self, game, kind, x, y):
        if kind.startswith("shortcut"):
            self.arch(x, y, GOLD, not game.shortcut_open, game.age)
            if kind == "shortcut" and not game.shortcut_open:
                pg.draw.line(self.screen, GOLD, (x, y - 18), (x + 16, y - 45), 4)
        elif kind == "finish":
            pg.draw.rect(self.screen, "#182b32", (x - 65, y - 205, 130, 205))
            pg.draw.circle(self.screen, "#182b32", (x, y - 205), 65, draw_bottom_left=False,
                           draw_bottom_right=False, draw_top_left=True, draw_top_right=True)
            pg.draw.arc(self.screen, "#77775c", (x - 65, y - 270, 130, 130), 0, pi, 12)
            for side in (-1, 1):
                pg.draw.line(self.screen, "#77775c", (x + side * 59, y), (x + side * 59, y - 205), 12)
            color = TEAL if game.finished else GOLD
            pg.draw.circle(self.screen, color, (x, y - 113), 34, 3 if game.finished else 2)
            pg.draw.line(self.screen, color, (x, y - 147), (x, y - 79), 2)
            pg.draw.line(self.screen, color, (x - 24, y - 113), (x + 24, y - 113), 2)
        else:
            pg.draw.rect(self.screen, "#53675e", (x - 34, y - 12, 68, 12))
            if kind in ("checkpoint", "shrine"):
                for side in (-1, 1):
                    pg.draw.line(self.screen, "#95a58e", (x + side * 25, y - 12),
                                 (x + side * 25, y - 30), 4)
                pg.draw.circle(self.screen, GOLD if kind == "checkpoint" else TEAL, (x, y - 45), 5)
                return
            pg.draw.rect(self.screen, "#829486", (x - 22, y - 27, 44, 15))
            obtained = game.player.dash_unlocked if kind == "dash" else game.secret_found
            if not obtained:
                gem = y - 65 + round(sin(game.age * 2) * 6)
                points = ((x, gem - 17), (x + 10, gem), (x, gem + 17), (x - 10, gem))
                pg.draw.polygon(self.screen, TEAL if kind == "dash" else GOLD, points)
                pg.draw.arc(self.screen, "#789c84", (x - 29, gem - 29, 58, 58),
                            game.age, game.age + pi * 1.5)

    def pickup(self, kind, x, y, age):
        y += round(sin(age * 3 + x) * 4)
        if kind == "seed":
            pg.draw.circle(self.screen, "#8a7144", (x, y), 15, 1)
            pg.draw.polygon(self.screen, "#f3d489", ((x, y - 11), (x + 7, y + 1),
                            (x, y + 9), (x - 7, y + 1)))
            pg.draw.line(self.screen, "#fff0c5", (x, y - 6), (x, y + 3), 2)
        else:
            pg.draw.circle(self.screen, "#284a49", (x, y), 13, 1)
            pg.draw.polygon(self.screen, TEAL, ((x, y - 10), (x + 7, y + 2),
                            (x + 4, y + 7), (x - 4, y + 7), (x - 7, y + 2)))
            pg.draw.circle(self.screen, "#ebfff5", (x - 2, y + 1), 2)

    def enemy(self, enemy, camera, age):
        x, floor = round(enemy.x), enemy.spawn.floor - camera
        if enemy.guardian:
            if enemy.windup:
                left, right = map(round, enemy.strike_bounds)
                pg.draw.rect(self.screen, "#653529", (left, floor - 68, right - left, 68), 1)
                pg.draw.line(self.screen, "#f59b69", (left, floor - 2), (right, floor - 2), 4)
                for mark in range(left + 8, right - 3, 14):
                    pg.draw.line(self.screen, "#b76248", (mark, floor - 4), (mark + 4, floor - 12), 2)
            elif enemy.recovery > 0.57:
                left, right = map(round, enemy.strike_bounds)
                pg.draw.arc(self.screen, "#f8b775", (left, floor - 66, right - left, 118), 0, pi, 5)
            armor = "#e3bd95" if enemy.flash else "#53615b"
            core = "#ec936e" if enemy.windup else "#e0bc79"
            for side in (-1, 1):
                pg.draw.line(self.screen, armor, (x + side * 17, floor - 34),
                             (x + side * 26, floor - 2), 11)
            pg.draw.polygon(self.screen, armor, ((x - 34, floor - 67), (x - 20, floor - 87),
                            (x + 20, floor - 87), (x + 34, floor - 67), (x + 23, floor - 25),
                            (x - 23, floor - 25)))
            pg.draw.rect(self.screen, "#223037", (x - 19, floor - 76, 38, 22), border_radius=5)
            eye = x + enemy.facing * 6
            pg.draw.line(self.screen, core, (eye - 8, floor - 64), (eye + 8, floor - 64), 4)
            pg.draw.circle(self.screen, core, (x, floor - 42), 6)
        else:
            body = "#f0bf9c" if enemy.flash else "#81534e"
            pg.draw.ellipse(self.screen, body, (x - 20, floor - 27, 40, 24))
            for i, offset in enumerate((-14, -5, 6, 15)):
                stride = round(sin(age * 16 + i * 2) * 4)
                pg.draw.line(self.screen, "#a07661", (x + offset, floor - 10),
                             (x + offset + stride, floor - 2), 3)
            pg.draw.circle(self.screen, "#f4b176", (x + enemy.facing * 12, floor - 16), 3)
            if enemy.health < enemy.max_health:
                pg.draw.line(self.screen, "#e0bc79", (x - 7, floor - 33), (x + 7, floor - 33), 2)

    def swing(self, game, camera):
        x, y = round(game.player.x), round(game.player.y) - camera
        angle = 0 if game.attack_facing > 0 else pi
        pg.draw.arc(self.screen, "#f7de9c", (x - ATTACK_REACH, y - 29, ATTACK_REACH * 2, 58),
                    angle - 0.87, angle + 0.87, 4)

    def traveller(self, player, camera, age):
        x, y = round(player.x), round(player.y - camera)
        bob = round(sin(age * 14) * min(abs(player.vx) / 310, 1) * 2)
        pg.draw.polygon(self.screen, "#479f9d", ((x - 11, y - 4), (x + 9, y - 4),
                        (x + 17, y + 18 + bob), (x + 1, y + 14), (x - 15, y + 20 + bob)))
        for side in (-1, 1):
            pg.draw.line(self.screen, "#162d39", (x + side * 6, y + 13), (x + side * 8, y + 21), 5)
        pg.draw.rect(self.screen, "#e4ecd9", (x - 12, y - 23 + bob, 24, 24), border_radius=8)
        for eye in (-4, 5):
            offset = x + eye + player.facing * 2
            pg.draw.line(self.screen, "#18313b", (offset, y - 15 + bob), (offset, y - 9 + bob), 3)
        pg.draw.line(self.screen, "#e3ba79", (x - 11, y + 1), (x + 10, y + 1), 4)
        tail = x - player.facing * (23 + sin(age * 10) * 4)
        pg.draw.line(self.screen, "#d3a969", (x - player.facing * 8, y + 2), (tail, y + 7), 4)

    def hud(self, game):
        pg.draw.circle(self.screen, GOLD, (51, 45), 14, 1)
        pg.draw.line(self.screen, GOLD, (51, 33), (51, 57))
        pg.draw.line(self.screen, GOLD, (44, 40), (58, 50))
        self.text("S A N T U A R I O   D E   L A S   R A Í C E S", 78, 26, 14)
        self.text("CAPÍTULO I    /    EL DESPERTAR", 78, 48, 11, MUTED)
        self.text(game.room.name, 40, 72, 32, serif=True)
        self.text(game.room.subtitle, 42, 115, 15, MUTED)
        pg.draw.line(self.screen, GOLD, (42, 149), (94, 149))
        self.text("A D / ← →   Mover", 40, 659, 14, MUTED)
        self.text("W / ↑ / Espacio   Saltar", 210, 659, 14, MUTED)
        self.text("E   Interactuar", 420, 659, 14, MUTED)
        unlocked = game.player.dash_unlocked
        self.text("Shift   Impulso" if unlocked else "Shift   Impulso por descubrir",
                  562, 659, 14, TEAL if unlocked else MUTED)
        self.text("F   Atacar", 778, 659, 14, GOLD)
        self.text("R   Volver al acceso seguro     ·     Esc   Pausa", 40, 687, 12, MUTED)
        self.text(game.objective, 665, 682, 13, TEAL if game.finished else GOLD, center=True)
        self.text(f"{len(game.visited):02} / {len(ROOMS):02}   SALAS", 1024, 659, 14, GOLD)
        self.text("CAPÍTULO COMPLETADO" if game.finished else "CAPÍTULO I", 1024, 687, 11, MUTED)
        for i in range(game.max_health):
            x = 770 + i * 24
            color = "#ea987c" if i < game.health else "#485052"
            pg.draw.circle(self.screen, color, (x - 4, 43), 5)
            pg.draw.circle(self.screen, color, (x + 4, 43), 5)
            pg.draw.polygon(self.screen, color, ((x - 9, 44), (x + 9, 44), (x, 54)))
        if unlocked:
            color = TEAL if game.player.dash_available else "#314e4c"
            pg.draw.circle(self.screen, color, (1018, 50), 5)
            self.text("IMPULSO", 940, 41, 12, TEAL)
        prompt = game.prompt()
        if prompt:
            width = font(16, False).size(prompt)[0] + 40
            self.panel((640 - width // 2, 590, width, 39))
            self.text(prompt, 640, 598, center=True)
        elif game.age < 15 or game.room_id != 0:
            self.text(game.room.hint, 640, 619, 14, INK, center=True)
        if game.message_time:
            self.panel((170, 174, 940, 56), border="#72816a")
            self.text(game.message, 640, 191, color=GOLD, center=True)
        guardian = game.guardian
        if game.room_id == 5 and guardian.health and abs(game.player.x - guardian.x) < 295:
            self.text("GUARDIÁN DE LAS RAÍCES", 640, 242, 12, GOLD, center=True)
            for i in range(guardian.max_health):
                fill = "#ab6651" if i < guardian.health else "#213137"
                pg.draw.rect(self.screen, fill, (515 + 51 * i, 265, 45, 7), border_radius=2)

    def map(self, game):
        self.veil((5, 10, 13, 248))
        self.text("C A R T O G R A F Í A", 85, 74, 14, GOLD)
        self.text("Santuario de las Raíces", 85, 102, 38, serif=True)
        self.text("Seis lugares unidos por una misma raíz.", 85, 154, 16, MUTED)
        positions = ((110, 385), (315, 385), (520, 385), (520, 245), (725, 245), (930, 245))
        pg.draw.lines(self.screen, "#385b58", False, [(x + 85, y + 37) for x, y in positions], 2)
        shortcut_color = GOLD if game.shortcut_open else "#46665e"
        pg.draw.lines(self.screen, shortcut_color, False, ((810, 320), (810, 530), (195, 530), (195, 460)), 2)
        self.text("ATAJO ABIERTO" if game.shortcut_open else "UN CAMINO POR DESPERTAR",
                  402, 540, 12, shortcut_color)
        for i, (x, y) in enumerate(positions):
            current, visited = i == game.room_id, i in game.visited
            self.panel((x, y, 170, 75), "#213d3d" if current else "#11262e",
                       TEAL if current else "#46665e" if visited else "#243b40")
            self.text(f"{i + 1:02}", x + 13, y + 10, 12, GOLD if visited else MUTED)
            self.text(ROOMS[i].name if visited else "Territorio inexplorado",
                      x + 13, y + 34, 14, INK if visited else MUTED)
            if current:
                pg.draw.circle(self.screen, TEAL, (x + 151, y + 20), 4)
        dash = "despertado" if game.player.dash_unlocked else "por descubrir"
        self.text(game.objective, 85, 583, 16, GOLD)
        self.text(game.side_objective, 85, 613, 16, TEAL)
        self.text(f"Impulso: {dash}", 950, 613, 15, TEAL)
        self.text("Tab / Esc  ·  Volver al mundo", 85, 666, 15, MUTED)
