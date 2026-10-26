
import bpy
import math
from mathutils import Vector

# Bersihkan scene
bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)

# Pengaturan render vertikal
scene = bpy.context.scene
scene.render.engine = "CYCLES"
scene.cycles.samples = 16
scene.render.resolution_x = 540
scene.render.resolution_y = 960
scene.render.resolution_percentage = 100
scene.render.fps = 24
scene.frame_end = 120
scene.render.image_settings.file_format = "FFMPEG"
scene.render.ffmpeg.format = "MPEG4"
scene.render.filepath = "/tmp/oyen_3d.mp4"
scene.world.color = (0.08, 0.08, 0.08)

# Material
def material(name, color, roughness=0.7):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (*color, 1)
    mat.use_nodes = True
    mat.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (*color, 1)
    mat.node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value = roughness
    return mat

orange = material("Bulu Oyen - jingga", (1.0, 0.28, 0.035))
cream = material("Bulu krem", (1.0, 0.77, 0.48))
white = material("Putih mata", (1.0, 0.95, 0.85))
black = material("Hitam", (0.025, 0.015, 0.01))
pink = material("Hidung merah muda", (1.0, 0.22, 0.32))
green = material("Mata hijau", (0.25, 0.75, 0.25))
ground = material("Lantai", (0.16, 0.32, 0.18))

def ball(name, loc, scale, mat):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=24, ring_count=16, location=loc)
    obj = bpy.context.object
    obj.name = name
    obj.scale = scale
    obj.data.materials.append(mat)
    bpy.ops.object.shade_smooth()
    return obj

# Badan dan kepala
body = ball("Badan Oyen", (0, 0, 1.0), (0.62, 0.42, 0.78), orange)
head = ball("Kepala Oyen", (0, -0.12, 2.0), (0.72, 0.52, 0.62), orange)

# Pipi
ball("Pipi kiri", (-0.29, -0.58, 1.82), (0.27, 0.12, 0.19), cream)
ball("Pipi kanan", (0.29, -0.58, 1.82), (0.27, 0.12, 0.19), cream)

# Mata besar
for x in (-0.27, 0.27):
    ball("Bola mata", (x, -0.585, 2.12), (0.20, 0.10, 0.25), white)
    ball("Iris hijau", (x, -0.68, 2.11), (0.105, 0.055, 0.16), green)
    ball("Pupil", (x, -0.725, 2.11), (0.045, 0.025, 0.105), black)
    ball("Kilau mata", (x-0.035, -0.75, 2.18), (0.035, 0.018, 0.045), white)

# Hidung dan moncong
ball("Moncong", (0, -0.65, 1.83), (0.22, 0.12, 0.14), cream)
ball("Hidung", (0, -0.78, 1.91), (0.075, 0.045, 0.05), pink)

# Telinga berbentuk kerucut
for x in (-0.48, 0.48):
    bpy.ops.mesh.primitive_cone_add(vertices=32, radius1=0.28, radius2=0.035,
                                    depth=0.62, location=(x, -0.05, 2.52))
    ear = bpy.context.object
    ear.name = "Telinga Oyen"
    ear.data.materials.append(orange)
    ear.rotation_euler[1] = -x * 0.55
    bpy.ops.object.shade_smooth()

# Kaki
for x in (-0.38, 0.38):
    for y in (-0.23, 0.25):
        ball("Kaki Oyen", (x, y, 0.43), (0.22, 0.24, 0.27), orange)

# Ekor melengkung sederhana
tail = ball("Pangkal ekor", (0.58, 0.22, 1.12), (0.20, 0.22, 0.24), orange)
tail2 = ball("Ekor", (0.82, 0.22, 1.42), (0.16, 0.17, 0.38), orange)
tail2.rotation_euler[1] = -0.55
tail3 = ball("Ujung ekor", (0.72, 0.22, 1.68), (0.15, 0.16, 0.20), orange)

# Lantai
bpy.ops.mesh.primitive_plane_add(size=200, location=(0, 0, 0.12))
floor = bpy.context.object
floor.name = "Lantai hijau"
floor.data.materials.append(ground)

# Kamera
bpy.ops.object.camera_add(location=(3.8, -8.5, 2.7))
camera = bpy.context.object
camera.rotation_euler = (Vector((0, 0, 1.45)) - camera.location).to_track_quat("-Z", "Y").to_euler()
camera.data.type = "ORTHO"
camera.data.ortho_scale = 4.5
scene.camera = camera

# Pencahayaan
for loc, power, size in [
    ((-3, -4, 6), 550, 4),
    ((4, 1, 5), 350, 3),
    ((0, -2, 4), 180, 2)
]:
    bpy.ops.object.light_add(type="AREA", location=loc)
    light = bpy.context.object
    light.data.energy = power
    light.data.shape = "DISK"
    light.data.size = size
    light.rotation_euler = (Vector((0, 0, 1.4)) - light.location).to_track_quat("-Z", "Y").to_euler()

# Gerakan badan naik-turun dan kepala mengangguk
for frame in range(1, 121):
    scene.frame_set(frame)
    body.location.z = 1.0 + 0.035 * math.sin(frame * 0.12)
    body.keyframe_insert(data_path="location", frame=frame)
    head.rotation_euler[1] = 0.035 * math.sin(frame * 0.09)
    head.keyframe_insert(data_path="rotation_euler", frame=frame)
    tail2.rotation_euler[1] = -0.55 + 0.12 * math.sin(frame * 0.13)
    tail2.keyframe_insert(data_path="rotation_euler", frame=frame)

# Render lebih ringan untuk GitHub Actions
scene.render.engine = "BLENDER_EEVEE_NEXT"
scene.view_settings.view_transform = "Standard"
scene.view_settings.look = "Medium High Contrast"
scene.camera.data.lens = 50

# Simpan proyek dan render video
bpy.ops.wm.save_as_mainfile(filepath="/tmp/oyen_3d.blend")
bpy.ops.render.render(animation=True)
