# Santuario de las Raíces en Pygame

Esta versión reproduce las seis salas del primer mundo de Godot. Usa el fondo de
`assets/sanctuary.png` y dibuja las plataformas, los portales y al viajero en Pygame.

## Jugar en Windows

Abre **Instalar requisitos Pygame.cmd** desde la carpeta principal para instalar
Python 3.12 y Pygame 2.6.1 en el entorno local `pygame_version/.venv`.
Después abre **Jugar Pygame.cmd**. El lanzador usa ese entorno explícitamente,
por lo que no depende de la versión predeterminada del comando `python`.

Para instalar manualmente desde PowerShell:

```powershell
py -3.12 -m venv pygame_version/.venv
& './pygame_version/.venv/Scripts/python.exe' -m pip install -r pygame_version/requirements.txt
& './pygame_version/.venv/Scripts/python.exe' pygame_version/main.py
```

Si faltan paquetes, vuelve a ejecutar el instalador. Requiere Internet durante
la instalación; el juego funciona sin conexión.

| Acción | Teclas |
| --- | --- |
| Moverse | A / D o ← / → |
| Saltar | W, ↑ o Espacio. Mantén la tecla para saltar más alto |
| Bajar de una plataforma delgada | S o ↓ + saltar |
| Usar el impulso después de desbloquearlo | Shift |
| Atacar hacia donde mira el viajero | F |
| Interactuar con un objeto o atravesar un portal | E |
| Ver el mapa y el progreso de las misiones | Tab o clic en Cartografía |
| Pausar o cerrar el mapa | Esc |
| Volver al último acceso seguro | R |

## Misiones del primer capítulo

- **Semillas de luz.** Recoge una semilla en La Galería, El Pozo y Puente Roto.
  Las tres abren el paso al Patio. Derrota al Guardián de las Raíces y pulsa
  E ante el sello para completar el capítulo.
- **Memoria de la raíz.** Al desbloquear el impulso puedes alcanzar el balcón
  oeste de El Pozo. Lleva la memoria al altar de El Refugio para sumar un
  corazón permanente durante la partida.

Las semillas y el rocío vital se recogen al tocarlos. El rocío recupera un
corazón si te falta salud. Puedes descansar para recuperarte en El Refugio o
en el altar del Patio. Si el guardián marca el suelo, sal de la zona o salta,
y ataca mientras se recupera. Al quedarte sin corazones, reapareces con salud
completa en el último acceso seguro y el guardián recupera su salud si seguía vivo.
Si abandonas el combate o usas R, el guardián también recupera su salud.

Los objetos recogidos, las misiones y los desbloqueos se conservan durante
la sesión.
