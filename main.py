from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
from random import randint
import time

app = Ursina()

DAY_SKY = load_texture("textures/DaySky.png")
NIGHT_SKY = load_texture("textures/NightSky.png")
sky = Sky(texture=DAY_SKY)

start_time = 0
WORLD_SIZE = (12, 7, 12)
TPS = 50
FLOWER_SPAWN_CHANCE = 5
ANDESITE_SPAWN_CHANCE = 3
DIORITE_SPAWN_CHANCE = 3
tex = "textures/Grass.png"
tick = 0

b_textures = {
    1: load_texture("textures/Grass.png"),
    2: load_texture("textures/Stone.png"),
    3: load_texture("textures/Brick.png"),
    4: load_texture("textures/Wood.png"),
    5: load_texture("textures/Ground.png"),
    6: load_texture("textures/Andesite.png"),
    7: load_texture("textures/Diorite.png"),
    8: load_texture("textures/YellowFlower.png"),
    9: load_texture("textures/RedFlower.png"),
}

blocks = []
blocks_by_key = {}

def pos_to_key(pos):
    return (int(pos.x), int(pos.y), int(pos.z))

def neighbor_keys(key):
    x,y,z = key
    return [
        (x+1,y,z), (x-1,y,z),
        (x,y+1,z), (x,y-1,z),
        (x,y,z+1), (x,y,z-1),
    ]

def generate_world():
    for x in range(WORLD_SIZE[0]):
        for y in range(WORLD_SIZE[1]):
            for z in range(WORLD_SIZE[2]):
                pos = (x, -y, z)
                if y == 0:
                    tex_i = 1
                elif 0 < y < 3:
                    tex_i = 5
                else:
                    num = randint(1, 100)
                    if num <= ANDESITE_SPAWN_CHANCE:
                        tex_i = 6
                    elif num <= ANDESITE_SPAWN_CHANCE + DIORITE_SPAWN_CHANCE:
                        tex_i = 7
                    else:
                        tex_i = 2
                e = Entity(model="cube", texture=b_textures[tex_i], position=pos, collider=None)
                blocks.append(e)
                blocks_by_key[pos_to_key(e.position)] = e

def neighbor_keys(key):
    x, y, z = key
    return [
        (x+1, y, z), (x-1, y, z),
        (x, y+1, z), (x, y-1, z),
        (x, y, z+1), (x, y, z-1),
    ]

def has_empty_neighbor_by_key(key):
    for n in neighbor_keys(key):
        if n not in blocks_by_key:
            return True
    return False

def update_block_and_neighbors(key):
    keys = [key] + neighbor_keys(key)
    for k in keys:
        b = blocks_by_key.get(k)
        if not b:
            continue
        visible = has_empty_neighbor_by_key(k)
        prev = getattr(b, "_visible", None)
        if visible:
            if prev is not True:
                b.enabled = True
                b.collider = "box"
                b._visible = True
        else:
            if prev is not False:
                b.enabled = False
                b.collider = None
                b._visible = False


def update_all_visibility_once():
    for k in list(blocks_by_key.keys()):
        update_block_and_neighbors(k)

def build_block():
    hit_info = raycast(camera.world_position, camera.forward, distance=5)
    if hit_info.hit:
        new_pos = hit_info.entity.position + hit_info.normal
        new_ent = Entity(model="cube", texture=tex, position=new_pos, collider=None)
        blocks.append(new_ent)
        blocks_by_key[pos_to_key(new_ent.position)] = new_ent
        update_block_and_neighbors(pos_to_key(new_pos))

def destroy_block():
    hit_info = raycast(camera.world_position, camera.forward, distance=5)
    if hit_info.hit:
        ent = hit_info.entity
        k = pos_to_key(ent.position)
        if ent in blocks:
            blocks.remove(ent)
        if k in blocks_by_key:
            del blocks_by_key[k]
        destroy(ent)
        update_block_and_neighbors(k)

def update_sky():
    if tick % 2000 <= 1000:
        sky.texture = DAY_SKY
    else:
        sky.texture = NIGHT_SKY

def reset():
    player.position = (5,5,5)

def close_menu():
    global start_time
    mouse.locked = True
    start_btn.enabled = False
    menu_bg.enabled = False
    logo.enabled = False
    exit_btn.enabled = False
    player.gravity = 1
    start_time = time.time()

def input(key):
    global tex
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
        tex = b_textures[1]
    if key == "2": 
        tex = b_textures[2]
    if key == "3": 
        tex = b_textures[3]
    if key == "4": 
        tex = b_textures[4]
    if key == "5": 
        tex = b_textures[5]
    if key == "6": 
        tex = b_textures[6]
    if key == "7": 
        tex = b_textures[7]
    if key == "f3":
        ticsText.enabled = not ticsText.enabled
        posText.enabled = not posText.enabled
    if key == "u":
        mouse.locked = not mouse.locked
    if key == "r":
        reset()

ticsText = Text(text=' ', scale=2, position=(-0.75,0.4), origin=(0,0), color=color.hex("#000000"))
posText = Text(text=' ', scale=2, position=(-0.675,0.34), origin=(0,0), color=color.hex("#000000"))
ticsText.enabled = False
posText.enabled = False

def update():
    global tick
    t = time.time() - start_time
    ticsText.text = f"Tick №{round(t*TPS)}"
    if hasattr(player, 'position'):
        posText.text = f"POSITION: {player.position}"
    tick = round(t*TPS)
    update_sky()
    if player.y < -20:
        reset()

generate_world()
update_all_visibility_once()

player = FirstPersonController()
player.position = (5,5,5)
player.gravity = 0
player.cursor.texture = "textures/Cross.png"
player.cursor.scale = 0.01
player.cursor.color = color.white
player.cursor.rotation_z = 0
player.height = 1.5

mouse.locked = False

menu_bg = Entity(parent=camera.ui, model="cube", scale=(2,1,2), texture="textures/MenuBG.png")
start_btn = Entity(parent=camera.ui, model="cube", scale=(0.2,0.1,0.2), texture="textures/PlayButton.png", collider="box")
exit_btn = Entity(parent=camera.ui, model="cube", scale=(0.1,0.05,0.1), texture="textures/ExitButton.png", collider="box", position=(-0.6,-0.4,0))
logo = Entity(parent=camera.ui, model="cube", scale=(1.5,0.2,0.2), texture="textures/BuildAndLifeLogo.png", position=(0,0.3,0))

app.run()