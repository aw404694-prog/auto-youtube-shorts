
import asyncio
import math
import os
import subprocess
from pathlib import Path

import edge_tts
from PIL import Image, ImageDraw, ImageFont

OUT = Path("oyen_shorts.mp4")
FRAMES = Path("oyen_frames")
AUDIO = Path("oyen_voice.mp3")

W, H = 540, 960
FPS = 18
DURATION = 15
TOTAL = FPS * DURATION

NARRATION = (
    "Ini Oyen. Hari ini, Oyen menemukan sebuah telur kecil. "
    "Dia menjaganya dengan penuh rasa penasaran. "
    "Tiba-tiba, telur itu bergerak! Oyen kaget, lalu mendekat. "
    "Ternyata, petualangan kecilnya baru saja dimulai."
)

def font(size):
    for name in [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf",
    ]:
        if os.path.exists(name):
            return ImageFont.truetype(name, size)
    return ImageFont.load_default()

def make_frame(i):
    t = i / FPS
    im = Image.new("RGB", (W, H), (155, 218, 250))
    d = ImageDraw.Draw(im)

    # Langit dan awan
    d.ellipse((35 + int(t * 5) % 100, 100, 155 + int(t * 5) % 100, 155),
              fill=(245, 251, 255))
    d.ellipse((90 + int(t * 5) % 100, 90, 190 + int(t * 5) % 100, 155),
              fill=(245, 251, 255))
    d.ellipse((350, 180, 430, 225), fill=(245, 251, 255))
    d.ellipse((390, 160, 475, 225), fill=(245, 251, 255))

    # Rumput
    d.rectangle((0, 680, W, H), fill=(90, 183, 91))
    d.ellipse((-120, 620, 650, 820), fill=(112, 198, 100))

    # Gerakan Oyen
    bob = int(math.sin(t * 3) * 8)
    cx, cy = 270, 530 + bob

    # Bayangan
    d.ellipse((cx-125, 680, cx+125, 720), fill=(66, 142, 73))

    # Ekor
    d.line(
        [(cx+75, cy+100), (cx+130, cy+65),
         (cx+145, cy+15 + int(math.sin(t*4)*12))],
        fill=(224, 105, 29), width=35
    )
    d.ellipse((cx+120, cy-5 + int(math.sin(t*4)*12),
               cx+166, cy+40 + int(math.sin(t*4)*12)),
              fill=(255, 148, 47))

    # Badan dan perut
    d.ellipse((cx-100, cy+30, cx+100, cy+205), fill=(239, 125, 37))
    d.ellipse((cx-55, cy+75, cx+55, cy+190), fill=(255, 218, 166))

    # Kaki
    for x in (cx-65, cx+35):
        d.ellipse((x, cy+165, x+65, cy+220), fill=(239, 125, 37))

    # Kepala dan telinga
    d.polygon([(cx-90,cy-40),(cx-80,cy-135),(cx-20,cy-70)],
              fill=(239, 125, 37))
    d.polygon([(cx+20,cy-70),(cx+80,cy-135),(cx+90,cy-40)],
              fill=(239, 125, 37))
    d.polygon([(cx-72,cy-76),(cx-70,cy-113),(cx-43,cy-80)],
              fill=(255, 178, 160))
    d.polygon([(cx+43,cy-80),(cx+70,cy-113),(cx+72,cy-76)],
              fill=(255, 178, 160))

    d.ellipse((cx-105,cy-100,cx+105,cy+90), fill=(255, 153, 53))

    # Garis belang
    for x in (-55, 0, 55):
        d.arc((cx+x-20,cy-100,cx+x+20,cy-35), 190, 340,
              fill=(180, 77, 24), width=9)

    # Mata besar dengan kilau
    look = int(math.sin(t*1.4)*5)
    for x in (cx-43, cx+43):
        d.ellipse((x-24,cy-35,x+24,cy+25), fill=(255,255,245))
        d.ellipse((x-10+look,cy-20,x+12+look,cy+18), fill=(48,116,62))
        d.ellipse((x-4+look,cy-13,x+5+look,cy+9), fill=(20,25,20))
        d.ellipse((x-4,cy-18,x+3,cy-10), fill="white")

    # Pipi dan hidung
    d.ellipse((cx-78,cy+15,cx-38,cy+38), fill=(255,174,156))
    d.ellipse((cx+38,cy+15,cx+78,cy+38), fill=(255,174,156))
    d.polygon([(cx-12,cy+17),(cx+12,cy+17),(cx,cy+30)],
              fill=(245,95,111))
    d.arc((cx-15,cy+22,cx,cy+43), 0, 120, fill=(95,48,36), width=3)
    d.arc((cx,cy+22,cx+15,cy+43), 60, 180, fill=(95,48,36), width=3)

    # Telur kecil
    eggx = 150 + int(math.sin(t*1.5)*5)
    d.ellipse((eggx-33, 665, eggx+33, 750), fill=(255,248,225),
              outline=(225,210,175), width=3)

    # Judul
    d.rounded_rectangle((35, 40, 505, 105), radius=22, fill=(255,255,255))
    d.text((270, 72), "PETUALANGAN OYEN",
           font=font(25), fill=(168,82,24), anchor="mm")

    # Subtitle
    if t < 3:
        caption = "Ini Oyen!"
    elif t < 6:
        caption = "Dia menemukan telur kecil."
    elif t < 9:
        caption = "Eh, telurnya bergerak!"
    elif t < 12:
        caption = "Oyen jadi penasaran."
    else:
        caption = "Petualangannya baru dimulai!"

    d.rounded_rectangle((28, 815, 512, 900), radius=20, fill=(30,35,42))
    d.text((270, 857), caption, font=font(22),
           fill="white", anchor="mm")

    return im

async def create_voice():
    communicate = edge_tts.Communicate(
        NARRATION, "id-ID-GadisNeural"
    )
    await communicate.save(str(AUDIO))

def main():
    FRAMES.mkdir(exist_ok=True)

    print("Membuat narasi bahasa Indonesia...")
    asyncio.run(create_voice())

    print("Menggambar animasi Oyen...")
    for i in range(TOTAL):
        frame = make_frame(i)
        frame.save(FRAMES / f"frame_{i:04d}.png")
        if i % 45 == 0:
            print(f"Frame {i}/{TOTAL}")

    print("Menggabungkan gambar dan suara...")
    subprocess.run([
        "ffmpeg", "-y",
        "-framerate", str(FPS),
        "-i", str(FRAMES / "frame_%04d.png"),
        "-i", str(AUDIO),
        "-vf", "scale=540:960,format=yuv420p",
        "-c:v", "libx264",
        "-preset", "ultrafast",
        "-c:a", "aac",
        "-b:a", "128k",
        "-shortest",
        "-movflags", "+faststart",
        str(OUT)
    ], check=True)

    print(f"VIDEO SELESAI: {OUT}")

if __name__ == "__main__":
    main()
