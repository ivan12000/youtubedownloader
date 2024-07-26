from flask import Flask, render_template, request, send_file
import yt_dlp
import os
import logging

app = Flask(__name__)
DOWNLOAD_FOLDER = 'downloads'
if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

# Set up logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(message)s',
                    handlers=[logging.FileHandler("app.log"),
                              logging.StreamHandler()])

def download_youtube_video_as_mp3(url, output_path):
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }

    logging.info(f"Downloading video from URL: {url}")
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    # Find the downloaded file
    info_dict = ydl.extract_info(url, download=False)
    title = info_dict.get('title', None)
    downloaded_file = os.path.join(output_path, f"{title}.mp3")
    logging.info(f"Downloaded and converted to MP3: {downloaded_file}")

    return downloaded_file

@app.route('/')
def index():
    logging.info("Rendering index page")
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download():
    youtube_url = request.form['url']
    logging.info(f"Received download request for URL: {youtube_url}")
    try:
        mp3_file = download_youtube_video_as_mp3(youtube_url, DOWNLOAD_FOLDER)
        logging.info(f"Successfully downloaded MP3 file: {mp3_file}")
        
        if not os.path.exists(mp3_file):
            logging.error(f"File not found: {mp3_file}")
            return "File not found", 404

        return send_file(mp3_file, as_attachment=True)
    except Exception as e:
        logging.error(f"Error occurred: {str(e)}", exc_info=True)
        return f"An error occurred: {str(e)}"

if __name__ == '__main__':
    logging.info("Starting Flask app")
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 3000)))
