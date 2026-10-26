
import asyncio
import json
import os
import random
import subprocess
from pathlib import Path

import edge_tts

ROOT = Path(__file__).parent
HISTORY = ROOT / "story_history.json"
OUTPUT = ROOT / "oyen_shorts.mp4"

STORIES = [
    {
        "id": "butterfly",
        "title": "Oyen mengejar kupu-kupu",
        "caption": "Oyen mengejar kupu-kupu!",
        "voice": "Pagi ini Oyen melihat kupu-kupu yang cantik. "
                 "Dia mengejarnya dengan penuh semangat. "
                 "Namun kupu-kupu itu terbang tinggi. "
                 "Oyen pun belajar bahwa tidak semua hal bisa dikejar."
    },
    {
        "id": "ball",
        "title": "Bola misterius",
        "caption": "Siapa yang menggerakkan bola?",
        "voice": "Oyen menemukan bola merah di lantai. "
                 "Saat disentuh, bola itu bergerak sendiri. "
                 "Oyen mundur karena terkejut. "
                 "Ternyata bola itu menggelinding karena dorongan kecilnya."
    },
    {
        "id": "fish",
        "title": "Oyen dan ikan",
        "caption": "Oyen melihat ikan!",
        "voice": "Oyen melihat ikan berenang di dalam akuarium. "
                 "Dia mendekat dengan rasa penasaran. "
                 "Ketika ikan itu bergerak cepat, Oyen ikut bergerak. "
                 "Hari ini menjadi petualangan yang lucu."
    },
    {
        "id": "gift",
        "title": "Kotak hadiah",
        "caption": "Apa isi kotak itu?",
        "voice": "Di sudut ruangan, Oyen menemukan sebuah kotak. "
                 "Dia mengendusnya lalu mendorong tutupnya. "
                 "Di dalamnya ada mainan kecil. "
                 "Oyen langsung bermain dengan gembira."
    },
    {
        "id": "bird",
        "title": "Burung di jendela",
        "caption": "Oyen bertemu burung!",
        "voice": "Seekor burung hinggap di dekat jendela. "
                 "Oyen memperhatikannya dengan mata berbinar. "
                 "Burung itu mengepakkan sayapnya lalu terbang. "
                 "Oyen masih penasaran dan menatap langit."
    },
    {
        "id": "hat",
        "title": "Topi Oyen",
        "caption": "Topi siapa ini?",
        "voice": "Oyen menemukan topi kecil yang lucu. "
                 "Dia mencoba mendekatkan kepalanya ke topi itu. "
                 "Topinya miring dan membuat Oyen terlihat kocak. "
                 "Petualangan sederhana pun menjadi menyenangkan."
    },
    {
        "id": "shadow",
        "title": "Bayangan misterius",
        "caption": "Oyen kaget melihat bayangan!",
        "voice": "Oyen melihat sesuatu bergerak di dinding. "
                 "Dia terkejut dan melompat kecil. "
                 "Ternyata itu bayangannya sendiri. "
                 "Oyen akhirnya kembali bermain dengan tenang."
    },
    {
        "id": "leaf",
        "title": "Daun yang terbang",
        "caption": "Oyen mengejar daun!",
        "voice": "Sebuah daun jatuh di depan Oyen. "
                 "Angin meniup daun itu menjauh. "
                 "Oyen berlari kecil untuk mengejarnya. "
                 "Saat daun berhenti, Oyen duduk dengan bangga."
    },
]

def read_history():
    try:
        return json.loads(HISTORY.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []

def choose_story(history):
    previous = set(history[-3:])
    choices = [s for s in STORIES if s["id"] not in previous]
    return random.choice(choices or STORIES)

async def make_voice(text):
    voice = edge_tts.Communicate(text, "id-ID-GadisNeural")
    await voice.save(str(ROOT / "oyen_voice.mp3"))

def main():
    history = read_history()
    story = choose_story(history)

    print("Cerita hari ini:", story["title"])

    env = os.environ.copy()
    env["OYEN_STORY_ID"] = story["id"]
    env["OYEN_STORY_TITLE"] = story["title"]
    env["OYEN_STORY_CAPTION"] = story["caption"]

    print("Merender adegan Blender 3D...")
    subprocess.run(
        ["blender", "--background", "--python", str(ROOT / "blender_scene.py")],
        env=env,
        check=True,
        timeout=720
    )

    print("Membuat suara bahasa Indonesia...")
    asyncio.run(make_voice(story["voice"]))

    print("Menggabungkan video dan suara...")
    subprocess.run([
        "ffmpeg", "-y",
        "-i", "/tmp/oyen_silent.mp4",
        "-i", str(ROOT / "oyen_voice.mp3"),
        "-vf",
        "drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:"
        "text='" + story["caption"] + "':"
        "fontcolor=white:fontsize=30:"
        "box=1:boxcolor=black@0.7:boxborderw=14:"
        "x=(w-text_w)/2:y=h-150",
        "-c:v", "libx264",
        "-preset", "ultrafast",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-shortest",
        "-movflags", "+faststart",
        str(OUTPUT)
    ], check=True)

    history.append(story["id"])
    HISTORY.write_text(
        json.dumps(history[-50:], ensure_ascii=False, indent=2),
        encoding="utf-8"
    )

    print("VIDEO SELESAI:", OUTPUT)

if __name__ == "__main__":
    main()
        
