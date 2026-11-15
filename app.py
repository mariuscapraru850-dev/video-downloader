import os
import tempfile
import subprocess
import imageio_ffmpeg

from flask import Flask, request, send_file, render_template_string

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 500 * 1024 * 1024

PAGE = """
<!DOCTYPE html>
<html lang="ro">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Video Downloader</title>
<style>
*{box-sizing:border-box}
body{
 margin:0;background:#101827;color:white;font-family:Arial;
 min-height:100vh;display:flex;justify-content:center;
 align-items:center;padding:20px
}
.container{width:100%;max-width:650px;text-align:center}
.logo{font-size:35px;font-weight:800;margin-bottom:12px}
.logo span{color:#ff4545}
.subtitle{color:#aab5c5;margin-bottom:30px}
.panel{background:#1c293b;padding:28px;border-radius:18px}
input,select,button{
 width:100%;padding:16px;border-radius:10px;
 border:0;margin-top:13px;font-size:16px
}
input{background:white;color:#111}
select{background:#e9edf4;color:#111}
button{background:#f04444;color:white;font-weight:bold;cursor:pointer}
.note{font-size:12px;color:#9caabd;margin-top:22px}
.separator{margin:22px 0;color:#aab5c5}
</style>
</head>
<body>
<div class="container">
 <div class="logo">VIDEO <span>DOWNLOADER</span></div>
 <div class="subtitle">Descarcă și convertește videoclipurile tale.</div>
 <div class="panel">

  <form action="/convert" method="POST" enctype="multipart/form-data">

   <input type="url" name="youtube_url"
   placeholder="Lipește linkul videoclipului YouTube (opțional)">

   <div class="separator">SAU ÎNCARCĂ VIDEOCLIPUL DESCĂRCAT DIN YOUTUBE STUDIO</div>

   <input type="file" name="video" accept="video/*,audio/*">

   <select name="format">
    <option value="mp4">MP4 – Video</option>
    <option value="mp3">MP3 – Audio</option>
   </select>

   <button type="submit">CONVERTEȘTE ACUM</button>
  </form>
 </div>
 <div class="note">
  Pentru videoclipurile proprii, descarcă mai întâi fișierul din YouTube Studio.
 </div>
</div>
</body>
</html>
"""

@app.route("/")
def home():
    return render_template_string(PAGE)

@app.route("/convert", methods=["POST"])
def convert():
    video = request.files.get("video")
    youtube_url = request.form.get("youtube_url", "").strip()
    fmt = request.form.get("format", "mp4")

    if youtube_url and not video.filename:
        return (
            "Linkul YouTube a fost primit, dar descărcarea directă "
            "nu este disponibilă prin API-ul oficial. Descarcă videoclipul "
            "propriu din YouTube Studio și încarcă fișierul aici."
        ), 400

    if not video or not video.filename:
        return "Alege un fișier video.", 400

    if fmt not in ("mp4", "mp3"):
        return "Format invalid.", 400

    folder = tempfile.mkdtemp()
    source = os.path.join(folder, "source")
    output = os.path.join(folder, "converted." + fmt)

    try:
        video.save(source)
        ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()

        if fmt == "mp3":
            command = [
                ffmpeg, "-y", "-i", source,
                "-vn", "-codec:a", "libmp3lame",
                "-q:a", "2", output
            ]
        else:
            command = [
                ffmpeg, "-y", "-i", source,
                "-c:v", "libx264", "-c:a", "aac",
                "-movflags", "+faststart", output
            ]

        result = subprocess.run(
            command, capture_output=True, text=True, timeout=600
        )

        if result.returncode != 0 or not os.path.exists(output):
            return "Nu am putut converti videoclipul.", 400

        return send_file(
            output, as_attachment=True,
            download_name="videoclip." + fmt
        )

    except subprocess.TimeoutExpired:
        return "Conversia a durat prea mult.", 408
    except Exception:
        return "A apărut o eroare la conversie.", 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
