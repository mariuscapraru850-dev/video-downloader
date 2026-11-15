import os
import tempfile
import requests
from urllib.parse import urlparse
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
 display:flex;justify-content:center;align-items:center;
 padding:20px
}
.container{width:100%;max-width:650px;text-align:center}
.logo{font-size:35px;font-weight:800;margin-bottom:12px}
.logo span{color:#ff4545}
.subtitle{color:#aab5c5;margin-bottom:30px}
.panel{
 background:#1c293b;padding:28px;border-radius:18px;
 box-shadow:0 15px 45px #0005
}
input,select,button{
 width:100%;padding:16px;border-radius:10px;
 border:0;margin-top:13px;font-size:16px
}
input{background:#fff;color:#111}
select{background:#e9edf4;color:#111}
button{
 background:#f04444;color:white;font-weight:bold;
 cursor:pointer
}
button:hover{background:#d92f2f}
.note{font-size:12px;color:#9caabd;margin-top:22px}
#status{margin-top:18px;color:#ffd166}
</style>
</head>
<body>
<div class="container">
 <div class="logo">VIDEO <span>DOWNLOADER</span></div>
 <div class="subtitle">Descarcă rapid materialele video pe care ai dreptul să le salvezi.</div>
 <div class="panel">
  <form action="/download" method="POST">
   <input name="url" type="url" placeholder="Lipește aici linkul video..." required>
   <select name="format">
    <option value="mp4">MP4 – Video</option>
    <option value="mp3">MP3 – Audio</option>
   </select>
   <button type="submit">DESCARCĂ ACUM</button>
  </form>
  <div id="status"></div>
 </div>
 <div class="note">Folosește numai materiale proprii sau pentru care ai permisiunea de descărcare.</div>
</div>
</body>
</html>
"""

@app.route("/")
def home():
    return render_template_string(PAGE)

@app.route("/download", methods=["POST"])
def download():
    url = request.form.get("url", "").strip()
    fmt = request.form.get("format", "mp4")

    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https") or not parsed.netloc:
        return "Link invalid.", 400

    # Acceptă linkuri directe către fișiere video/audio.
    if not parsed.path.lower().endswith((".mp4", ".mp3", ".webm", ".mov", ".m4a")):
        return (
            "Acest site acceptă momentan linkuri directe către fișiere "
            "video sau audio. Pentru videoclipurile YouTube, folosește "
            "metodele oficiale de descărcare disponibile pentru materialele tale."
        ), 400

    folder = tempfile.mkdtemp()
    try:
        response = requests.get(url, stream=True, timeout=30)
        response.raise_for_status()

        filename = os.path.basename(parsed.path) or "video"
        path = os.path.join(folder, filename)

        with open(path, "wb") as f:
            for chunk in response.iter_content(chunk_size=1024 * 1024):
                if chunk:
                    f.write(chunk)

        return send_file(path, as_attachment=True, download_name=filename)

    except Exception:
        return "Nu am putut descărca fișierul. Verifică linkul și încearcă din nou.", 400

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
