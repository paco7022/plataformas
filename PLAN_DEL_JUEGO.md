# Plan del juego de plataformas

Estado: etapa 1 implementada en Godot 4.6.2. Seis salas jugables, personaje provisional, dash desbloqueable, atajo, secreto y cartografía. Validación: 51 comprobaciones de física y navegación aprobadas y captura visual del juego renderizado. Consulta README.md para jugar y continuar el desarrollo.

## Visión

Metroidvania 2D para un jugador, inspirado en la exploración y precisión de Hollow Knight, con mundo, personajes y arte originales. Los pilares son movimiento fluido, exploración con habilidades desbloqueables y parry como herramienta central del combate.

Base técnica: Godot 4 y GDScript, inicialmente para PC con teclado. Se usa CharacterBody2D para el jugador y geometría modular por datos con cuerpos estáticos para el escenario provisional. TileMapLayer queda para integrar el tileset definitivo.

Referencias oficiales:
- https://docs.godotengine.org/en/stable/tutorials/physics/using_character_body_2d.html
- https://docs.godotengine.org/en/stable/tutorials/2d/using_tilemaps.html

## Controles propuestos

| Acción | Teclas |
| --- | --- |
| Movimiento lateral | A/D o izquierda/derecha |
| Salto | W, arriba o espacio |
| Bajar por plataformas atravesables | S o abajo + salto |
| Dash | Shift |
| Ataque | J |
| Parry | K |
| Interactuar | E |
| Habilidad equipada | L |
| Mapa | Tab |
| Pausa y opciones | Esc |

Controles reasignables en la etapa de interfaz. S/abajo también permite orientar un ataque descendente cuando exista esa habilidad.

## Etapa 1: mapa inicial jugable

Ambientación provisional: ruinas subterráneas con vegetación luminosa y maquinaria antigua. Nombre provisional del área: Santuario de las Raíces.

Construir seis salas con bloques simples y colisiones, antes de vestirlas con arte final:

1. Refugio: inicio seguro, punto de control y espacio para aprender a moverse.
2. Galería: saltos cortos, diferentes alturas y plataformas atravesables.
3. Pozo: recorrido vertical y desvío hacia un secreto visible pero inicialmente inaccesible.
4. Cámara del impulso: lugar donde se obtendrá el dash; durante las primeras pruebas será un desbloqueo provisional.
5. Puente roto: hueco que exige dash y mecanismo para abrir un atajo al Refugio.
6. Patio del guardián: arena reservada para el primer minijefe y salida al siguiente bioma.

Ruta principal: Refugio → Galería → Pozo → Cámara del impulso → Puente roto → Patio del guardián.
Atajo desbloqueable: Puente roto ↔ Refugio.
Ruta opcional: regreso al Pozo con dash para alcanzar un secreto.

El primer entregable incluye el mapa completo de esta zona, un personaje provisional, desplazamiento, salto, dash de prueba, cámara, colisiones, reaparición y transiciones entre salas. No incluye todavía enemigos ni progresión completa.

Diseñar distancias a partir del alcance medido del salto y del dash. Las rutas obligatorias tendrán margen de aterrizaje; los retos precisos serán opcionales. Separar las capas de fondo, terreno con colisión, decoración y primer plano.

Criterios de aceptación:
- Recorrer las seis salas sin quedar atrapado ni atravesar el suelo.
- Entrar y salir por ambos lados de cada conexión prevista.
- Caer en un peligro y reaparecer en un punto seguro.
- Alcanzar las plataformas obligatorias con margen razonable.
- Ver el paso bloqueado antes de obtener dash y cruzarlo después.
- Abrir el atajo y volver al Refugio.
- Mantener al jugador y sus zonas de aterrizaje visibles con la cámara.

## Etapa 2: movimiento definitivo

Ajustar aceleración, frenado, control aéreo, salto de altura variable y dash. Añadir un pequeño margen para saltar después de abandonar un borde y recordar brevemente una pulsación de salto hecha antes de aterrizar. Estos márgenes evitan que pequeñas diferencias de tiempo hagan sentir torpe el control.

Separar los estados de reposo, carrera, salto, caída, dash, ataque, parry, daño y muerte. Definir qué acciones pueden interrumpir a otras. Probar entrada y física a distintas tasas de renderizado, tomando 60 FPS como objetivo inicial sujeto al equipo de prueba.

## Etapa 3: combate y parry

Ataque básico, salud, retroceso, breve protección tras recibir daño y señales claras antes de cada golpe enemigo.

Regla central: todos los ataques de enemigos y jefes pueden contrarrestarse con un parry bien ejecutado, incluidos proyectiles. El parry evita el daño del impacto y genera energía para una habilidad; puede desequilibrar enemigos o devolver proyectiles. Los jefes tendrán un medidor de postura para evitar que un solo parry los inmovilice continuamente.

Propuesta inicial para ajustar jugando: ventana de éxito de 0,15 segundos, seguida de una recuperación corta que impida mantener protección continua pulsando repetidamente. Mantener K no concede invulnerabilidad. Cada impacto de una secuencia requiere su propio parry, con ritmos que permitan reaccionar.

Los peligros permanentes del escenario, como abismos o suelo de pinchos, se consideran peligros de navegación. Las trampas que disparen ataques podrán usar el mismo sistema de parry que los enemigos. Esta distinción se comunicará visualmente.

Feedback del parry: destello, sonido, breve pausa de impacto y respuesta clara del atacante. Añadir opciones para reducir sacudidas y destellos.

## Etapa 4: enemigos

Implementar gradualmente cuatro arquetipos y un minijefe:
- Patrullero cuerpo a cuerpo: enseña anticipación y alcance.
- Tirador: enseña devolución de proyectiles.
- Volador: exige controlar posición y altura.
- Guardián con escudo: abre oportunidades después de un parry.
- Minijefe: combina ataques individuales y secuencias con señales legibles.

Cada enemigo tendrá preparación, ataque y recuperación reconocibles. Primero se valida cada uno por separado y después en combinaciones dentro del mapa.

## Etapa 5: niveles y desbloqueables

Ganar experiencia por combate, exploración y desafíos. Subir de nivel concede puntos para mejoras moderadas de salud, energía y especializaciones de combate. Evitar exigir repetir combates para superar la ruta principal.

Separar mejoras de estadísticas y habilidades de exploración: dash, doble salto y salto de pared se obtienen mediante hitos del mundo. El dash llega pronto para sostener el ritmo del juego. Añadir mejoras de parry, habilidades activas, coleccionables y secretos; limitar las mejoras equipadas para permitir diferentes estilos.

## Etapa 6: arte y sonido

Usar el modelo de generación de imágenes para crear los assets visuales, como pidió el usuario. Primero definir una guía visual: paleta, escala, siluetas, iluminación y materiales coherentes.

Orden de producción: concepto del primer bioma → fondos por capas → terreno modular → decoración → personaje → enemigos → iconos e interfaz.

Solicitar transparencias para personajes y objetos aislados. Revisar que el terreno encaje sin costuras, que las siluetas se distingan del fondo y que los elementos interactivos se reconozcan. Los sprites y animaciones requerirán revisión de tamaño, pivotes y continuidad entre fotogramas; una imagen generada no equivale a una animación ya lista para el motor.

Integrar música, ambientes y efectos con licencia adecuada en una fase posterior. Ajustar audio del salto, dash, golpes y parry para reforzar la respuesta de los controles.

## Etapa 7: interfaz, guardado y demo

Menú principal, pausa, salud, energía, experiencia, mapa descubierto, habilidades y opciones. Guardar punto de control, experiencia, habilidades, atajos, secretos y progreso de jefes. Comprobar que cerrar y reabrir conserva un estado válido.

Primera demo objetivo: un bioma de seis salas, cuatro arquetipos enemigos, un minijefe, dash, parry, una muestra de progresión y un secreto que motive regresar. Duración orientativa: 10–20 minutos, a validar jugando.

## Orden acordado de trabajo

Plan → mapa con personaje provisional → ajuste de movimiento → combate y parry → enemigos → progresión → arte integrado → interfaz, guardado y pulido.

La generación de conceptos visuales puede acompañar el trabajo del mapa una vez fijada su dirección artística. No ampliar a más biomas antes de validar que el recorrido, el movimiento y el parry resultan satisfactorios.
