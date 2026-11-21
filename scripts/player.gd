extends CharacterBody2D

const SPEED := 310.0
const JUMP := -650.0
const GRAVITY := 1500.0
const DASH_SPEED := 880.0
const DASH_DURATION := 0.20

var dash_unlocked := false
var dash_available := true
var facing := 1.0
var coyote := 0.0
var jump_buffer := 0.0
var dash_time := 0.0
var dash_cooldown := 0.0
var drop_time := 0.0
var age := 0.0
var trail: Array[Dictionary] = []
var frozen := false

func _ready() -> void:
	collision_layer = 2
	collision_mask = 5
	floor_snap_length = 8.0
	var shape := CollisionShape2D.new()
	var capsule := CapsuleShape2D.new()
	capsule.radius = 13.0
	capsule.height = 42.0
	shape.shape = capsule
	add_child(shape)
	z_index = 5

func reset_at(at: Vector2) -> void:
	position = at
	velocity = Vector2.ZERO
	dash_time = 0.0
	dash_cooldown = 0.0
	drop_time = 0.0
	coyote = 0.0
	jump_buffer = 0.0
	dash_available = true
	set_collision_mask_value(3, true)
	trail.clear()

func _physics_process(delta: float) -> void:
	if frozen:
		return
	age += delta
	for ghost in trail:
		ghost.life -= delta
	trail = trail.filter(func(ghost: Dictionary) -> bool: return ghost.life > 0.0)
	var axis := Input.get_axis("move_left", "move_right")
	if axis != 0.0:
		facing = signf(axis)
	coyote = 0.11 if is_on_floor() else maxf(coyote - delta, 0.0)
	jump_buffer = maxf(jump_buffer - delta, 0.0)
	dash_cooldown = maxf(dash_cooldown - delta, 0.0)
	drop_time = maxf(drop_time - delta, 0.0)
	set_collision_mask_value(3, drop_time <= 0.0)
	if is_on_floor() and dash_time <= 0.0:
		dash_available = true
	if Input.is_action_just_pressed("jump"):
		if Input.is_action_pressed("down") and is_on_floor():
			drop_time = 0.22
			set_collision_mask_value(3, false)
			position.y += 4.0
			velocity.y = 80.0
			coyote = 0.0
		else:
			jump_buffer = 0.13
	if Input.is_action_just_pressed("dash") and dash_unlocked and dash_available and dash_cooldown <= 0.0:
		dash_time = DASH_DURATION
		dash_available = false
		dash_cooldown = 0.38
	if dash_time > 0.0:
		dash_time -= delta
		velocity = Vector2(facing * DASH_SPEED, 0.0)
		trail.append({"at":position, "life":0.22})
	else:
		velocity.x = move_toward(velocity.x, axis * SPEED, (2600.0 if is_on_floor() else 1700.0) * delta)
		velocity.y = minf(velocity.y + GRAVITY * delta, 950.0)
		if jump_buffer > 0.0 and coyote > 0.0:
			velocity.y = JUMP
			jump_buffer = 0.0
			coyote = 0.0
		if Input.is_action_just_released("jump") and velocity.y < -180.0:
			velocity.y = -180.0
	move_and_slide()
	position.x = clampf(position.x, 16.0, 1264.0)
	queue_redraw()

func _draw() -> void:
	for ghost in trail:
		draw_circle(ghost.at - position, 15.0, Color(0.48, 0.97, 0.84, ghost.life * 1.5))
	var bob := sin(age * 14.0) * minf(absf(velocity.x) / SPEED, 1.0) * 2.0
	draw_circle(Vector2(0, 0), 27, Color(0.47, 0.98, 0.84, 0.035))
	# Temporary traveller: pale wooden mask, teal cloak, amber scarf.
	draw_colored_polygon(PackedVector2Array([Vector2(-11,-4),Vector2(9,-4),Vector2(17,18+bob),Vector2(1,14),Vector2(-15,20+bob)]), Color("479f9d"))
	draw_line(Vector2(-6,13), Vector2(-7,21), Color("162d39"), 5)
	draw_line(Vector2(7,13), Vector2(8,21), Color("162d39"), 5)
	draw_style_box(_mask_style(), Rect2(-12, -23+bob, 24, 24))
	draw_line(Vector2(-4 + facing*2,-15+bob), Vector2(-4 + facing*2,-9+bob), Color("18313b"), 3)
	draw_line(Vector2(5 + facing*2,-15+bob), Vector2(5 + facing*2,-9+bob), Color("18313b"), 3)
	draw_line(Vector2(-11,1),Vector2(10,1),Color("e3ba79"),4)
	draw_line(Vector2(-facing*8,2),Vector2(-facing*(23+sin(age*10)*4),7),Color("d3a969"),4)

func _mask_style() -> StyleBoxFlat:
	var box := StyleBoxFlat.new()
	box.bg_color = Color("e4ecd9")
	box.corner_radius_top_left = 9
	box.corner_radius_top_right = 9
	box.corner_radius_bottom_left = 6
	box.corner_radius_bottom_right = 6
	return box
