from backend.transcribing import main
from backend.translating import sending_to_translation
from backend.Process_Util import PostProcessUtil , MidProcessUtil , PreprocessUtil
from flask import Flask, request, jsonify, send_from_directory , render_template
from flask_cors import CORS
from pathlib import Path
import tempfile
import os
import glob
import time
import json
# from concurrent.futures import ThreadPoolExecutor
app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = 'storage/videos/mp4/'
MP3_FOLDER = 'storage/videos/mp3/'
# executor = ThreadPoolExecutor(max_workers=2)  # you can set how many threads you want.

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/edetvido')
def edetvido():
    video_filename = request.args.get('video')
    return render_template('edetvido.html', video_filename=video_filename)

@app.route('/videoshow')
def videoshow():
    video_filename = request.args.get('video')
    return render_template('videoshow.html', video_filename=video_filename)

@app.route('/index', methods=['POST'])
def upload_video():
    if 'video' not in request.files:
        return jsonify({'success': False, 'message': 'No video file part'})
    #PreprocessUtil.clear_cache(Path(UPLOAD_FOLDER).parts[0])
    video = request.files['video']
    # global filename
    global filename 
    filename = video.filename  # Get the original filename
    PROBLEMATIC_CHARS = ['#', '?', '&', '=', '+', '%', '/', '\\', ' ']
    for char in PROBLEMATIC_CHARS:
        filename = filename.replace(char, '_')
    print(filename)
    files = glob.glob(os.path.join(UPLOAD_FOLDER, '*'))
    for f in files:
        os.remove(f)
    video.save(os.path.join(UPLOAD_FOLDER, filename))
    try:
       # Convert to mp3 and save the new file in the mp3 folder, using the same base filename
        PreprocessUtil.convert_mp4_to_mp3(MP3_FOLDER, os.path.join(UPLOAD_FOLDER, filename))
    except Exception as e:
        print(f"Exception converting {filename} to mp3: {e}")
    return jsonify({'success': True, 'filename': filename})  # Send original filename back

@app.route('/language', methods=['POST'])
def get_language():
    try:
        data = request.get_json()
        lang = data.get('language')
        print("Successful")
        return jsonify({
            'success': True,
            'language': lang or 'auto-detected',
            'video_filename': filename
        })
        
    except Exception as e:
        print(f"Error in get_language: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/video/<filename>')
def get_video(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

@app.route('/storage/final_output/<path:filename>')
def serve_vtt(filename):
    return send_from_directory('storage/final_output', filename)

@app.route('/videoshow/<language>')
def do_processing(language):
    try:
        video_filename = request.args.get('video')
        print(video_filename)
        print(language)
        lang = language
        if lang == 'auto-detect':
            lang = None
        # mp3_file = filename.split(".")[0] + ".mp3"
        # srt_path = os.path.join("storage/transcription_files/srt_files/", mp3_file.replace(".mp3" , ".srt"))
        # json_path = os.path.join("storage/transcription_files/json_files/", mp3_file.replace(".mp3" , ".json"))
        # audio_path = os.path.join(MP3_FOLDER, mp3_file)
        # print(audio_path)
        # result = main(audio_path, lang)

        # # print(mew)
        # try:
        #     with open(srt_path , "w" , encoding="utf-8") as f:
        #         f.write(result.get('srt'))
        #         f.close()
        # except Exception as e:
        #     print(f"Error writing SRT: {str(e)}")
        #     return jsonify({'success': False, 'message': 'Error processing video'}), 500
        # try:
        #     with open(json_path , "w" , encoding="utf-8") as f:
        #         json.dump(result.get('json') , f , ensure_ascii=False)
        #         f.close()
        # except Exception as e:
        #     print(f"Error writing JSON: {str(e)}")
        #     return jsonify({'success': False, 'message': 'Error processing video'}), 500
        
        # split_filename = mp3_file.replace(".mp3" , "_split.mp3")
        # split_json_path = os.path.join("storage/splitting/json_output/", split_filename.replace(".mp3" , ".json"))
        # split_srt_path = os.path.join("storage/splitting/srt_output/", split_filename.replace(".mp3" , ".srt"))
        # #Ensure the language is available
        # try:
        #     with open(json_path, encoding="utf-8") as f:
        #         lang = json.loads(f.read()).get('language')
        # except FileNotFoundError:
        #     return jsonify({'success': False, 'message': 'Language file not found'}), 404
        # MidProcessUtil.linguistic_splitting(json_path , split_json_path , split_srt_path , lang)

        # print(f"Processing language: {lang}")
        
        # gemini_json_path = os.path.join("storage/gemini_files/json_input/", split_filename.replace(".mp3" , ".json"))
        
        # #Write the Gemini JSON input
        # try:
        #     with open(gemini_json_path , "w" , encoding="utf-8") as f:
        #         f.write(MidProcessUtil.gemini_json_input(split_srt_path))
        # except Exception as e:
        #     print(f"Error writing Gemini JSON: {str(e)}")
        #     return jsonify({'success': False, 'message': 'Error processing video'}), 500    
        # #translate the gemini json
        # sending_to_translation(gemini_json_path)
        
        # #convert the translated json to srt and match the timestamps
        # tranlsated_jon_file = split_filename.split(".mp3")[0]
        # translated_json_path = os.path.join(f"output/translated {tranlsated_jon_file}2.json")
        # translated_srt_path = os.path.join(f"storage/gemini_files/srt_output/{split_filename.replace('.mp3' , '.srt')}")
        # PostProcessUtil.match_timings(translated_json_path , split_srt_path , translated_srt_path)
        
        # # convert srt to vtt
        # output_dir = "storage/final_output/"
        # vtt_file =  PostProcessUtil.convert_srt_to_vtt(translated_srt_path, output_dir)
        vtt_file = r"storage\final_output\I_rewrote_my_dungeon_generator!_split.vtt"
        print(video_filename)
        return jsonify({
                'success': True,
                'video_filename': video_filename,
                'subtitleUrl': vtt_file
            })
    except Exception as e:
        print(f"Error in do_processing: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500

if __name__ == '__main__':
    app.run(port=5001, debug=True)
