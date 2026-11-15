import os
import tempfile
import subprocess
import imageio_ffmpeg

from flask import Flask, request, send_file, render_template_string

app = Flask(__name__)

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
 margin:0;background:#101827;color:white;
 font-family:Arial,sans-serif;min-height:100vh;
 display:flex;justify-content:center;align-items:center;padding:20px
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
input{background:#fff;color:#111}
select{background:#e9edf4;color:#111}
button{background:#f04444;color:white;font-weight:bold;cursor:pointer}
.note{font-size:12px;color:#9caabd;margin-top:22px}
</style>
</head>
<body>
<div class="container">
 <div class="logo">VIDEO <span>DOWNLOADER</span></div>
 <div class="subtitle">Descarcă și convertește fișierele video.</div>
 <div class="panel">
  <form action="/convert" method="POST" enctype="multipart/form-data">
   <input type="file" name="video" accept="video/*,audio/*" required>
   <select name="format">
    <option value="mp4">MP4 – Video</option>
    <option value="mp3">MP3 – Audio</option>
   </select>
   <button type="submit">CONVERTEȘTE ACUM</button>
  </form>
 </div>
 <div class="note">Folosește numai materiale proprii sau autorizate.</div>
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
    fmt = request.form.get("format", "mp4")

    if not video or not video.filename:
        return "Alege un fișier.", 400

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
            return "Conversia nu a reușit. Verifică fișierul ales.", 400

        return send_file(
            output,
            as_attachment=True,
            download_name="videoclip." + fmt
        )

    except subprocess.TimeoutExpired:
        return "Conversia a durat prea mult.", 408
    except Exception as e:
        return "Eroare la conversie: " + str(e), 500

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=10000)
