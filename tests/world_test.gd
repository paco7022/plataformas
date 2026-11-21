extends SceneTree

var world: Node2D
var failures := 0
var checks := 0

func _initialize() -> void:
	call_deferred("run")

func tick(count: int = 1) -> void:
	for i in range(count):
		await physics_frame
		await process_frame

func check(ok: bool, label: String) -> void:
	checks += 1
	if not ok:
		failures += 1
		push_error("FAIL: " + label)
	else:
		print("PASS: " + label)

func release_keys() -> void:
	for action in ["move_left","move_right","jump","dash","down"]:
		Input.action_release(action)

func place(id: int, at: Vector2) -> void:
	release_keys()
	world.enter_room(id,at)
	await tick(20)

func hop(target: float, dash: bool = false) -> void:
	var direction: float = signf(target-world.player.position.x)
	var action := "move_right" if direction > 0 else "move_left"
	Input.action_press(action)
	Input.action_press("jump")
	await tick(2)
	for frame in range(120):
		if dash and frame == 14:
			Input.action_press("dash")
		if frame == 17:
			Input.action_release("dash")
		if (target-world.player.position.x)*direction < 12:
			Input.action_release(action)
		await tick()
		if frame > 5 and world.player.is_on_floor():
			break
	release_keys()
	await tick(10)

func run() -> void:
	world = load("res://scenes/world.tscn").instantiate()
	root.add_child(world)
	await tick(30)
	check(world.rooms.size()==6,"six rooms loaded")
	check(world.player.is_on_floor(),"initial spawn lands on solid ground")
	check(not world.player.dash_unlocked,"dash starts locked")
	Input.action_press("move_right")
	await tick(30)
	Input.action_release("move_right")
	check(world.player.position.x>350,"horizontal movement responds to input")
	await tick(15)
	check(absf(world.player.velocity.x)<1,"player stops without sliding")
	# Every declared doorway is physically reachable at floor level and reciprocal.
	for id in range(6):
		for portal in world.rooms[id].portals:
			await place(id,Vector2(portal.x,portal.y-30))
			check(world.player.is_on_floor(),"doorway %d to %d has footing" % [id,portal.to])
			if portal.get("dash",false):
				world.player.dash_unlocked = false
				world.interact()
				check(world.room_id==id,"bridge entrance requires the dash unlock")
				world.player.dash_unlocked = true
			world.interact()
			await tick(20)
			check(world.room_id==portal.to and world.player.is_on_floor(),"doorway %d to %d lands safely" % [id,portal.to])
	# Actual jump physics, not merely connectivity metadata.
	await place(1,Vector2(260,570))
	await hop(375)
	check(world.player.position.y<500 and world.player.is_on_floor(),"gallery first stepping stone")
	await hop(520)
	check(world.player.position.x>450 and world.player.is_on_floor(),"gallery first gap")
	await place(1,Vector2(720,570))
	await hop(825)
	check(world.player.position.y<480 and world.player.is_on_floor(),"gallery second stepping stone")
	await hop(1000)
	check(world.player.position.x>930 and world.player.is_on_floor(),"gallery second gap")
	var staircases := [[Vector2(220,1010),340.0,925.0],[Vector2(400,895),520.0,810.0],[Vector2(490,780),380.0,695.0],[Vector2(400,665),520.0,580.0],[Vector2(620,550),740.0,465.0],[Vector2(800,435),980.0,350.0]]
	for step in staircases:
		await place(2,step[0])
		await hop(step[1])
		check(world.player.is_on_floor() and absf(world.player.position.y+21-step[2])<4,"pozo terrace y=%d" % int(step[2]))
	# Drop-through must ignore only one-way terrain, never the solid floor.
	await place(0,Vector2(530,460))
	Input.action_press("down")
	Input.action_press("jump")
	await tick(2)
	release_keys()
	await tick(40)
	check(world.player.position.y>550 and world.player.is_on_floor(),"drop-through reaches the solid floor")
	await place(3,Vector2(640,570))
	world.player.dash_unlocked = false
	world.interact()
	check(world.player.dash_unlocked,"altar unlocks dash")
	await place(4,Vector2(410,570))
	await hop(875,false)
	check(world.player.position.x<800,"bridge cannot be crossed with a normal jump")
	await place(4,Vector2(410,570))
	await hop(850,true)
	check(world.player.position.x>=800 and world.player.is_on_floor(),"bridge crosses with jump plus dash")
	check(world.player.dash_available,"dash recharges on landing")
	await place(4,Vector2(1000,570))
	world.interact()
	check(world.shortcut_open,"shortcut activates from the far side")
	world.interact()
	check(world.room_id==0,"shortcut returns to refuge")
	await place(0,Vector2(980,570))
	world.interact()
	check(world.room_id==4,"shortcut works in reverse")
	await place(2,Vector2(655,320))
	await hop(235,true)
	check(world.player.position.x<270 and absf(world.player.position.y-329)<5,"secret balcony reachable using dash")
	await place(2,Vector2(120,320))
	world.interact()
	check(world.secret_found,"memory can be collected")
	await place(2,Vector2(255,320))
	await hop(675,true)
	check(world.player.position.x>640 and absf(world.player.position.y-329)<5,"secret balcony has a return route")
	await place(4,Vector2(120,570))
	world.player.position = Vector2(600,850)
	await tick(5)
	check(world.player.position.x<200 and world.player.position.y<600,"fall respawns at safe entrance")
	check(world.player.dash_unlocked and world.secret_found and world.shortcut_open,"fall preserves session progression")
	world.toggle_map()
	var before: Vector2 = world.player.position
	Input.action_press("move_right")
	await tick(15)
	check(world.player.position.is_equal_approx(before),"map pauses movement")
	release_keys()
	world.toggle_map()
	await place(5,Vector2(1110,570))
	world.interact()
	check(world.finished,"guardian seal completes the route")
	print("RESULT: %d checks, %d failures" % [checks,failures])
	quit(1 if failures else 0)
