
import asyncio
import json
import os
import random
import subprocess
from pathlib import Path

import edge_tts

ROOT = Path(__file__).resolve().parent
HISTORY = ROOT / "story_history.json"
OUTPUT = ROOT / "oyen_shorts.mp4"
AUDIO = ROOT / "oyen_voice.mp3"
SILENT_VIDEO = Path("/tmp/oyen_silent.mp4")

STORIES = [
    ("butterfly", "Kupu-kupu misterius", [
        ("Oyen melihat kupu-kupu cantik.", "Dia mengikutinya dengan penasaran."),
        ("Seekor kupu-kupu hinggap di dekat Oyen.", "Oyen mendekat perlahan, lalu kupu-kupu itu terbang."),
        ("Oyen mencoba mengejar kupu-kupu.", "Ternyata petualangan kecil bisa sangat menyenangkan."),
        ("Kupu-kupu kuning terbang di depan Oyen.", "Oyen melompat kecil, tetapi kupu-kupu itu lolos.")
    ]),
    ("ball", "Bola merah", [
        ("Oyen menemukan bola merah.", "Bola itu menggelinding dan membuatnya terkejut."),
        ("Oyen menyentuh sebuah bola.", "Bola itu bergerak menjauh dan Oyen mengejarnya."),
        ("Sebuah bola merah menarik perhatian Oyen.", "Dia mendorongnya lagi dan mulai bermain."),
        ("Oyen ingin menangkap bola yang bergerak.", "Bola itu berhenti tepat di depan kakinya.")
    ]),
    ("fish", "Ikan yang lincah", [
        ("Oyen melihat ikan berenang.", "Dia mengamati ikan itu dengan penuh rasa ingin tahu."),
        ("Seekor ikan bergerak cepat di akuarium.", "Oyen mengikuti gerakannya dari luar."),
        ("Oyen duduk memperhatikan ikan kecil.", "Gerakan ikan itu membuatnya terus penasaran."),
        ("Ikan kecil berenang ke sisi akuarium.", "Oyen ikut berpindah untuk melihatnya.")
    ]),
    ("gift", "Kotak misterius", [
        ("Oyen menemukan kotak kecil.", "Dia mengendusnya dan mencoba membuka tutupnya."),
        ("Sebuah kotak menarik perhatian Oyen.", "Di dekatnya ada kejutan yang belum diketahui."),
        ("Oyen mendorong kotak yang ada di lantai.", "Kotak itu bergeser dan membuatnya penasaran."),
        ("Oyen mendekati sebuah kotak hadiah.", "Dia mengamatinya seolah sedang menemukan harta karun.")
    ]),
    ("bird", "Burung di dekat jendela", [
        ("Seekor burung hinggap di dekat jendela.", "Oyen memperhatikannya dengan mata berbinar."),
        ("Oyen melihat burung kecil mengepakkan sayap.", "Burung itu terbang dan Oyen terus memandangnya."),
        ("Suara burung membuat Oyen menoleh.", "Dia mencari sumber suara itu dengan penasaran."),
        ("Burung kecil datang sebentar.", "Oyen mendekat, tetapi burung itu segera terbang.")
    ]),
    ("hat", "Topi lucu", [
        ("Oyen menemukan topi kecil.", "Topi itu membuatnya terlihat lucu."),
        ("Sebuah topi berada di dekat Oyen.", "Dia mendekat dan mencoba mengendusnya."),
        ("Oyen penasaran dengan topi berwarna merah.", "Dia menyentuhnya dan topi itu bergeser."),
        ("Topi kecil menarik perhatian Oyen.", "Oyen mencoba mendekat dengan hati-hati.")
    ]),
    ("shadow", "Bayangan misterius", [
        ("Oyen melihat bayangan bergerak.", "Dia terkejut, lalu menyadari bayangan itu miliknya."),
        ("Ada bayangan di dinding.", "Oyen menoleh dan mencoba mencari tahu asalnya."),
        ("Oyen bergerak dan bayangan ikut bergerak.", "Dia tampak bingung melihat kejadian itu."),
        ("Bayangan besar muncul di dekat Oyen.", "Setelah mengamati, dia kembali tenang.")
    ]),
    ("leaf", "Daun yang terbang", [
        ("Daun jatuh tepat di depan Oyen.", "Angin meniupnya dan Oyen mengikuti gerakannya."),
        ("Oyen melihat daun bergerak di lantai.", "Dia mendekat dan mencoba menyentuhnya."),
        ("Daun kecil tertiup angin.", "Oyen mengejarnya dengan langkah-langkah kecil."),
        ("Oyen menemukan daun berwarna hijau.", "Daun itu bergeser dan membuatnya penasaran.")
    ])
]

def read_history():
    try:
        return json.loads(HISTORY.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []

def choose_story(history):
    pool = []
    for theme, title, variations in STORIES:
        for number, pair in enumerate(variations):
            story_id = f"{theme}-{number}"
            pool.append({
                "id": story_id,
                "theme": theme,
                "title": title,
                "caption": pair[0],
                "voice": pair[0] + " " + pair[1]
            })

    used = set(history)
    available = [s for s in pool if s["id"] not in used]

    # Jika semua variasi sudah terpakai, mulai siklus baru.
    if not available:
        available = pool

    return random.choice(available)

async def make_voice(text):
    voice = edge_tts.Communicate(text, "id-ID-GadisNeural")
    await voice.save(str(AUDIO))

def main():
    history = read_history()
    story = choose_story(history)

    print("Cerita:", story["title"])
    print("Narasi:", story["voice"])

    env = os.environ.copy()
    env["OYEN_STORY_ID"] = story["theme"]
    env["OYEN_STORY_TITLE"] = story["title"]

    print("Merender animasi 3D...")
    subprocess.run(
        ["blender", "--background", "--python",
         str(ROOT / "blender_scene.py")],
        env=env,
        check=True,
        timeout=1500
    )

    if not SILENT_VIDEO.exists():
        raise FileNotFoundError("Blender tidak menghasilkan video.")

    print("Membuat suara Indonesia...")
    asyncio.run(make_voice(story["voice"]))

    print("Menggabungkan video, suara, dan teks...")
    subprocess.run([
        "ffmpeg", "-y",
        "-i", str(SILENT_VIDEO),
        "-i", str(AUDIO),
        "-vf",
        "drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:"
        "text='" + story["caption"].replace("'", r"\'") + "':"
        "fontcolor=white:fontsize=28:"
        "box=1:boxcolor=black@0.7:boxborderw=12:"
        "x=(w-text_w)/2:y=h-150,"
        "format=yuv420p",
        "-c:v", "libx264",
        "-preset", "ultrafast",
        "-c:a", "aac",
        "-b:a", "128k",
        "-shortest",
        "-movflags", "+faststart",
        str(OUTPUT)
    ], check=True)

    history.append(story["id"])
    HISTORY.write_text(
        json.dumps(history[-32:], ensure_ascii=False, indent=2),
        encoding="utf-8"
    )

    print("VIDEO SELESAI:", OUTPUT)

if __name__ == "__main__":
    main()
