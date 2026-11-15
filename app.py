import os
import tempfile
from flask import Flask, request, send_file, render_template_string

app = Flask(__name__)

HTML = """
<!DOCTYPE html>
<html lang="ro">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Video Downloader</title>
<style>
body {
    background: #111827;
    color: white;
    font-family: Arial;
    text-align: center;
    padding: 40px 15px;
}
.container {
    max-width: 500px;
    margin: auto;
    background: #1f2937;
    padding: 25px;
    border-radius: 15px;
}
input, select, button {
    width: 100%;
    padding: 14px;
    margin-top: 15px;
    border: 0;
    border-radius: 8px;
    box-sizing: border-box;
    font-size: 16px;
}
button {
    background: #ef4444;
    color: white;
    font-weight: bold;
    cursor: pointer;
}
</style>
</head>
<body>
<div class="container">
<h1>Video Downloader</h1>
<p>Descarcă videoclipuri pe care ai dreptul să le salvezi.</p>
<form action="/download" method="POST">
<input name="url" type="url" placeholder="Introdu linkul video" required>
<select name="format">
<option value="mp4">MP4 - Video</option>
<option value="mp3">MP3 - Audio</option>
</select>
<button type="submit">DESCARCĂ</button>
</form>
</div>
</body>
</html>
"""

@app.route("/", methods=["GET"])
def home():
    return render_template_string(HTML)

@app.route("/download", methods=["POST"])
def download():
    url = request.form.get("url", "").strip()
    fmt = request.form.get("format", "mp4")

    if not url.startswith(("http://", "https://")):
        return "Link invalid", 400

    import yt_dlp

    folder = tempfile.mkdtemp()

    options = {
        "outtmpl": os.path.join(folder, "%(title).100s.%(ext)s"),
        "noplaylist": True,
        "quiet": True,
    }

    if fmt == "mp3":
        options["format"] = "bestaudio/best"
        options["postprocessors"] = [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",
        }]
        options["ffmpeg_location"] = __import__("imageio_ffmpeg").get_ffmpeg_exe()
    else:
        options["format"] = "best"

    try:
        with yt_dlp.YoutubeDL(options) as ydl:
            ydl.download([url])

        files = os.listdir(folder)
        if not files:
            return "Nu s-a putut descărca fișierul.", 500

        filepath = os.path.join(folder, files[0])

        return send_file(
            filepath,
            as_attachment=True,
            download_name=os.path.basename(filepath)
        )

    except Exception as e:
        return "Descărcarea a eșuat: " + str(e), 500
