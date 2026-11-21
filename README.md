# Santuario de las Raíces

Primer mundo jugable de un metroidvania 2D original, con versiones en Pygame y Godot 4.

## Descargar y jugar el ejecutable

Descarga [SantuarioDeLasRaices.exe](https://github.com/paco7022/plataformas/raw/refs/heads/main/releases/SantuarioDeLasRaices.exe) y ábrelo con doble clic en Windows de 64 bits. Incluye Python, Pygame y el fondo; no necesita instalar dependencias ni descargar el código.

El ejecutable corresponde a la versión **Pygame**, que incluye combate con F, semillas de luz, misiones y el Guardián de las Raíces. Consulta sus [controles y recorrido](pygame_version/README.md). El progreso se conserva durante la sesión y se pierde al cerrar.

Para reconstruirlo, ejecuta `Instalar requisitos Pygame.cmd` y después, desde PowerShell:

```powershell
powershell -ExecutionPolicy Bypass -File '.\Crear exe.ps1'
```

El archivo se genera en `releases/SantuarioDeLasRaices.exe`. La compilación necesita Internet para instalar las dependencias.

La opción `--smoke-test` inicia el ejecutable, carga sus recursos, dibuja 60 fotogramas y sale automáticamente para comprobar el arranque.

## Prototipo Godot

El proyecto Godot se probó con la versión 4.6.2. Instala Godot 4.3 o posterior o coloca la versión portátil 4.6.2 en `tools/godot`; el motor no se incluye en GitHub.

## Jugar

En Windows, abre **Jugar.cmd** con doble clic. También puedes importar **project.godot** en Godot y pulsar F5. No requiere paquetes de Python, Node ni conexión a Internet para jugar.

| Acción | Control |
| --- | --- |
| Caminar | A / D o flechas izquierda / derecha |
| Saltar | W, flecha arriba o espacio; mantener para mayor altura |
| Bajar de una plataforma delgada | S o abajo + salto |
| Dash / impulso | Shift, después de despertar el altar |
| Interactuar y viajar entre salas | E, cerca de un arco u objeto |
| Cartografía | Tab o botón superior derecho |
| Pausa | Esc; también al perder el foco de la ventana |
| Volver al último acceso seguro | R |

## Recorrido

Refugio → Galería → Pozo → Cámara del Impulso → Puente Roto → Patio del Guardián.

Salta por las terrazas del Pozo. En la Cámara, pulsa E junto al altar para desbloquear dash. Para cruzar el Puente Roto, toma carrera, salta cerca del borde y pulsa Shift durante el salto. Al llegar al otro lado podrás abrir un atajo al Refugio. Regresa al balcón oeste del Pozo con dash para conseguir la memoria oculta.

El mapa muestra las salas descubiertas y tu ubicación. Las caídas conservan las habilidades y descubrimientos de la sesión. El progreso todavía no se guarda al cerrar el juego.

## Incluido en esta etapa

- Seis salas, recorrido vertical, plataformas atravesables y transiciones bidireccionales.
- Movimiento provisional con aceleración, control aéreo, salto variable, tolerancia de salto en bordes y pulsaciones anticipadas.
- Dash desbloqueable y recargable al aterrizar, con estela visual.
- Reaparición segura, atajo, secreto, cartografía, pausa y final del recorrido.
- Fondo original generado con image_gen, encuadres por sala, partículas y terreno provisional legible.

El personaje y las plataformas son gráficos provisionales. Combate, parry, enemigos, niveles, sonido, animaciones definitivas y guardado persistente pertenecen a las siguientes etapas. La puerta del guardián marca el final de este prototipo; no inicia un combate.

## Estructura

- `scripts/rooms.gd`: geometría, conexiones, puntos de llegada y objetos de cada sala.
- `scripts/player.gd`: movimiento y dibujo provisional del personaje.
- `scripts/world.gd`: colisiones, interacción, progreso de sesión, cámara y escenario.
- `scripts/interface.gd`: interfaz, cartografía y pausa.
- `assets/sanctuary.png`: fondo generado; prompt y procedencia en `assets/ART.md`.
- `tests/world_test.gd`: comprobaciones de navegación usando la física real de Godot.

## Comprobaciones

Desde PowerShell en esta carpeta:

```powershell
& '.\tools\godot\Godot_v4.6.2-stable_win64_console.exe' --headless --path . --editor --import --quit
& '.\tools\godot\Godot_v4.6.2-stable_win64_console.exe' --headless --path . --script tests/world_test.gd
```

La geometría es modular por datos y usa cuerpos estáticos en este prototipo. Se podrá trasladar a TileMapLayer cuando exista un tileset definitivo, conservando el trazado y las conexiones.
