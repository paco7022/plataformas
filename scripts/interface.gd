extends Control

var world: Node2D
var serif := SystemFont.new()
var sans := SystemFont.new()
var map_button: Button
const INK := Color("e1e9da")
const MUTED := Color("8baaa5")
const GOLD := Color("d5b97b")
const TEAL := Color("92d7be")

func _ready() -> void:
	serif.font_names = PackedStringArray(["Georgia", "Times New Roman"])
	sans.font_names = PackedStringArray(["Segoe UI", "Arial"])
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	map_button = Button.new()
	map_button.text = "TAB   Cartografía"
	map_button.position = Vector2(1060,30)
	map_button.size = Vector2(176,40)
	map_button.focus_mode = Control.FOCUS_NONE
	map_button.add_theme_font_override("font",sans)
	map_button.add_theme_font_size_override("font_size",15)
	map_button.add_theme_color_override("font_color",INK)
	map_button.add_theme_stylebox_override("normal",_box(Color(0.025,0.07,0.085,0.85),Color("405e59")))
	map_button.add_theme_stylebox_override("hover",_box(Color("223c3c"),GOLD))
	map_button.pressed.connect(func() -> void: world.toggle_map())
	add_child(map_button)

func _box(fill: Color, border: Color) -> StyleBoxFlat:
	var box := StyleBoxFlat.new()
	box.bg_color = fill
	box.border_color = border
	box.set_border_width_all(1)
	box.set_corner_radius_all(3)
	return box

func _text(at: Vector2, text: String, size: int = 16, color: Color = INK, elegant: bool = false) -> void:
	draw_string(serif if elegant else sans,at,text,HORIZONTAL_ALIGNMENT_LEFT,-1,size,color)

func _center(y: float, text: String, size: int = 16, color: Color = INK, elegant: bool = false) -> void:
	var font: Font = serif if elegant else sans
	var width := font.get_string_size(text,HORIZONTAL_ALIGNMENT_LEFT,-1,size).x
	_text(Vector2((1280-width)/2,y),text,size,color,elegant)

func _draw() -> void:
	# Subtle top and bottom shades keep the scenery visible.
	for i in range(8):
		draw_rect(Rect2(0,i*18,1280,18),Color(0.012,0.027,0.04,0.52*(1.0-i/8.0)))
		draw_rect(Rect2(0,720-(i+1)*10,1280,10),Color(0.012,0.027,0.04,0.9*(1.0-i/8.0)))
	draw_arc(Vector2(51,45),14,0,TAU,32,GOLD,1,true)
	draw_line(Vector2(51,33),Vector2(51,57),GOLD,1)
	draw_line(Vector2(44,40),Vector2(58,50),GOLD,1)
	_text(Vector2(78,42),"S A N T U A R I O   D E   L A S   R A Í C E S",14,INK)
	_text(Vector2(78,61),"CAPÍTULO I    /    EL DESPERTAR",10,MUTED)
	_text(Vector2(40,108),world.rooms[world.room_id].name,31,INK,true)
	_text(Vector2(42,132),world.rooms[world.room_id].subtitle,14,MUTED)
	draw_line(Vector2(42,149),Vector2(94,149),GOLD,1)
	_text(Vector2(40,678),"A D / ← →   Mover",13,MUTED)
	_text(Vector2(210,678),"W / ↑ / Espacio   Saltar",13,MUTED)
	_text(Vector2(420,678),"E   Interactuar",13,MUTED)
	_text(Vector2(562,678),"Shift   Impulso" if world.player.dash_unlocked else "Shift   Impulso por descubrir",13,TEAL if world.player.dash_unlocked else MUTED)
	_text(Vector2(40,703),"R   Volver al acceso seguro     ·     Esc   Pausa",11,Color("6d8887"))
	_text(Vector2(1024,678),"%02d / 06   SALAS" % world.visited.size(),13,GOLD)
	_text(Vector2(1024,701),"MUNDO EN CONSTRUCCIÓN",10,MUTED)
	if world.player.dash_unlocked:
		draw_circle(Vector2(1018,49),5,TEAL if world.player.dash_available else Color("314e4c"))
		_text(Vector2(899,54),"IMPULSO",12,TEAL)
	if not world.prompt.is_empty():
		var width := sans.get_string_size(world.prompt,HORIZONTAL_ALIGNMENT_LEFT,-1,16).x+40
		draw_style_box(_box(Color(0.02,0.055,0.07,0.94),Color("426760")),Rect2((1280-width)/2,583,width,42))
		_center(610,world.prompt,16,INK)
	elif world.age < 15.0 or world.room_id != 0:
		_center(634,world.rooms[world.room_id].hint,13,MUTED)
	if world.message_time > 0:
		draw_style_box(_box(Color(0.025,0.07,0.075,0.96),Color("72816a")),Rect2(170,174,940,56))
		_center(208,world.message,16,GOLD)
	if world.map_open:
		_draw_map()
	if world.paused:
		draw_rect(Rect2(0,0,1280,720),Color(0.01,0.03,0.045,0.91))
		_center(312,"Un momento de quietud",40,INK,true)
		_center(358,"Esc para volver al santuario",17,GOLD)
		_center(404,"Tu progreso se conserva durante esta sesión.",14,MUTED)
	if world.transition > 0.0:
		draw_rect(Rect2(0,0,1280,720),Color(0.01,0.025,0.04,world.transition*0.6))

func _draw_map() -> void:
	draw_rect(Rect2(0,0,1280,720),Color(0.018,0.039,0.051,0.97))
	_text(Vector2(85,92),"C A R T O G R A F Í A",13,GOLD)
	_text(Vector2(85,144),"Santuario de las Raíces",38,INK,true)
	_text(Vector2(85,174),"Seis lugares unidos por una misma raíz.",15,MUTED)
	var positions: Array[Vector2] = [Vector2(110,385),Vector2(315,385),Vector2(520,385),Vector2(520,245),Vector2(725,245),Vector2(930,245)]
	var names := ["El Refugio","La Galería","El Pozo","Cámara del Impulso","Puente Roto","Patio del Guardián"]
	for i in range(5):
		var from := positions[i]+Vector2(85,37)
		var to := positions[i+1]+Vector2(85,37)
		draw_line(from,to,Color("385b58"),2,true)
	var shortcut_color := GOLD if world.shortcut_open else Color("334540")
	draw_polyline(PackedVector2Array([positions[4]+Vector2(85,75),Vector2(810,530),Vector2(195,530),positions[0]+Vector2(85,75)]),shortcut_color,1.5,true)
	_text(Vector2(402,553),"ATAJO ABIERTO" if world.shortcut_open else "UN CAMINO POR DESPERTAR",11,shortcut_color)
	for i in range(6):
		var explored: bool = world.visited.has(i)
		var current: bool = world.room_id == i
		draw_style_box(_box(Color("213d3d") if current else Color("11262e"),TEAL if current else Color("46665e") if explored else Color("243b40")),Rect2(positions[i],Vector2(170,75)))
		_text(positions[i]+Vector2(13,24),"%02d" % (i+1),11,GOLD if explored else MUTED)
		_text(positions[i]+Vector2(13,49),names[i] if explored else "Territorio inexplorado",13,INK if explored else MUTED)
		if current:
			draw_circle(positions[i]+Vector2(151,20),4,TEAL)
	_text(Vector2(85,622),"◈  Impulso: " + ("despertado" if world.player.dash_unlocked else "por descubrir"),15,TEAL)
	_text(Vector2(430,622),"Memoria de la raíz: " + ("encontrada" if world.secret_found else "oculta en el pozo"),15,GOLD)
	_text(Vector2(85,672),"Tab / Esc  ·  Volver al mundo",14,MUTED)
