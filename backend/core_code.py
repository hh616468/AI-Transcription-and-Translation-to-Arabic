from transcribing import main
from translating import sending_to_translation
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import tempfile
import os
import glob
app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route('/index', methods=['POST'])
def upload_video():
    if 'video' not in request.files:
        return jsonify({'success': False, 'message': 'No video file part'})

    video = request.files['video']
    filename = video.filename  # Get the original filename
    files = glob.glob(os.path.join(UPLOAD_FOLDER, '*'))
    for f in files:
        os.remove(f)
    video.save(os.path.join(UPLOAD_FOLDER, filename))
    return jsonify({'success': True, 'filename': filename})  # Send filename back

@app.route('/language', methods=['POST'])
def get_language():
    data = request.get_json()
    print(data)
    return jsonify({'success': True, 'language': 'English'})

@app.route('/video/<filename>')
def get_video(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)


if __name__ == '__main__':
    app.run(port=5001, debug=True) 
