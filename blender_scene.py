
import bpy
import math
import os
from mathutils import Vector

scene = bpy.context.scene
story = os.environ.get("OYEN_STORY_ID", "butterfly")
title = os.environ.get("OYEN_STORY_TITLE", "Petualangan Oyen")

bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)

scene.render.engine = "BLENDER_EEVEE_NEXT"
scene.render.resolution_x = 540
scene.render.resolution_y = 960
scene.render.resolution_percentage = 100
scene.render.fps = 18
scene.frame_start = 1
scene.frame_end = 270
scene.render.image_settings.file_format = "FFMPEG"
scene.render.ffmpeg.format = "MPEG4"
scene.render.ffmpeg.codec = "H264"
scene.render.filepath = "/tmp/oyen_silent.mp4"
scene.render.resolution_percentage = 70

def material(name, color, roughness=0.6):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1)
    m.roughness = roughness
    return m

orange = material("Oyen Orange", (1.0, 0.30, 0.045))
cream = material("Cream Fur", (1.0, 0.78, 0.48))
white = material("Eye White", (1, 0.98, 0.88))
green = material("Eye Green", (0.08, 0.38, 0.14))
black = material("Pupil", (0.012, 0.018, 0.012))
pink = material("Ear Pink", (1.0, 0.35, 0.42))
ground_mat = material("Ground", (0.12, 0.43, 0.18))
blue = material("Sky", (0.20, 0.58, 0.85))
red = material("Red Ball", (0.92, 0.04, 0.07))
yellow = material("Butterfly", (1.0, 0.78, 0.04))
brown = material("Box", (0.48, 0.23, 0.08))
silver = material("Fish", (0.65, 0.78, 0.85))

def uv(name, loc, scale, mat):
    bpy.ops.mesh.primitive_uv_sphere_add(
        segments=24, ring_count=16, location=loc
    )
    o = bpy.context.object
    o.name = name
    o.scale = scale
    bpy.ops.object.shade_smooth()
    o.data.materials.append(mat)
    return o

def cube(name, loc, scale, mat):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    o = bpy.context.object
    o.name = name
    o.dimensions = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    o.data.materials.append(mat)
    return o

# Ground and background
cube("Ground", (0, 0, -0.25), (12, 12, 0.5), ground_mat)
cube("Backdrop", (0, 3, 4), (12, 0.3, 10), blue)

# Body and head
uv("Body", (0, 0, 1.35), (0.82, 0.55, 1.0), orange)
uv("Chest", (0, -0.48, 1.3), (0.48, 0.13, 0.68), cream)
head = uv("Head", (0, -0.05, 2.75), (1.0, 0.70, 0.82), orange)

# Ears
for x in (-0.66, 0.66):
    ear = uv("Ear", (x, -0.02, 3.42), (0.34, 0.24, 0.48), orange)
    inner = uv("Inner Ear", (x, -0.235, 3.43), (0.19, 0.06, 0.29), pink)

# Eyes, pupils, highlights
for x in (-0.39, 0.39):
    uv("Eye", (x, -0.68, 2.86), (0.25, 0.13, 0.30), white)
    uv("Iris", (x + 0.03, -0.80, 2.84), (0.12, 0.07, 0.17), green)
    uv("Pupil", (x + 0.04, -0.855, 2.84), (0.055, 0.035, 0.11), black)
    uv("Eye Shine", (x + 0.01, -0.89, 2.91), (0.035, 0.02, 0.045), white)

uv("Muzzle", (0, -0.70, 2.57), (0.35, 0.16, 0.20), cream)
uv("Nose", (0, -0.86, 2.63), (0.09, 0.05, 0.07), pink)

# Legs
for x in (-0.48, 0.48):
    for y in (-0.30, 0.30):
        uv("Paw", (x, y, 0.52), (0.23, 0.28, 0.32), orange)

# Tail
tail = uv("Tail", (0.85, 0.15, 1.85), (0.22, 0.25, 0.72), orange)
tail.rotation_euler[1] = -0.65

# Props for the day's story
prop = None
if story == "butterfly":
    prop = uv("Butterfly Body", (1.4, -0.2, 2.3), (0.07, 0.06, 0.22), black)
    uv("Butterfly Wing", (1.22, -0.22, 2.4), (0.20, 0.07, 0.15), yellow)
    uv("Butterfly Wing", (1.58, -0.22, 2.4), (0.20, 0.07, 0.15), yellow)
elif story == "ball":
    prop = uv("Red Ball", (1.5, -0.2, 0.5), (0.32, 0.32, 0.32), red)
elif story == "fish":
    prop = uv("Aquarium", (1.45, 0.1, 1.7), (0.52, 0.35, 0.75), blue)
    uv("Fish", (1.45, -0.30, 1.75), (0.25, 0.12, 0.13), silver)
elif story == "gift":
    prop = cube("Gift Box", (1.4, 0, 0.55), (0.8, 0.8, 0.8), brown)
    cube("Gift Ribbon", (1.4, -0.42, 0.55), (0.12, 0.04, 0.8), yellow)
elif story == "bird":
    prop = uv("Bird Body", (1.4, 0, 2.5), (0.28, 0.20, 0.20), yellow)
    uv("Bird Wing", (1.4, -0.18, 2.56), (0.18, 0.06, 0.12), orange)
elif story == "hat":
    prop = uv("Hat Top", (0.1, -0.05, 3.7), (0.48, 0.28, 0.25), red)
    uv("Hat Brim", (0.1, -0.05, 3.56), (0.58, 0.32, 0.08), red)
elif story == "shadow":
    prop = uv("Shadow", (1.6, 0.5, 1.3), (0.5, 0.12, 1.0), black)
elif story == "leaf":
    prop = uv("Leaf", (1.4, -0.1, 0.5), (0.28, 0.08, 0.12), green)

# Simple movement animation: Oyen bobs and turns toward the prop
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

# Camera
bpy.ops.object.camera_add(location=(0, -10, 2.3))
camera = bpy.context.object
camera.name = "Shorts Camera"
camera.data.type = "ORTHO"
camera.data.ortho_scale = 5.5
camera.rotation_euler = (Vector((0, 0, 1.9)) - camera.location).to_track_quat("-Z", "Y").to_euler()
scene.camera = camera

# Lighting
bpy.ops.object.light_add(type="AREA", location=(-4, -5, 7))
key = bpy.context.object
key.data.energy = 850
key.data.shape = "DISK"
key.data.size = 5

bpy.ops.object.light_add(type="AREA", location=(4, 1, 5))
fill = bpy.context.object
fill.data.energy = 500
fill.data.size = 4

scene.world.color = (0.12, 0.12, 0.12)
scene.render.image_settings.color_mode = "RGB"
scene.render.ffmpeg.constant_rate_factor = "MEDIUM"
scene.render.ffmpeg.ffmpeg_preset = "GOOD"
scene.render.filepath = "/tmp/oyen_silent.mp4"

scene.frame_set(1)
bpy.ops.render.render(animation=True)
print("Blender video selesai:", scene.render.filepath)
