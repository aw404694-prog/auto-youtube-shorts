
import os
import random
import subprocess
from pathlib import Path

import requests
import edge_tts
from PIL import Image, ImageDraw, ImageFont

OUTPUT = Path("output")
OUTPUT.mkdir(exist_ok=True)

FACTS = [
    {
        "title": "Gurita Punya Tiga Jantung!",
        "text": "Tahukah kamu? Gurita memiliki tiga jantung. Dua memompa darah menuju insang, dan satu lagi mengalirkan darah ke seluruh tubuh."
    },
    {
        "title": "Madu Bisa Bertahan Lama",
        "text": "Madu yang disimpan dengan benar dapat bertahan sangat lama karena kadar airnya rendah dan sifatnya menghambat pertumbuhan banyak mikroba."
    },
    {
        "title": "Sehari di Venus Sangat Lama",
        "text": "Venus berputar sangat lambat. Satu putaran pada porosnya memerlukan sekitar 243 hari Bumi, lebih lama daripada satu tahunnya."
    }
]

async def make_voice(text, path):
    voice = edge_tts.Communicate(
        text, voice="id-ID-ArdiNeural"
    )
    await voice.save(str(path))

def make_video(fact):
    image_path = OUTPUT / "background.png"
    audio_path = OUTPUT / "voice.mp3"
    video_path = OUTPUT / "short.mp4"

    image = Image.new("RGB", (720, 1280), "#10182b")
    draw = ImageDraw.Draw(image)

    try:
        font_big = ImageFont.truetype(
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            54
        )
        font_small = ImageFont.truetype(
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            34
        )
    except OSError:
        font_big = ImageFont.load_default()
        font_small = ImageFont.load_default()

    draw.text((45, 230), "FAKTA UNIK", font=font_small,
              fill="#ffd166")
    draw.text((45, 340), fact["title"], font=font_big,
              fill="white", width=620)
    draw.text((45, 590), fact["text"], font=font_small,
              fill="#dce6f7", width=620)

    image.save(image_path)

    import asyncio
    asyncio.run(make_voice(
        fact["title"] + ". " + fact["text"],
        audio_path
    ))

    subprocess.run([
        "ffmpeg", "-y",
        "-loop", "1", "-i", str(image_path),
        "-i", str(audio_path),
        "-c:v", "libx264", "-tune", "stillimage",
        "-c:a", "aac", "-b:a", "128k",
        "-pix_fmt", "yuv420p", "-shortest",
        "-vf", "scale=720:1280",
        str(video_path)
    ], check=True)

    print(f"Video siap: {video_path}")

if __name__ == "__main__":
    fact = random.choice(FACTS)
    make_video(fact)
  
