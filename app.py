import os
import yt_dlp

def descarca_youtube():
    url = input("Introdu link-ul videoclipului de pe YouTube: ").strip()
    if not url:
        print("Nu ai introdus niciun link.")
        return

    print("\nAlege formatul dorit:")
    print("1 - Video (cea mai bună calitate MP4)")
    print("2 - Doar Audio (MP3)")
    optiune = input("Introdu 1 sau 2: ").strip()

    # Creează un folder 'Descarcari' dacă nu există deja
    folder_destinatie = "Descarcari"
    os.makedirs(folder_destinatie, exist_ok=True)

    if optiune == "2":
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': f'{folder_destinatie}/%(title)s.%(ext)s',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        }
    else:
        ydl_opts = {
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            'outtmpl': f'{folder_destinatie}/%(title)s.%(ext)s',
            'merge_output_format': 'mp4',
        }

    try:
        print("\nSe descarcă...")
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        print(f"\nGata! Fișierul a fost salvat în folderul '{folder_destinatie}'.")
    except Exception as e:
        print(f"\nA apărut o eroare: {e}")

if __name__ == "__main__":
    descarca_youtube()
