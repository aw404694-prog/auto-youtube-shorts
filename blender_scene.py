
import bpy
import math
import os
from mathutils import Vector

scene = bpy.context.scene
story = os.environ.get("OYEN_STORY_ID", "butterfly")

bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)

scene.render.engine = "BLENDER_EEVEE_NEXT"
scene.render.resolution_x = 540
scene.render.resolution_y = 960
scene.render.resolution_percentage = 70
scene.render.fps = 18
scene.frame_start = 1
scene.frame_end = 270
scene.render.image_settings.file_format = "FFMPEG"
scene.render.ffmpeg.format = "MPEG4"
scene.render.ffmpeg.codec = "H264"
scene.render.filepath = "/tmp/oyen_silent.mp4"

def mat(name, color):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1)
    m.roughness = 0.65
    return m

orange = mat("Oyen Orange", (1.0, 0.30, 0.045))
cream = mat("Cream Fur", (1.0, 0.78, 0.48))
white = mat("Eye White", (1.0, 0.98, 0.9))
green = mat("Green Iris", (0.08, 0.4, 0.14))
black = mat("Black", (0.015, 0.02, 0.015))
pink = mat("Pink", (1.0, 0.3, 0.4))
grass = mat("Grass", (0.12, 0.43, 0.18))
blue = mat("Sky", (0.2, 0.58, 0.85))
yellow = mat("Yellow", (1.0, 0.75, 0.04))
red = mat("Red", (0.9, 0.035, 0.06))
brown = mat("Brown", (0.45, 0.22, 0.08))
silver = mat("Silver", (0.65, 0.8, 0.9))

def sphere(name, loc, scale, material):
    bpy.ops.mesh.primitive_uv_sphere_add(
        segments=24, ring_count=16, location=loc
    )
    obj = bpy.context.object
    obj.name = name
    obj.scale = scale
    obj.data.materials.append(material)
    bpy.ops.object.shade_smooth()
    return obj

def cube(name, loc, scale, material):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = scale
    bpy.ops.object.transform_apply(
        location=False, rotation=False, scale=True
    )
    obj.data.materials.append(material)
    return obj

cube("Floor", (0, 0, -0.2), (12, 12, 0.4), grass)
cube("Background", (0, 3, 4), (12, 0.2, 10), blue)

# Oyen's body and face
sphere("Body", (0, 0, 1.35), (0.82, 0.55, 1.0), orange)
sphere("Chest", (0, -0.48, 1.35), (0.46, 0.13, 0.65), cream)
head = sphere("Head", (0, -0.05, 2.75), (1.0, 0.7, 0.82), orange)

for x in (-0.65, 0.65):
    sphere("Ear", (x, -0.03, 3.4), (0.34, 0.24, 0.46), orange)
    sphere("Inner Ear", (x, -0.23, 3.42), (0.18, 0.06, 0.27), pink)

for x in (-0.39, 0.39):
    sphere("Eye", (x, -0.68, 2.86), (0.25, 0.13, 0.30), white)
    sphere("Iris", (x + 0.03, -0.80, 2.84), (0.12, 0.07, 0.17), green)
    sphere("Pupil", (x + 0.04, -0.855, 2.84), (0.055, 0.035, 0.11), black)
    sphere("Eye Shine", (x + 0.01, -0.89, 2.91), (0.035, 0.02, 0.045), white)

sphere("Muzzle", (0, -0.70, 2.57), (0.35, 0.16, 0.20), cream)
sphere("Nose", (0, -0.86, 2.63), (0.09, 0.05, 0.07), pink)

for x in (-0.48, 0.48):
    for y in (-0.3, 0.3):
        sphere("Paw", (x, y, 0.52), (0.23, 0.28, 0.32), orange)

tail = sphere("Tail", (0.85, 0.15, 1.85), (0.22, 0.25, 0.72), orange)
tail.rotation_euler[1] = -0.65

# Different prop for each story theme
prop = None

if story == "butterfly":
    prop = sphere("Butterfly Body", (1.4, -0.2, 2.3), (0.07, 0.06, 0.22), black)
    sphere("Butterfly Wing", (1.2, -0.22, 2.4), (0.20, 0.07, 0.15), yellow)
    sphere("Butterfly Wing", (1.6, -0.22, 2.4), (0.20, 0.07, 0.15), yellow)

elif story == "ball":
    prop = sphere("Red Ball", (1.4, -0.2, 0.5), (0.32, 0.32, 0.32), red)

elif story == "fish":
    prop = sphere("Aquarium", (1.4, 0.1, 1.7), (0.52, 0.35, 0.75), blue)
    sphere("Fish", (1.4, -0.30, 1.75), (0.25, 0.12, 0.13), silver)

elif story == "gift":
    prop = cube("Gift Box", (1.4, 0, 0.55), (0.8, 0.8, 0.8), brown)
    cube("Gift Ribbon", (1.4, -0.42, 0.55), (0.12, 0.04, 0.8), yellow)

elif story == "bird":
    prop = sphere("Bird", (1.4, 0, 2.5), (0.28, 0.2, 0.2), yellow)
    sphere("Bird Wing", (1.4, -0.18, 2.56), (0.18, 0.06, 0.12), orange)

elif story == "hat":
    prop = sphere("Hat Top", (0.1, -0.05, 3.7), (0.48, 0.28, 0.25), red)
    sphere("Hat Brim", (0.1, -0.05, 3.56), (0.58, 0.32, 0.08), red)

elif story == "shadow":
    prop = sphere("Shadow", (1.6, 0.5, 1.3), (0.5, 0.12, 1.0), black)

elif story == "leaf":
    prop = sphere("Leaf", (1.4, -0.1, 0.5), (0.28, 0.08, 0.12), yellow)

# Animate Oyen and the main prop
for frame in range(1, 271, 9):
    scene.frame_set(frame)
    head.location.z = 2.75 + 0.08 * math.sin(frame / 12)
    head.keyframe_insert(data_path="location", frame=frame)

    tail.rotation_euler[1] = -0.65 + 0.25 * math.sin(frame / 10)
    tail.keyframe_insert(data_path="rotation_euler", frame=frame)

if prop:
    start = prop.location.copy()
    for frame in (1, 90, 180, 270):
        scene.frame_set(frame)
        prop.location.z = start.z + 0.12 * math.sin(frame / 14)
        prop.keyframe_insert(data_path="location", frame=frame)

# Vertical camera
bpy.ops.object.camera_add(location=(0, -10, 2.3))
camera = bpy.context.object
camera.data.type = "ORTHO"
camera.data.ortho_scale = 5.5
camera.rotation_euler = (
    Vector((0, 0, 1.9)) - camera.location
).to_track_quat("-Z", "Y").to_euler()
scene.camera = camera

# Lighting
bpy.ops.object.light_add(type="AREA", location=(-4, -5, 7))
bpy.context.object.data.energy = 850
bpy.context.object.data.shape = "DISK"
bpy.context.object.data.size = 5

bpy.ops.object.light_add(type="AREA", location=(4, 1, 5))
bpy.context.object.data.energy = 500
bpy.context.object.data.size = 4

scene.world.color = (0.12, 0.12, 0.12)
scene.render.ffmpeg.constant_rate_factor = "MEDIUM"
scene.render.ffmpeg.ffmpeg_preset = "GOOD"
scene.frame_set(1)

bpy.ops.render.render(animation=True)
print("Render selesai:", scene.render.filepath)
        
