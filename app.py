import os
import time
from flask import Flask, render_template, request, redirect, url_for
import whisper
import subprocess

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def extract_audio_from_video(video_path, audio_path):
    command = f"ffmpeg -i {video_path} -q:a 0 -map a {audio_path}"
    subprocess.run(command, shell=True)

def transcribe_audio(audio_path, model="base"):
    model = whisper.load_model(model)
    result = model.transcribe(audio_path)
    return result['text']

@app.route('/', methods=['GET', 'POST'])
def index():
    transcription = ""
    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            return redirect(request.url)
        if file:
            video_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(video_path)
            audio_path = video_path.rsplit('.', 1)[0] + '.wav'
            extract_audio_from_video(video_path, audio_path)
            transcription = transcribe_audio(audio_path)

            # Delay the removal of files
            time.sleep(1)  # Give it a moment to ensure all processes are done
            os.remove(video_path)
            os.remove(audio_path)

    return render_template('index.html', transcription=transcription)

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
