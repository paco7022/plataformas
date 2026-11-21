# Validación de la etapa 1

Motor: Godot 4.6.2 estable, Windows x64. Fecha: 17 de octubre de 2026.

La ejecución de `world_test.gd` finalizó con **51 comprobaciones, 0 fallos**, usando la física real del proyecto a 60 pasos por segundo. Comprueba entradas seguras y tránsito entre salas, movimiento y frenado, plataformas de la Galería, seis escalones del Pozo, descenso por plataformas atravesables, desbloqueo del dash, puente imposible con salto normal y alcanzable con dash, atajo bidireccional, acceso y retorno del secreto, conservación del progreso tras caer, pausa del movimiento con el mapa y llegada al sello final.

También se ejecutó el juego con renderizado OpenGL 3.3 en Intel UHD Graphics. La captura `output/sanctuary-preview.png` fue revisada visualmente: fondo importado, personaje visible, suelo y plataformas, indicadores de interacción y controles legibles a 1280×720. La importación y la ejecución aprobada no mostraron errores de script.

Las pruebas automatizadas colocan al jugador en los puntos de partida de los retos antes de moverlo mediante las acciones de entrada. No sustituyen una sesión completa de evaluación humana de dificultad ni miden rendimiento sostenido. No se ha validado exportación a otras plataformas.

Limitaciones de esta etapa: progreso de sesión sin guardado en disco, gráficos provisionales para personaje y terreno, sin combate ni audio.
