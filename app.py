from flask import Flask, render_template, request, send_file
from flask_socketio import SocketIO, emit
import yt_dlp
import os
import logging
from threading import Thread

app = Flask(__name__)
socketio = SocketIO(app)

DOWNLOAD_FOLDER = 'downloads'
if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

# Set up logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(message)s')

class SocketIOHandler(logging.Handler):
    def emit(self, record):
        log_entry = self.format(record)
        socketio.emit('log_message', {'message': log_entry})

# Add the SocketIOHandler to the logger
socketio_handler = SocketIOHandler()
socketio_handler.setLevel(logging.INFO)
socketio_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'))
logging.getLogger().addHandler(socketio_handler)

def log_info(message):
    logging.info(message)

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

    log_info(f"Downloading video from URL: {url}")
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    # Find the downloaded file
    info_dict = ydl.extract_info(url, download=False)
    title = info_dict.get('title', None)
    downloaded_file = os.path.join(output_path, f"{title}.mp3")
    log_info(f"Downloaded and converted to MP3: {downloaded_file}")

    return downloaded_file

@app.route('/')
def index():
    log_info("Rendering index page")
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download():
    youtube_url = request.form['url']
    log_info(f"Received download request for URL: {youtube_url}")

    def download_thread():
        try:
            log_info(f"Starting downloading MP3 file from: {youtube_url}")
            mp3_file = download_youtube_video_as_mp3(youtube_url, DOWNLOAD_FOLDER)
            log_info(f"Successfully downloaded MP3 file: {mp3_file}")
            socketio.emit('download_complete', {'file_path': mp3_file})
        except Exception as e:
            log_info(f"Error occurred: {str(e)}")

    thread = Thread(target=download_thread)
    thread.start()
    
    return render_template('index.html')

@app.route('/download_file', methods=['GET'])
def download_file():
    file_path = request.args.get('file_path')
    if file_path and os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    return "File not found", 404

if __name__ == '__main__':
    log_info("Starting Flask app")
    socketio.run(app, host='0.0.0.0',allow_unsafe_werkzeug=True, port=int(os.environ.get('PORT', 3000)))
