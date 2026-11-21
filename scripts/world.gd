extends Node2D

const Rooms = preload("res://scripts/rooms.gd")
const Traveller = preload("res://scripts/player.gd")
const Interface = preload("res://scripts/interface.gd")
const BACKGROUND = preload("res://assets/sanctuary.png")

var rooms: Array[Dictionary] = Rooms.all()
var room_id := 0
var visited: Array[int] = []
var player: CharacterBody2D
var camera: Camera2D
var terrain: Node2D
var hud: Control
var respawn := Vector2(240, 570)
var shortcut_open := false
var secret_found := false
var finished := false
var map_open := false
var paused := false
var age := 0.0
var transition := 1.0
var message := ""
var message_time := 0.0
var prompt := ""
var portal_cooldown := 0.0
var checkpoint := Vector2(240, 600)
var active_object: Dictionary = {}
var decorative_rng := RandomNumberGenerator.new()

func _ready() -> void:
	_setup_input()
	terrain = Node2D.new()
	terrain.name = "Terrain"
	add_child(terrain)
	player = Traveller.new()
	player.name = "Traveller"
	add_child(player)
	camera = Camera2D.new()
	camera.position_smoothing_enabled = true
	camera.position_smoothing_speed = 6.0
	add_child(camera)
	var layer := CanvasLayer.new()
	add_child(layer)
	hud = Interface.new()
	hud.world = self
	layer.add_child(hud)
	enter_room(0, Vector2(240,570))
	if "--capture" in OS.get_cmdline_user_args():
		_capture_preview()

func _setup_input() -> void:
	var bindings := {
		"move_left":[KEY_A,KEY_LEFT], "move_right":[KEY_D,KEY_RIGHT],
		"jump":[KEY_W,KEY_UP,KEY_SPACE], "down":[KEY_S,KEY_DOWN],
		"dash":[KEY_SHIFT], "interact":[KEY_E], "map":[KEY_TAB],
		"pause":[KEY_ESCAPE], "respawn":[KEY_R]
	}
	for action in bindings:
		if not InputMap.has_action(action):
			InputMap.add_action(action)
		for key in bindings[action]:
			var event := InputEventKey.new()
			event.physical_keycode = key
			InputMap.action_add_event(action,event)

func enter_room(id: int, spawn: Vector2) -> void:
	room_id = id
	if not visited.has(id):
		visited.append(id)
	for child in terrain.get_children():
		terrain.remove_child(child)
		child.queue_free()
	for data in rooms[id].platforms:
		var body := StaticBody2D.new()
		var one_way: bool = data.size() > 4
		body.collision_layer = 4 if one_way else 1
		body.collision_mask = 2
		body.position = Vector2(data[0] + data[2]*0.5, data[1] + data[3]*0.5)
		var collision := CollisionShape2D.new()
		var shape := RectangleShape2D.new()
		shape.size = Vector2(data[2], data[3])
		collision.shape = shape
		collision.one_way_collision = one_way
		collision.one_way_collision_margin = 6.0
		body.add_child(collision)
		terrain.add_child(body)
	respawn = spawn
	player.reset_at(spawn)
	camera.position = Vector2(640,clampf(spawn.y-65,360,rooms[id].height-360))
	camera.reset_smoothing()
	portal_cooldown = 0.35
	transition = 0.9
	prompt = ""
	active_object = {}
	queue_redraw()

func _unhandled_input(event: InputEvent) -> void:
	if event.is_action_pressed("map"):
		toggle_map()
	if event.is_action_pressed("pause"):
		if map_open:
			map_open = false
		else:
			paused = not paused
		_update_frozen()
	if event.is_action_pressed("respawn") and not map_open and not paused:
		respawn_player()
	if event.is_action_pressed("interact") and not map_open and not paused and portal_cooldown <= 0.0:
		interact()

func toggle_map() -> void:
	map_open = not map_open
	paused = false
	_update_frozen()

func _update_frozen() -> void:
	player.frozen = map_open or paused

func _notification(what: int) -> void:
	if what == NOTIFICATION_APPLICATION_FOCUS_OUT and is_instance_valid(player):
		paused = true
		_update_frozen()

func _process(delta: float) -> void:
	if not paused and not map_open:
		age += delta
		message_time = maxf(message_time-delta, 0.0)
		portal_cooldown = maxf(portal_cooldown-delta, 0.0)
		transition = maxf(transition-delta*2.0, 0.0)
		camera.position.y = clampf(player.position.y-65,360,rooms[room_id].height-360)
		if player.position.y > rooms[room_id].height + 70:
			respawn_player()
		_refresh_prompt()
	queue_redraw()
	hud.queue_redraw()

func _refresh_prompt() -> void:
	prompt = ""
	active_object = {}
	var foot := player.position + Vector2(0,21)
	for portal in rooms[room_id].portals:
		if foot.distance_to(Vector2(portal.x,portal.y)) < 75:
			active_object = {"kind":"portal", "data":portal}
			prompt = "E  ·  " + portal.label
			if portal.get("dash", false) and not player.dash_unlocked:
				prompt = "El altar guarda el impulso que necesitas"
			return
	for object in rooms[room_id].objects:
		if foot.distance_to(object.at) < 80:
			active_object = object
			match object.kind:
				"checkpoint": prompt = "E  ·  Descansar en el refugio"
				"dash": prompt = "E  ·  Despertar el impulso" if not player.dash_unlocked else "El impulso te acompaña  ·  Shift"
				"shortcut": prompt = "E  ·  Abrir el atajo al Refugio" if not shortcut_open else "E  ·  Volver al Refugio"
				"shortcut_return": prompt = "E  ·  Atajo al Puente Roto" if shortcut_open else "Un camino dormido. Se abre desde el otro lado."
				"secret": prompt = "E  ·  Recoger la memoria de la raíz" if not secret_found else "La memoria está contigo"
				"finish": prompt = "E  ·  Examinar el sello del guardián"
			return

func interact() -> void:
	_refresh_prompt()
	if active_object.is_empty():
		return
	match active_object.kind:
		"portal":
			var portal: Dictionary = active_object.data
			if portal.get("dash",false) and not player.dash_unlocked:
				notify("Despierta el impulso en el altar antes de continuar.")
				return
			enter_room(portal.to,portal.spawn)
		"checkpoint":
			respawn = Vector2(240,570)
			notify("Refugio activado. Las raíces cuidarán de ti.")
		"dash":
			if not player.dash_unlocked:
				player.dash_unlocked = true
				player.dash_available = true
				notify("IMPULSO DESPERTADO  ·  Pulsa Shift. Se recarga al tocar el suelo.",7.0)
		"shortcut":
			if not shortcut_open:
				shortcut_open = true
				notify("ATAJO ABIERTO  ·  El puente y el refugio vuelven a estar unidos.",6.0)
			else:
				enter_room(0,Vector2(905,570))
		"shortcut_return":
			if shortcut_open:
				enter_room(4,Vector2(925,570))
		"secret":
			if not secret_found:
				secret_found = true
				notify("MEMORIA DE LA RAÍZ  ·  Encontraste el secreto del santuario.",6.0)
		"finish":
			finished = true
			notify("PRIMER MUNDO EXPLORADO  ·  El guardián llegará en la etapa de combate.",7.0)

func notify(text: String, duration: float = 4.5) -> void:
	message = text
	message_time = duration

func respawn_player() -> void:
	player.reset_at(respawn)
	camera.position.y = clampf(respawn.y-65,360,rooms[room_id].height-360)
	camera.reset_smoothing()
	transition = 0.9
	notify("Las raíces te devuelven al último acceso seguro.",3.0)

func _draw() -> void:
	if not is_instance_valid(camera):
		return
	var top := camera.get_screen_center_position().y - 360.0
	var tint: Color = rooms[room_id].tint
	draw_texture_rect(BACKGROUND,Rect2(-16,top-135-top*0.12,1312,875),false,tint)
	draw_rect(Rect2(0,top,1280,720),Color(0.015,0.035,0.055,0.21))
	# Distant shafts are deliberately faint to preserve collision readability.
	for i in range(4):
		var x := float(180+i*290)
		draw_colored_polygon(PackedVector2Array([Vector2(x,top),Vector2(x+30,top),Vector2(x+170,top+720),Vector2(x-60,top+720)]),Color(0.52,0.89,0.85,0.018))
	for data in rooms[room_id].platforms:
		_draw_platform(data)
	for portal in rooms[room_id].portals:
		_draw_arch(Vector2(portal.x,portal.y), Color("87c7bd"),false)
	for object in rooms[room_id].objects:
		_draw_object(object)
	for i in range(48):
		var x := fposmod(i*179.7+sin(age*0.23+i)*24.0,1280)
		var y := top + fposmod(i*67.3-age*(6.0+i%5),720)
		var alpha := 0.12+0.22*(sin(age+i)*0.5+0.5)
		draw_circle(Vector2(x,y),1.3 if i%3 else 2.0,Color(0.62,0.95,0.83,alpha))

func _draw_platform(data: Array) -> void:
	var rect := Rect2(data[0],data[1],data[2],data[3])
	var thin := data.size() > 4
	draw_rect(rect,Color("15292e") if thin else Color("101e27"))
	draw_rect(Rect2(rect.position+Vector2(0,5),Vector2(rect.size.x,9)),Color("35504c"))
	draw_line(rect.position,rect.position+Vector2(rect.size.x,0),Color("89bda0"),3.0)
	draw_line(rect.position+Vector2(0,3),rect.position+Vector2(rect.size.x,3),Color("497e70"),3.0)
	for x in range(int(rect.position.x)+24,int(rect.end.x),55):
		var depth := 14.0 if thin else 34.0+float(x%37)
		draw_line(Vector2(x,rect.position.y+14),Vector2(x-4,rect.position.y+depth),Color("294044"),1.0)
	for x in range(int(rect.position.x)+12,int(rect.end.x)-8,21):
		var h := 4.0+float((x*7)%9)
		draw_line(Vector2(x,rect.position.y),Vector2(x-3,rect.position.y-h),Color("528e78"),1.2)
		if x%3 == 0:
			draw_circle(Vector2(x-3,rect.position.y-h),2,Color("a7d4ae"))
	if not thin:
		for x in range(int(rect.position.x)+40,int(rect.end.x),150):
			_draw_fern(Vector2(x,rect.position.y),float(x%3)*0.2+0.8)

func _draw_fern(at: Vector2, scale_factor: float) -> void:
	for side in [-1,1]:
		var end := at + Vector2(side*26,-30)*scale_factor
		draw_line(at,end,Color("34645a"),1.5)
		for step in range(1,5):
			var p := at.lerp(end,step/5.0)
			draw_line(p,p+Vector2(side*10,-2)*scale_factor,Color("427767"),2)
			draw_line(p,p+Vector2(-side*3,-9)*scale_factor,Color("427767"),2)

func _draw_arch(at: Vector2, color: Color, sealed: bool) -> void:
	var radius := 33.0
	draw_rect(Rect2(at+Vector2(-44,-83),Vector2(16,83)),Color("263b40"))
	draw_rect(Rect2(at+Vector2(28,-83),Vector2(16,83)),Color("263b40"))
	draw_arc(at+Vector2(0,-83),radius,PI,TAU,24,Color("3b5555"),14,true)
	draw_arc(at+Vector2(0,-83),radius,PI,TAU,24,Color(color,0.5),2,true)
	for side in [-1,1]:
		draw_line(at+Vector2(side*29,-82),at+Vector2(side*29,-2),Color(color,0.5),2)
	if sealed:
		for i in range(-2,3):
			draw_line(at+Vector2(i*11,-93),at+Vector2(i*11,0),Color("796d51"),3)
	else:
		draw_circle(at+Vector2(0,-51),23,Color(color,0.065))
		draw_circle(at+Vector2(0,-51),4+sin(age*2)*0.8,color)

func _draw_object(object: Dictionary) -> void:
	var at: Vector2 = object.at
	match object.kind:
		"checkpoint":
			draw_rect(Rect2(at+Vector2(-32,-13),Vector2(64,13)),Color("69746a"))
			draw_line(at+Vector2(-25,-14),at+Vector2(-25,-30),Color("95a58e"),4)
			draw_line(at+Vector2(25,-14),at+Vector2(25,-30),Color("95a58e"),4)
			draw_circle(at+Vector2(0,-45),38,Color(0.85,0.72,0.43,0.07))
			draw_circle(at+Vector2(0,-45),5,Color("ebce8d"))
		"dash", "secret":
			var obtained: bool = player.dash_unlocked if object.kind == "dash" else secret_found
			draw_rect(Rect2(at+Vector2(-34,-12),Vector2(68,12)),Color("53675e"))
			draw_rect(Rect2(at+Vector2(-22,-27),Vector2(44,15)),Color("829486"))
			if not obtained:
				var p := at+Vector2(0,-65+sin(age*2.0)*6)
				for r in range(4,0,-1):
					draw_circle(p,r*13,Color(0.65,0.96,0.78,0.025))
				draw_colored_polygon(PackedVector2Array([p+Vector2(0,-17),p+Vector2(10,0),p+Vector2(0,17),p+Vector2(-10,0)]),Color("b8efd2") if object.kind=="dash" else Color("edce8a"))
				draw_arc(p,29,age,age+PI*1.5,30,Color("789c84"),1,true)
		"shortcut", "shortcut_return":
			_draw_arch(at,Color("e1bc77"),not shortcut_open)
			if not shortcut_open and object.kind=="shortcut":
				draw_line(at+Vector2(0,-18),at+Vector2(16,-45),Color("edcb8c"),4)
		"finish":
			draw_rect(Rect2(at+Vector2(-65,-205),Vector2(130,205)),Color("182b32"))
			draw_arc(at+Vector2(0,-205),65,PI,TAU,32,Color("77775c"),14,true)
			for x in [-58,58]:
				draw_line(at+Vector2(x,0),at+Vector2(x,-205),Color("77775c"),12)
			draw_arc(at+Vector2(0,-113),34,0,TAU,40,Color("d1b879"),2,true)
			draw_line(at+Vector2(0,-147),at+Vector2(0,-79),Color("d1b879"),2)
			draw_line(at+Vector2(-24,-113),at+Vector2(24,-113),Color("d1b879"),2)

func _capture_preview() -> void:
	for i in range(50):
		await get_tree().process_frame
	await RenderingServer.frame_post_draw
	DirAccess.make_dir_recursive_absolute("res://output")
	get_viewport().get_texture().get_image().save_png("res://output/sanctuary-preview.png")
	print("PREVIEW_SAVED")
	get_tree().quit()
