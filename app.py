
from flask import Flask, request, jsonify
import requests
import re
from urllib.parse import urlparse

app = Flask(__name__)

def get_video_id(url):
    patterns = [
        r'youtube\.com/watch\?v=([a-zA-Z0-9_-]{11})',
        r'youtu\.be/([a-zA-Z0-9_-]{11})',
        r'youtube\.com/shorts/([a-zA-Z0-9_-]{11})',
        r'youtube\.com/embed/([a-zA-Z0-9_-]{11})'
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None

@app.route("/")
def home():
    return """
<!DOCTYPE html>
<html lang="ro">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Video Downloader</title>
<style>
*{box-sizing:border-box}
body{
 margin:0;background:#111;color:white;
 font-family:Arial,sans-serif;text-align:center;
}
header{padding:25px;background:#080808}
h1{font-size:32px;margin:0;color:#ff2525}
h1 span{color:white}
main{max-width:700px;margin:65px auto;padding:20px}
h2{font-size:27px}
p{color:#bbb;line-height:1.6}
.form{
 display:flex;gap:10px;margin-top:30px;
 flex-wrap:wrap;justify-content:center
}
input{
 flex:1;min-width:220px;padding:18px;
 border:1px solid #444;border-radius:8px;
 background:#222;color:white;font-size:15px
}
button{
 padding:17px 25px;background:#ed2020;
 color:white;border:0;border-radius:8px;
 font-weight:bold;cursor:pointer
}
button:hover{background:#bd1010}
#result{
 margin-top:30px;padding:20px;
 background:#1b1b1b;border-radius:12px;
 display:none
}
#thumb{width:100%;max-width:450px;border-radius:8px}
#message{margin-top:20px;color:#ddd}
footer{color:#777;padding:30px}
</style>
</head>
<body>
<header>
<h1>VIDEO <span>DOWNLOADER</span></h1>
</header>
<main>
<h2>Descarcă videoclipuri</h2>
<p>Introdu linkul videoclipului pentru a identifica materialul.</p>
<div class="form">
<input id="url" placeholder="Lipește linkul YouTube aici">
<button onclick="checkVideo()">VERIFICĂ LINKUL</button>
</div>
<div id="result">
<img id="thumb" src="" alt="Miniatura videoclipului">
<h3 id="title"></h3>
<p id="message"></p>
</div>
</main>
<footer>Video Downloader</footer>
<script>
async function checkVideo(){
 const url=document.getElementById('url').value.trim();
 const result=document.getElementById('result');
 const message=document.getElementById('message');
 result.style.display='block';
 message.textContent='Se verifică linkul...';

 try{
  const response=await fetch('/info?url='+encodeURIComponent(url));
  const data=await response.json();

  if(!response.ok) throw new Error(data.error);

  document.getElementById('thumb').src=data.thumbnail;
  document.getElementById('title').textContent=data.title;
  message.textContent=
   'Videoclip identificat. Pentru descărcare, folosește YouTube Studio dacă este videoclipul tău.';
 }catch(e){
  message.textContent=e.message || 'Link invalid.';
 }
}
</script>
</body>
</html>
"""

@app.route("/info")
def info():
    url = request.args.get("url", "")
    video_id = get_video_id(url)

    if not video_id:
        return jsonify(error="Link YouTube invalid."), 400

    try:
        response = requests.get(
            "https://www.youtube.com/oembed",
            params={"url": "https://www.youtube.com/watch?v=" + video_id,
                    "format": "json"},
            timeout=10
        )
        response.raise_for_status()
        data = response.json()

        return jsonify(
            title=data.get("title", "Videoclip YouTube"),
            thumbnail=data.get(
                "thumbnail_url",
                "https://img.youtube.com/vi/" + video_id + "/hqdefault.jpg"
            )
        )
    except requests.RequestException:
        return jsonify(error="Nu am putut identifica videoclipul."), 502

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
