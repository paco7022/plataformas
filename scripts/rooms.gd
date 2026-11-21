extends RefCounted

# Coordinates are in world pixels. Each landing is at most 115 px above the last.
# Portal positions sit on the floor; arrivals are separate from the portal trigger.
static func all() -> Array[Dictionary]:
	return [
		{
			"name": "El Refugio", "subtitle": "Donde las raíces aún recuerdan", "height": 720,
			"tint": Color(0.88, 1.0, 0.96),
			"platforms": [[0,600,1280,160], [450,492,190,22,1], [700,420,150,22,1]],
			"portals": [{"x":1210,"y":600,"to":1,"spawn":Vector2(110,570),"label":"La Galería"}],
			"objects": [{"kind":"checkpoint","at":Vector2(240,600)}, {"kind":"shortcut_return","at":Vector2(980,600)}],
			"hint": "Sigue las luces hacia el este. E para atravesar los arcos."
		},
		{
			"name": "La Galería", "subtitle": "Un sendero suspendido en el silencio", "height":720,
			"tint": Color(0.76, 0.91, 1.0),
			"platforms": [[0,600,300,160], [450,600,300,160], [930,600,350,160], [330,505,100,22,1], [770,485,120,22,1]],
			"portals": [{"x":65,"y":600,"to":0,"spawn":Vector2(1120,570),"label":"El Refugio"}, {"x":1210,"y":600,"to":2,"spawn":Vector2(140,1010),"label":"El Pozo"}],
			"objects": [], "hint":"Mantén el salto para llegar más alto. Abajo + salto atraviesa las plataformas delgadas."
		},
		{
			"name": "El Pozo", "subtitle": "Lo que duerme arriba espera tu regreso", "height":1120,
			"tint": Color(0.73, 1.0, 0.91),
			"platforms": [[0,1040,1280,120], [250,925,180,22,1], [470,810,180,22,1], [250,695,180,22,1], [470,580,180,22,1], [690,465,220,22,1], [640,350,640,32,1], [0,350,270,32,1]],
			"portals": [{"x":65,"y":1040,"to":1,"spawn":Vector2(1120,570),"label":"La Galería"}, {"x":1210,"y":350,"to":3,"spawn":Vector2(120,570),"label":"Cámara del Impulso"}],
			"objects": [{"kind":"secret","at":Vector2(120,350)}],
			"hint":"Asciende por las terrazas. La luz del balcón oeste está fuera del alcance de un salto."
		},
		{
			"name": "Cámara del Impulso", "subtitle": "El viento también echa raíces", "height":720,
			"tint": Color(0.95, 0.93, 0.78),
			"platforms": [[0,600,1280,160], [340,485,150,22,1], [790,485,150,22,1]],
			"portals": [{"x":65,"y":600,"to":2,"spawn":Vector2(1110,320),"label":"El Pozo"}, {"x":1210,"y":600,"to":4,"spawn":Vector2(120,570),"label":"Puente Roto","dash":true}],
			"objects": [{"kind":"dash","at":Vector2(640,600)}],
			"hint":"Una chispa antigua permanece en el altar. Acércate y pulsa E."
		},
		{
			"name": "Puente Roto", "subtitle": "Confía en el impulso", "height":720,
			"tint": Color(0.70, 0.85, 1.0),
			"platforms": [[0,600,430,160], [800,600,480,160]],
			"portals": [{"x":65,"y":600,"to":3,"spawn":Vector2(1110,570),"label":"Cámara del Impulso"}, {"x":1210,"y":600,"to":5,"spawn":Vector2(120,570),"label":"Patio del Guardián"}],
			"objects": [{"kind":"shortcut","at":Vector2(1000,600)}],
			"hint":"Toma carrera, salta desde el borde y pulsa Shift en el aire."
		},
		{
			"name": "Patio del Guardián", "subtitle": "El santuario contiene la respiración", "height":720,
			"tint": Color(1.0, 0.87, 0.72),
			"platforms": [[0,600,1280,160], [320,475,170,22,1], [760,475,170,22,1]],
			"portals": [{"x":65,"y":600,"to":4,"spawn":Vector2(1120,570),"label":"Puente Roto"}],
			"objects": [{"kind":"finish","at":Vector2(1110,600)}],
			"hint":"Has alcanzado el límite del primer mundo. La puerta aguarda a su guardián."
		}
	]
