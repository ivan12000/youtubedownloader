import yt_dlp
from pydub import AudioSegment
import os
import sys

def download_youtube_video_as_mp3(url, output_path):
    # Download video from YouTube
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    # Find the downloaded file
    info_dict = ydl.extract_info(url, download=False)
    title = info_dict.get('title', None)
    downloaded_file = os.path.join(output_path, f"{title}.mp3")

    return downloaded_file

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python script.py <YouTube URL>")
        sys.exit(1)
    
    youtube_url = sys.argv[1]
    output_directory = '.'

    mp3_file = download_youtube_video_as_mp3(youtube_url, output_directory)
    print(f"Downloaded and converted to MP3: {mp3_file}")
