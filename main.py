from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
from random import randint
import time

app = Ursina()

DAY_SKY = load_texture("textures/DaySky.png")
NIGHT_SKY = load_texture("textures/NightSky.png")
sky = Sky(texture=DAY_SKY)

start_time = 0
cells_num = 9
tex_id = 1
selected_item = 1
WORLD_SIZE = (12, 7, 12)
TPS = 50
FLOWER_SPAWN_CHANCE = 5
ANDESITE_SPAWN_CHANCE = 3
DIORITE_SPAWN_CHANCE = 3
TREE_HEIGHT = 4
TALL_TREE_HEIGHT = 5
TREE_SPAWN_CHANCE = 1
tex = "textures/Grass.png"
tick = 0
selecter = Entity(parent=camera.ui, model="cube", texture="textures/InventoryBorder.png", scale=0.09)

b_textures = {
    1: load_texture("textures/Grass.png"),
    2: load_texture("textures/Stone.png"),
    3: load_texture("textures/Brick.png"),
    4: load_texture("textures/Wood.png"),
    5: load_texture("textures/Ground.png"),
    6: load_texture("textures/Andesite.png"),
    7: load_texture("textures/Diorite.png"),
    8: load_texture("textures/WoodPlanks.png"),
    9: load_texture("textures/Leafs.png"),
}

blocks = []
inv_cells = []
inv_blocks = []
blocks_by_key = {}

class Block(Entity):
    def __init__(self, tex_id, add_to_scene_entities=True, enabled=True, **kwargs):
        super().__init__(add_to_scene_entities, enabled, **kwargs)
        if tex_id == 11:
            self.is_transparent = True
        else:
            self.is_transparent = False

def pos_to_key(pos):
    return (int(pos.x), int(pos.y), int(pos.z))

def neighbor_keys(key):
    x,y,z = key
    return [
        (x+1,y,z), (x-1,y,z),
        (x,y+1,z), (x,y-1,z),
        (x,y,z+1), (x,y,z-1),
    ]

def add_entity(tex_id, pos, model, scale=(1, 1, 1)):
    global blocks, blocks_by_key
    e = Block(tex_id, model=model, texture=b_textures[tex_id], position=pos, scale=scale)
    blocks.append(e)
    blocks_by_key[pos_to_key(e.position)] = e

def generate_world():
    for x in range(WORLD_SIZE[0]):
        for y in range(WORLD_SIZE[1]):
            for z in range(WORLD_SIZE[2]):
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
                add_entity(tex_i, Vec3(x, -y, z), "cube")

def generate_tree(pos: Vec3, height: int):
    x, z = pos.X, pos.Z
    for y in range(height):
        add_entity(4, (x, y+1, z), "wood", (0.5, 0.5, 0.5))
    add_entity(9, (x, height+1, z), "cube")
    
    add_entity(9, (x+1, height, z), "cube")
    add_entity(9, (x-1, height, z), "cube")
    add_entity(9, (x, height, z+1), "cube")
    add_entity(9, (x, height, z-1), "cube")
    
    add_entity(9, (x+1, height-1, z), "cube")
    add_entity(9, (x-1, height-1, z), "cube")
    add_entity(9, (x, height-1, z+1), "cube")
    add_entity(9, (x, height-1, z-1), "cube")

def generate_trees():
    for x in range(WORLD_SIZE[0]):
        for z in range(WORLD_SIZE[2]):
            if randint(1, 100) <= TREE_SPAWN_CHANCE:
                if randint(1, 4) == 4:
                    generate_tree(Vec3(x, 0, z), TREE_HEIGHT+2)
                else:
                    generate_tree(Vec3(x, 0, z), TREE_HEIGHT)
                    
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


def update_all_visibility():
    for k in list(blocks_by_key.keys()):
        update_block_and_neighbors(k)

def build_block(tex_id):
    hit_info = raycast(camera.world_position, camera.forward, distance=5)
    if hit_info.hit:
        new_pos = hit_info.entity.position + hit_info.normal
        new_ent = Block(tex_id=tex_id, model="cube", texture=b_textures[tex_id], position=new_pos, collider=None)
        if tex_id == 4:
            new_ent.model = "models/wood.obj"
            new_ent.scale = (0.5, 0.5, 0.5)
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
    show_inventory()

def create_inventory(cells_num=9):
    for i in range(cells_num):
        inv_cells.append(Entity(parent=camera.ui, model="cube", texture="textures/InventoryCell.png", position=((i-(cells_num/2))/12, -0.4, 0), scale=0.09))
        inv_blocks.append(Entity(parent=camera.ui, model="cube", position=((i-(cells_num/2))/12, -0.4, 0), texture=b_textures[i+1], scale = 0.04, rotation=(45, 45, 0)))
        if i == 3:
            inv_blocks[-1].model = "models/wood"
            inv_blocks[-1].scale = 0.02

def hide_inventory():
    global selecter
    for e in inv_cells:
        e.enabled = False
    for e in inv_blocks:
        e.enabled = False
    selecter.enabled = False

def show_inventory():
    global selecter
    for e in inv_cells:
        e.enabled = True
    for e in inv_blocks:
        e.enabled = True
    selecter.enabled = True  

def input(key):
    global tex_id, selected_item
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
        build_block(tex_id)
    if key == "1": 
        selected_item = 1
    if key == "2": 
        selected_item = 2
    if key == "3": 
        selected_item = 3
    if key == "4": 
        selected_item = 4
    if key == "5": 
        selected_item = 5
    if key == "6": 
        selected_item = 6
    if key == "7": 
        selected_item = 7
    if key == "8": 
        selected_item = 8
    if key == "9": 
        selected_item = 9
    if key == "f3":
        ticsText.enabled = not ticsText.enabled
        posText.enabled = not posText.enabled
    if key == "u":
        mouse.locked = not mouse.locked
    if key == "r":
        reset()
    if key == "h":
        hide_inventory()
    if key == "g":
        show_inventory()
    if key == "scroll down":
        selected_item = (selected_item - 1) % cells_num
    if key == "scroll up":
        selected_item = (selected_item + 1) % cells_num

ticsText = Text(text=' ', scale=2, position=(-0.75,0.4), origin=(0,0), color=color.hex("#000000"))
posText = Text(text=' ', scale=2, position=(-0.675,0.34), origin=(0,0), color=color.hex("#000000"))
ticsText.enabled = False
posText.enabled = False

def update():
    global tick, tex_id
    t = time.time() - start_time
    ticsText.text = f"Tick №{round(t*TPS)}"
    posText.text = f"POSITION: {player.X}, {player.Y}, {player.Z}"
    tick = round(t*TPS)
    tex_id = selected_item
    update_sky()
    selecter.position=inv_cells[selected_item-1].position
    if player.y < -20:
        reset()

generate_world()
generate_trees()
update_all_visibility()
create_inventory(cells_num)
hide_inventory()

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
logo = Entity(parent=camera.ui, model="cube", scale=(0.5,0.3,0.5), texture="textures/BuildAndLifeLogo.png", position=(-0.6,0.3,0))

app.run()