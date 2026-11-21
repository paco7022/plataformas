import sys

import pygame as pg

from game import Game, HEIGHT, STEP, WIDTH
from view import MAP_BUTTON, View


LEFT = {pg.K_a, pg.K_LEFT}
RIGHT = {pg.K_d, pg.K_RIGHT}
JUMP = {pg.K_w, pg.K_UP, pg.K_SPACE}
DOWN = {pg.K_s, pg.K_DOWN}
DASH = {pg.K_LSHIFT, pg.K_RSHIFT}


class Controls:
    def __init__(self):
        self.held = set()
        self.edges = {}

    def clear_edges(self):
        self.edges.clear()

    def handle(self, event, game):
        if event.type == pg.WINDOWFOCUSLOST:
            self.held.clear()
            self.clear_edges()
            game.map_open = False
            game.paused = True
        elif event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            if MAP_BUTTON.collidepoint(event.pos):
                game.toggle_map()
                self.clear_edges()
        elif event.type == pg.KEYUP:
            self.held.discard(event.key)
            if event.key in JUMP and not self.held & JUMP:
                self.edges["release"] = True
        elif event.type == pg.KEYDOWN and event.key not in self.held:
            key = event.key
            if key == pg.K_TAB:
                game.toggle_map()
                self.clear_edges()
            elif key == pg.K_ESCAPE:
                game.escape()
                self.clear_edges()
            elif not game.frozen:
                if key == pg.K_e:
                    game.interact()
                elif key == pg.K_r:
                    game.respawn()
                    self.clear_edges()
                elif key in JUMP and not self.held & JUMP:
                    self.edges["jump"] = True
                elif key in DASH and not self.held & DASH:
                    self.edges["dash"] = True
                elif key == pg.K_f:
                    self.edges["attack"] = True
            self.held.add(key)

    def update(self, game):
        axis = bool(self.held & RIGHT) - bool(self.held & LEFT)
        game.update(axis=axis, down=bool(self.held & DOWN), **self.edges)
        self.clear_edges()


def main(frame_limit=None):
    pg.display.init()
    pg.font.init()
    try:
        screen = pg.display.set_mode((WIDTH, HEIGHT), pg.SCALED)
        pg.display.set_caption("Santuario de las Raíces — Pygame")
        view = View(screen)
        game, controls = Game(), Controls()
        clock = pg.time.Clock()
        accumulator = 0.0
        while True:
            accumulator += min(clock.tick(60) / 1000, 0.1)
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    return
                controls.handle(event, game)
            while accumulator >= STEP:
                controls.update(game)
                accumulator -= STEP
            view.draw(game)
            pg.display.flip()
            if frame_limit is not None:
                frame_limit -= 1
                if frame_limit <= 0:
                    return
    finally:
        pg.quit()


if __name__ == "__main__":
    main(frame_limit=60 if "--smoke-test" in sys.argv else None)
