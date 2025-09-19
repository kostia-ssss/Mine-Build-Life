from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
import math

app = Ursina()

Sky()

WORLD_SIZE = (32, 1, 32)
VIEW_SIZE = 5
MAX_HP_NUM = 10
BUILD_DIST = 5
hp_count = MAX_HP_NUM
hp = []
tex = "textures/Grass.png"

MAX_FOOD_NUM = 10
food_count = MAX_FOOD_NUM
food = []

def add_point_to_hp(tex, start_x):
    posX = start_x-len(hp)/21
    hp.append(Entity(parent=camera.ui, model="cube", scale=(0.04, 0.04, 0.04), texture=tex, position=(posX, 0.3, 0)))

def generate():
    for x in range(WORLD_SIZE[0]):
        for y in range(WORLD_SIZE[1]):
            for z in range(WORLD_SIZE[2]):
                blocks.append(Entity(model="cube", texture="textures/Grass.png", position=(x, y, z), collider="box"))

def build_block():
    hit_info = raycast(camera.world_position, camera.forward, distance=5)
    if hit_info.hit:
        blocks.append(Entity(model="cube", texture=tex, position=hit_info.entity.position + hit_info.normal, collider="box"))

def render_blocks():
    for block in blocks:
        if distance(player, block) > VIEW_SIZE:
            block.enabled = False
        else:
            block.enabled = True

def destroy_block():
    hit_info = raycast(camera.world_position, camera.forward, distance=5)
    if hit_info.hit:
        blocks.remove(hit_info.entity)   
        destroy(hit_info.entity)

def reset():
    player.position = (5, 5, 5)

def close_menu():
    mouse.locked = True
    start_btn.enabled = False
    menu_bg.enabled = False
    logo.enabled = False
    exit_btn.enabled = False
    player.gravity = 1

def input(key):
    global tex
    print(key)
    if key == "escape":
        exit()
    if key == "left mouse down":
        if start_btn.hovered:
            close_menu()
        elif exit_btn.hovered:
            exit()
        else:
            destroy_block()
    if key == "right mouse down":
        build_block()
    if key == "1":
        tex = "textures/Grass.png"
    if key == "2":
        tex = "textures/Stone.png"
    if key == "3":
        tex = "textures/Brick.png"

def update():
    render_blocks()
    if player.Y < -20:
        reset()

# for i in range(MAX_HP_NUM):
#     add_point_to_hp("textures/Heart.png", -0.1)

# for i in range(MAX_HP_NUM):
#     add_point_to_hp("textures/Food.png", 0.9)

blocks = []

generate()

player = FirstPersonController()
player.position = (5, 5, 5)
player.gravity = 0
player.cursor.texture = "textures/Cross.png"
player.cursor.scale = 0.01
player.cursor.color = color.white
player.cursor.rotation_z = 0

mouse.locked = False

menu_bg = Entity(parent=camera.ui, model="cube", scale=(2, 1, 2), texture="textures/MenuBG.jfif")
start_btn = Entity(parent=camera.ui, model="cube", scale=(0.2, 0.1, 0.2), texture="textures/PlayButton.png", collider="box")
exit_btn = Entity(parent=camera.ui, model="cube", scale=(0.1, 0.05, 0.1), texture="textures/ExitButton.png", collider="box", position=(-0.6, -0.4, 0))
logo = Entity(parent=camera.ui, model="cube", scale=(1.5, 0.2, 0.2), texture="textures/BuildAndLifeLogo.png", position=(0, 0.3, 0))

app.run()