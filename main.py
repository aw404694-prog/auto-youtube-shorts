
import os
import random
import asyncio
import textwrap
import subprocess
from pathlib import Path

import edge_tts
from PIL import Image, ImageDraw, ImageFont

OUTPUT = Path("output")
OUTPUT.mkdir(exist_ok=True)

FACTS = [
    {
        "title": "Fakta unik tentang gurita",
        "text": "Gurita memiliki tiga jantung. Dua memompa darah ke insang, dan satu memompa darah ke seluruh tubuh.",
    },
    {
        "title": "Fakta unik tentang luar angkasa",
        "text": "Di Venus, satu hari lebih lama daripada satu tahunnya. Venus berputar sangat lambat pada porosnya.",
    },
    {
        "title": "Fakta unik tentang lebah",
        "text": "Lebah madu berkomunikasi dengan gerakan tarian untuk memberi tahu lebah lain lokasi sumber makanan.",
    },
    {
        "title": "Fakta unik tentang hiu",
        "text": "Hiu sudah hidup di Bumi jauh sebelum dinosaurus muncul.",
    },
    {
        "title": "Fakta unik tentang jerapah",
        "text": "Pola bercak pada setiap jerapah memiliki bentuk yang unik, seperti pola sidik jari.",
    },
]

VOICE = "id-ID-ArdiNeural"


def create_image(fact, image_path):
    image = Image.new("RGB", (720, 1280), (12, 24, 52))
    draw = ImageDraw.Draw(image)

    font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    bold_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

    title_font = ImageFont.truetype(bold_path, 44)
    body_font = ImageFont.truetype(font_path, 34)
    footer_font = ImageFont.truetype(bold_path, 25)

    draw.rounded_rectangle(
        (35, 180, 685, 1100),
        radius=35,
        fill=(25, 43, 79),
        outline=(90, 180, 255),
        width=3,
    )

    draw.text(
        (65, 235),
        "FAKTA UNIK",
        font=footer_font,
        fill=(90, 220, 255),
    )

    title_lines = textwrap.wrap(fact["title"], width=23)
    y = 320
    for line in title_lines:
        draw.text((65, y), line, font=title_font, fill="white")
        y += 62

    y += 45
    words = fact["text"].split()
    lines = []
    current = ""

    for word in words:
        candidate = f"{current} {word}".strip()
        if draw.textbbox((0, 0), candidate, font=body_font)[2] > 560:
            lines.append(current)
            current = word
        else:
            current = candidate

    if current:
        lines.append(current)

    for line in lines:
        draw.text((65, y), line, font=body_font, fill=(225, 235, 250))
        y += 52

    draw.text(
        (65, 1015),
        "TAMBAH WAWASANMU!",
        font=footer_font,
        fill=(255, 210, 80),
    )

    image.save(image_path)


async def create_voice(text, audio_path):
    communicate = edge_tts.Communicate(
        text=text,
        voice=VOICE,
        rate="+0%",
    )
    await communicate.save(str(audio_path))


def create_video(image_path, audio_path, video_path):
    command = [
        "ffmpeg", "-y",
        "-loop", "1",
        "-i", str(image_path),
        "-i", str(audio_path),
        "-vf", "scale=720:1280,format=yuv420p",
        "-c:v", "libx264",
        "-tune", "stillimage",
        "-c:a", "aac",
        "-b:a", "128k",
        "-shortest",
        "-movflags", "+faststart",
        str(video_path),
    ]

    subprocess.run(command, check=True)

    if not video_path.exists() or video_path.stat().st_size == 0:
        raise RuntimeError("Video tidak berhasil dibuat.")


def upload_to_youtube(video_path, title, description):
    client_id = os.getenv("YT_CLIENT_ID")
    client_secret = os.getenv("YT_CLIENT_SECRET")
    refresh_token = os.getenv("YT_REFRESH_TOKEN")

    if not all([client_id, client_secret, refresh_token]):
        print("Upload dilewati: Secret YouTube API belum lengkap.")
        return

    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaFileUpload

    credentials = Credentials(
        token=None,
        refresh_token=refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=client_id,
        client_secret=client_secret,
        scopes=["https://www.googleapis.com/auth/youtube.upload"],
    )
    credentials.refresh(Request())

    youtube = build(
        "youtube", "v3",
        credentials=credentials,
        cache_discovery=False,
    )

    request = youtube.videos().insert(
        part="snippet,status",
        body={
            "snippet": {
                "title": title[:100],
                "description": description,
                "tags": ["fakta unik", "shorts", "pengetahuan"],
                "categoryId": "27",
            },
            "status": {
                "privacyStatus": os.getenv(
                    "YT_PRIVACY_STATUS", "unlisted"
                ),
                "selfDeclaredMadeForKids": False,
            },
        },
        media_body=MediaFileUpload(
            str(video_path),
            mimetype="video/mp4",
            resumable=True,
        ),
    )

    result = request.execute()
    print("Upload berhasil:", result["id"])
    print("Link: https://www.youtube.com/watch?v=" + result["id"])


def main():
    fact = random.choice(FACTS)
    title = fact["title"] + " #Shorts"

    image_path = OUTPUT / "background.jpg"
    audio_path = OUTPUT / "narration.mp3"
    video_path = OUTPUT / "fakta_unik.mp4"

    narration = fact["title"] + ". " + fact["text"]

    print("Membuat gambar...")
    create_image(fact, image_path)

    print("Membuat narasi...")
    asyncio.run(create_voice(narration, audio_path))

    print("Membuat video...")
    create_video(image_path, audio_path, video_path)

    print("Video berhasil dibuat:", video_path)

    description = (
        fact["text"]
        + "\n\n#Shorts #FaktaUnik #Pengetahuan"
    )
    upload_to_youtube(video_path, title, description)


if __name__ == "__main__":
    main()
    
