
import asyncio
import math
import os
import subprocess
from PIL import Image, ImageDraw, ImageFont
import edge_tts

W, H = 540, 960
FPS = 20
DURATION = 15
OUT = "oyen_shorts.mp4"

NARRATION = (
    "Suatu pagi, Oyen menemukan sebuah telur misterius "
    "di tengah taman. Telur itu tiba-tiba bersinar! "
    "Oyen mendekat dengan penasaran. "
    "Tiba-tiba, terdengar suara dari dalam telur. "
    "Kira-kira, makhluk apa yang akan menetas?"
)

SCENES = [
    (0, 4, "Oyen menemukan telur misterius!"),
    (4, 8, "Telurnya mulai bersinar!"),
    (8, 12, "Ada suara dari dalam telur!"),
    (12, 15, "Apa yang akan menetas?"),
]

def font(size):
    paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf",
    ]
    for p in paths:
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()

def draw_frame(t):
    im = Image.new("RGB", (W, H), (130, 196, 239))
    d = ImageDraw.Draw(im)

    # Langit, awan, matahari, dan bukit
    d.ellipse((370, 90, 450, 170), fill=(255, 226, 125))
    for x in [45, 270, 470]:
        xx = (x + int(t * 9)) % 650 - 70
        d.ellipse((xx, 170, xx + 100, 210), fill=(245, 250, 255))
        d.ellipse((xx + 25, 145, xx + 75, 205), fill=(245, 250, 255))

    d.ellipse((-180, 440, 390, 810), fill=(88, 170, 112))
    d.ellipse((190, 480, 760, 840), fill=(60, 147, 91))
    d.rectangle((0, 680, W, H), fill=(76, 155, 79))

    # Gerakan rumput
    for x in range(12, W, 32):
        y = 730 + (x % 5) * 20
        sway = int(math.sin(t * 3 + x) * 5)
        d.line((x, y, x + sway, y - 17), fill=(36, 111, 59), width=3)

    # Oyen: badan, ekor, kepala, dan telinga
    bob = int(math.sin(t * 3) * 8)
    cx, cy = 190, 625 + bob

    tail_sway = int(math.sin(t * 4) * 16)
    d.ellipse((cx - 105, cy + 35, cx - 42, cy + 82 + tail_sway),
              fill=(226, 119, 38), outline=(143, 71, 27), width=3)
    d.ellipse((cx - 65, cy + 35, cx + 53, cy + 158),
              fill=(239, 139, 48), outline=(143, 71, 27), width=3)
    d.ellipse((cx - 61, cy - 87, cx + 63, cy + 38),
              fill=(244, 155, 57), outline=(143, 71, 27), width=3)

    d.polygon([(cx-54, cy-58), (cx-49, cy-118), (cx-9, cy-78)],
              fill=(239, 139, 48), outline=(143, 71, 27))
    d.polygon([(cx+8, cy-78), (cx+50, cy-118), (cx+55, cy-55)],
              fill=(239, 139, 48), outline=(143, 71, 27))
    d.polygon([(cx-43, cy-68), (cx-42, cy-101), (cx-20, cy-76)],
              fill=(246, 173, 174))
    d.polygon([(cx+20, cy-76), (cx+43, cy-101), (cx+43, cy-65)],
              fill=(246, 173, 174))

    # Mata berkedip
    blink = (int(t * 2) % 7 == 0 and t % 1 < 0.12)
    if blink:
        d.line((cx-37, cy-39, cx-19, cy-39), fill=(45, 35, 27), width=4)
        d.line((cx+20, cy-39, cx+38, cy-39), fill=(45, 35, 27), width=4)
    else:
        d.ellipse((cx-36, cy-48, cx-19, cy-25), fill=(35, 29, 25))
        d.ellipse((cx+20, cy-48, cx+37, cy-25), fill=(35, 29, 25))
        d.ellipse((cx-32, cy-44, cx-26, cy-37), fill="white")
        d.ellipse((cx+24, cy-44, cx+30, cy-37), fill="white")

    d.ellipse((cx-7, cy-19, cx+7, cy-9), fill=(237, 99, 123))
    d.arc((cx-15, cy-12, cx, cy+8), 0, 150, fill=(65, 35, 28), width=2)
    d.arc((cx, cy-12, cx+15, cy+8), 30, 180, fill=(65, 35, 28), width=2)
    d.ellipse((cx-47, cy-16, cx-31, cy-7), fill=(255, 174, 155))
    d.ellipse((cx+32, cy-16, cx+48, cy-7), fill=(255, 174, 155))

    # Telur ajaib bergoyang dan bersinar
    ex = 370 + int(math.sin(t * 2.3) * 8)
    ey = 665 + int(math.sin(t * 3) * 5)
    glow = int((math.sin(t * 5) + 1) * 25)
    d.ellipse((ex-63-glow//3, ey-75-glow//3,
               ex+63+glow//3, ey+75+glow//3),
              fill=(255, 235, 146))
    d.ellipse((ex-43, ey-62, ex+43, ey+62),
              fill=(250, 250, 255), outline=(145, 111, 220), width=4)
    d.ellipse((ex-15, ey-30, ex+15, ey),
              fill=(191, 155, 247))

    # Kilauan
    for i in range(8):
        a = t * 1.8 + i * math.pi / 4
        sx = ex + int(math.cos(a) * 60)
        sy = ey + int(math.sin(a) * 75)
        r = 2 + int((math.sin(t * 6 + i) + 1) * 2)
        d.ellipse((sx-r, sy-r, sx+r, sy+r), fill=(255, 255, 190))

    # Subtitle cerita
    caption = next(text for start, end, text in SCENES if start <= t < end)
    f = font(23)
    box = d.textbbox((0, 0), caption, font=f)
    tw = box[2] - box[0]
    d.rounded_rectangle((14, 65, W-14, 128), radius=18,
                        fill=(255, 255, 255))
    d.text(((W-tw)//2, 83), caption, font=f, fill=(68, 45, 110))

    return im

async def make_voice():
    voice = edge_tts.Communicate(
        NARRATION,
        voice="id-ID-GadisNeural",
        rate="+0%",
        volume="+0%"
    )
    await voice.save("narration.mp3")

def main():
    os.makedirs("frames", exist_ok=True)

    asyncio.run(make_voice())

    total = FPS * DURATION
    for i in range(total):
        draw_frame(i / FPS).save(f"frames/frame_{i:04d}.png")

    subprocess.run([
        "ffmpeg", "-y",
        "-framerate", str(FPS),
        "-i", "frames/frame_%04d.png",
        "-i", "narration.mp3",
        "-map", "0:v:0", "-map", "1:a:0",
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-shortest",
        "-movflags", "+faststart",
        OUT
    ], check=True)

    print(f"Video dengan narasi berhasil dibuat: {OUT}")

if __name__ == "__main__":
    main()
