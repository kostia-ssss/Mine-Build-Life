from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController

app = Ursina()

skybox_image = load_texture("textures/DaySky.png")
sky = Sky(texture=skybox_image)

start_time = 0
WORLD_SIZE = (10, 5, 10)
VIEW_SIZE = 10
BUILD_DIST = 5
TPS = 50
tex = "textures/Grass.png"
tick = 0

b_textures = {
    1: load_texture("textures/Grass.png"),
    2: load_texture("textures/Stone.png"),
    3: load_texture("textures/Brick.png"),
    4: load_texture("textures/Wood.png"),
    5: load_texture("textures/Ground.png"),
}

def generate():
    for x in range(WORLD_SIZE[0]):
        for y in range(WORLD_SIZE[1]):
            for z in range(WORLD_SIZE[2]):
                if y == 0:
                    blocks.append(Entity(model="cube", texture=b_textures[1], position=(x, -y, z), collider="box"))
                elif y > 0 and y < 4:
                    blocks.append(Entity(model="cube", texture=b_textures[5], position=(x, -y, z), collider="box"))
                elif y >= 4:
                    blocks.append(Entity(model="cube", texture=b_textures[2], position=(x, -y, z), collider="box"))

def build_block():
    hit_info = raycast(camera.world_position, camera.forward, distance=5)
    if hit_info.hit:
        blocks.append(Entity(model="cube", texture=tex, position=hit_info.entity.position + hit_info.normal, collider="box"))

def render_blocks():
    for block in blocks:
        if distance(player, block) > VIEW_SIZE:
            block.enabled = False
        else:
            if player.rotation_y < 90 and player.rotation_y > -90:
                if block.position.y < player.position.y:
                    block.enabled = False
                else:
                    block.enabled = True
            else:
                if block.position.y < player.position.y:
                    block.enabled = True
                else:
                    block.enabled = False

def update_sky():
    if tick%2000 <= 1000:
        sky.texture = load_texture("textures/DaySky.png")
    else:
        sky.texture = load_texture("textures/NightSky.png")

def destroy_block():
    hit_info = raycast(camera.world_position, camera.forward, distance=5)
    if hit_info.hit:
        blocks.remove(hit_info.entity)   
        destroy(hit_info.entity)

def reset():
    player.position = (5, 5, 5)

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
        tex = b_textures[1]

    if key == "2":
        tex = b_textures[2]

    if key == "3":
        tex = b_textures[3]

    if key == "4":
        tex = b_textures[4]
    
    if key == "5":
        tex = b_textures[5]
    
    if key == "f3":
        ticsText.enabled = not ticsText.enabled

ticsText = Text(
    text=' ',
    scale=2,
    position=(-0.75, 0.4),
    origin=(0, 0),
    color=color.hex("#000000")
)
ticsText.enabled = False

def update():
    global tick
    t = time.time()-start_time
    ticsText.text = f"Tick №{round(t*TPS)}"
    tick = round(t*TPS)
    # render_blocks()
    update_sky()
    if player.Y < -20:
        reset()

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