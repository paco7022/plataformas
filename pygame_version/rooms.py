"""Coordinates from scripts/rooms.gd, in world pixels."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Portal:
    x: int
    y: int
    target: int
    spawn: tuple[int, int]
    locked: bool = False


@dataclass(frozen=True)
class Room:
    name: str
    subtitle: str
    height: int
    tint: tuple[int, int, int]
    platforms: tuple[tuple[int, ...], ...]
    portals: tuple[Portal, ...]
    objects: tuple[tuple[str, int, int], ...]
    hint: str


# Each seed belongs to one room. Dew is collected only when it can restore health.
PICKUPS = {
    1: (("seed", 598, 578), ("dew", 1120, 578)),
    2: (("seed", 950, 328),),
    4: (("seed", 1060, 578), ("dew", 965, 578)),
    5: (("dew", 386, 578),),
}


ROOMS = (
    Room(
        "El Refugio", "Donde las raíces aún recuerdan", 720, (224, 255, 245),
        ((0, 600, 1280, 160), (450, 492, 190, 22, 1), (700, 420, 150, 22, 1)),
        (Portal(1210, 600, 1, (110, 570)),),
        (("checkpoint", 240, 600), ("shortcut_return", 980, 600)),
        "Descansa en el refugio y sigue las luces hacia el este.",
    ),
    Room(
        "La Galería", "Un sendero suspendido en el silencio", 720, (194, 232, 255),
        ((0, 600, 300, 160), (450, 600, 300, 160), (930, 600, 350, 160),
         (330, 505, 100, 22, 1), (770, 485, 120, 22, 1)),
        (Portal(65, 600, 0, (1120, 570)), Portal(1210, 600, 2, (140, 1010))),
        (),
        "Mantén el salto para llegar más alto. Abajo + salto atraviesa las plataformas delgadas.",
    ),
    Room(
        "El Pozo", "Lo que duerme arriba espera tu regreso", 1120, (186, 255, 232),
        ((0, 1040, 1280, 120), (250, 925, 180, 22, 1), (470, 810, 180, 22, 1),
         (250, 695, 180, 22, 1), (470, 580, 180, 22, 1), (690, 465, 220, 22, 1),
         (640, 350, 640, 32, 1), (0, 350, 270, 32, 1)),
        (Portal(65, 1040, 1, (1120, 570)), Portal(1210, 350, 3, (120, 570))),
        (("secret", 120, 350),),
        "Asciende por las terrazas. La luz del balcón oeste está fuera del alcance de un salto.",
    ),
    Room(
        "Cámara del Impulso", "El viento también echa raíces", 720, (242, 237, 199),
        ((0, 600, 1280, 160), (340, 485, 150, 22, 1), (790, 485, 150, 22, 1)),
        (Portal(65, 600, 2, (1110, 320)), Portal(1210, 600, 4, (120, 570), True)),
        (("dash", 640, 600),),
        "Una chispa antigua permanece en el altar. Acércate y pulsa E.",
    ),
    Room(
        "Puente Roto", "Confía en el impulso", 720, (179, 217, 255),
        ((0, 600, 430, 160), (800, 600, 480, 160)),
        (Portal(65, 600, 3, (1110, 570)), Portal(1210, 600, 5, (120, 570))),
        (("shortcut", 1000, 600),),
        "Toma carrera, salta desde el borde y pulsa Shift en el aire.",
    ),
    Room(
        "Patio del Guardián", "El santuario contiene la respiración", 720, (255, 222, 184),
        ((0, 600, 1280, 160), (320, 475, 170, 22, 1), (760, 475, 170, 22, 1)),
        (Portal(65, 600, 4, (1120, 570)),),
        (("shrine", 245, 600), ("finish", 1110, 600)),
        "Aléjate o salta cuando el guardián marque el suelo. Ataca con F mientras se recupera.",
    ),
)
