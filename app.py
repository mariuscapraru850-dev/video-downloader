
from flask import Flask, request, Response
import requests
from urllib.parse import urlparse
import socket
import ipaddress

app = Flask(__name__)

@app.route("/")
def home():
    return """
    <html>
    <head>
      <title>Video Downloader</title>
      <meta name="viewport" content="width=device-width, initial-scale=1">
      <style>
        body {background:#101010;color:white;font-family:Arial;text-align:center;padding:40px}
        h1 {color:#ff3030}
        input,button {padding:15px;width:90%;max-width:400px;margin:10px;border:0;border-radius:8px}
        button {background:#e60000;color:white;font-weight:bold;cursor:pointer}
      </style>
    </head>
    <body>
      <h1>VIDEO DOWNLOADER</h1>
      <p>Descarcă fișiere video de la adrese directe autorizate.</p>
      <form action="/download" method="get">
        <input name="url" placeholder="Introdu adresa fișierului video" required>
        <button>DESCARCĂ VIDEO</button>
      </form>
    </body>
    </html>
    """

@app.route("/download")
def download():
    url = request.args.get("url", "")
    parsed = urlparse(url)

    if parsed.scheme != "https" or not parsed.hostname:
        return "Este necesară o adresă HTTPS validă.", 400

    try:
        addresses = socket.getaddrinfo(parsed.hostname, 443)
        for address in addresses:
            ip = ipaddress.ip_address(address[4][0])
            if not ip.is_global:
                return "Adresa nu este permisă.", 400

        r = requests.get(url, stream=True, timeout=20)
        r.raise_for_status()

        if not r.headers.get("Content-Type", "").startswith("video/"):
            return "Adresa nu indică un fișier video.", 400

        return Response(
            r.iter_content(chunk_size=65536),
            content_type=r.headers.get("Content-Type"),
            headers={"Content-Disposition": 'attachment; filename="video.mp4"'}
        )
    except Exception:
        return "Nu am putut accesa fișierul video.", 400

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
