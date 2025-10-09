from ursina import *

class Block(Entity):
    def __init__(self, tex_id, add_to_scene_entities=True, enabled=True, **kwargs):
        super().__init__(add_to_scene_entities, enabled, **kwargs)
        self.tex_id = tex_id
        if tex_id == 11:
            self.is_transparent = True
        else:
            self.is_transparent = False

class Pig(Entity):
    def __init__(self, speed, add_to_scene_entities=True, enabled=True, **kwargs):
        super().__init__(add_to_scene_entities, enabled, **kwargs)
        self.speed = speed
    
    def move(self, point: Vec3):
        direction = (point - self.position).normalized()
        self.position += direction * self.speed * time.dt
        self.look_at(point)
        self.rotation_y -= 90
        if distance(self.position, point) < 0.5:
            return "End"