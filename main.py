
import os
import math
import random
import subprocess
from PIL import Image, ImageDraw, ImageFont

W, H = 540, 960
FPS = 20
DURATION = 12
OUT = "oyen_shorts.mp4"

def get_font(size):
    paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf",
    ]
    for path in paths:
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()

def draw_frame(t):
    img = Image.new("RGB", (W, H), (150, 218, 255))
    d = ImageDraw.Draw(img)

    # Langit dan bukit bergerak
    d.ellipse((350 - int(t * 3), 65, 430 - int(t * 3), 145),
              fill=(255, 224, 100))
    d.ellipse((-100 + int(t * 5), 480, 350 + int(t * 5), 850),
              fill=(102, 203, 125))
    d.ellipse((220 - int(t * 4), 530, 700 - int(t * 4), 900),
              fill=(65, 177, 108))
    d.rectangle((0, 720, W, H), fill=(96, 187, 105))

    # Rumput kecil
    for x in range(15, W, 45):
        y = 740 + (x % 4) * 12
        d.line((x, y, x - 7, y - 16), fill=(36, 133, 66), width=3)

    # Oyen melompat perlahan
    bob = int(math.sin(t * 3) * 12)
    cx, cy = 205, 640 + bob

    # Ekor
    d.ellipse((cx - 100, cy + 15, cx - 42, cy + 75),
              fill=(242, 135, 42))
    d.ellipse((cx - 91, cy + 22, cx - 55, cy + 60),
              fill=(255, 190, 90))

    # Badan dan kepala
    d.ellipse((cx - 75, cy + 15, cx + 65, cy + 145),
              fill=(244, 151, 56), outline=(160, 82, 30), width=4)
    d.ellipse((cx - 67, cy - 95, cx + 65, cy + 38),
              fill=(255, 168, 65), outline=(160, 82, 30), width=4)

    # Telinga
    d.polygon([(cx - 56, cy - 63), (cx - 52, cy - 125),
               (cx - 12, cy - 83)], fill=(244, 151, 56))
    d.polygon([(cx + 12, cy - 83), (cx + 54, cy - 125),
               (cx + 56, cy - 57)], fill=(244, 151, 56))

    # Mata dan hidung
    d.ellipse((cx - 40, cy - 52, cx - 22, cy - 28), fill="black")
    d.ellipse((cx + 20, cy - 52, cx + 38, cy - 28), fill="black")
    d.ellipse((cx - 7, cy - 21, cx + 7, cy - 9), fill=(255, 105, 130))
    d.arc((cx - 20, cy - 14, cx, cy + 8), 0, 150, fill="black", width=2)
    d.arc((cx, cy - 14, cx + 20, cy + 8), 30, 180, fill="black", width=2)

    # Telur ajaib di samping Oyen
    ex = 360 + int(math.sin(t * 2) * 9)
    ey = 675 + int(math.sin(t * 3) * 5)
    d.ellipse((ex - 48, ey - 60, ex + 48, ey + 60),
              fill=(245, 248, 255), outline=(125, 90, 220), width=4)
    d.ellipse((ex - 16, ey - 28, ex + 16, ey + 4),
              fill=(190, 150, 255))

    # Kilauan ajaib
    for i in range(5):
        sx = ex + int(math.sin(t * 2 + i) * 55)
        sy = ey + int(math.cos(t * 2 + i * 2) * 70)
        r = 4 + int((math.sin(t * 5 + i) + 1) * 3)
        d.ellipse((sx-r, sy-r, sx+r, sy+r), fill=(255, 255, 120))

    # Cerita bertahap
    if t < 4:
        caption = "OYEN MENEMUKAN TELUR AJAIB!"
    elif t < 8:
        caption = "Wah, telurnya bersinar!"
    else:
        caption = "Kira-kira apa isinya?"

    font = get_font(23)
    box = d.textbbox((0, 0), caption, font=font)
    tw = box[2] - box[0]
    d.rounded_rectangle((15, 65, W - 15, 125),
                        radius=18, fill=(255, 255, 255))
    d.text(((W - tw) // 2, 81), caption, font=font, fill=(90, 50, 130))

    return img

def main():
    os.makedirs("output", exist_ok=True)
    frames_dir = "output/frames"
    os.makedirs(frames_dir, exist_ok=True)

    for i in range(FPS * DURATION):
        frame = draw_frame(i / FPS)
        frame.save(f"{frames_dir}/frame_{i:04d}.png")

    subprocess.run([
        "ffmpeg", "-y", "-framerate", str(FPS),
        "-i", f"{frames_dir}/frame_%04d.png",
        "-c:v", "libx264", "-pix_fmt", "yuv420p",
        "-vf", "scale=540:960", OUT
    ], check=True)

    print(f"Video berhasil dibuat: {OUT}")

if __name__ == "__main__":
    main()
    
