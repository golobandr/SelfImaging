from yt_dlp import YoutubeDL

# Link do filmu z YouTube
video_url = "https://www.youtube.com/watch?v=1csFTDXXULY"

# Opcje pobierania i konwersji do MP3
options = {
    'format': 'bestaudio/best',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
    'outtmpl': '%(title)s.%(ext)s',
}

# Pobieranie pliku
with YoutubeDL(options) as ydl:
    ydl.download([video_url])