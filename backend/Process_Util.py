import os
import ffmpeg
import pysrt
import json
import re
from backend.MLM_Puncut.splitting_process import split_text 
from backend.MLM_Puncut.splitter_output_to_srt import convert_to_srt

class PreprocessUtil:
    def __init__(self):
        self.input_file = None
        pass
    
    def clear_cache(directory_path):
        """Deletes all files within a directory and its subdirectories, while keeping the directory structure."""
        try:
            for root, dirs, files in os.walk(directory_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    os.remove(file_path)
                    print(f"Deleted {file_path}")
            print(f"Successfully cleared all files from {directory_path}")
        except Exception as e:
            print(f"Error deleting files in {directory_path}: {e}")
        
    def convert_mp4_to_mp3(output_folder , input_file):
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
        output_file = os.path.join(output_folder, os.path.splitext(os.path.basename(input_file))[0] + ".mp3")
        try:
            (
                ffmpeg
                .input(input_file)
                .output(output_file, codec='libmp3lame', audio_bitrate='128k' , map='0:a')
                .run(overwrite_output=True)
            )
            print(f"Converted {input_file} to {output_file}")
        except ffmpeg.Error as e:
            print(f"Failed to convert {input_file}. Reason: {e}")
        
    
    
    
class MidProcessUtil:
    
    def linguistic_splitting(input_file , output_folder , srt_output_folder , lang):
        data = ""
        data = json.loads(open(input_file, encoding="utf-8").read())
        complete_sub = split_text(data , lang)
        with open(output_folder, "w", encoding="utf-8") as f:
            json.dump(complete_sub, f, indent=4 , ensure_ascii=False)
        
        with open(output_folder, "r", encoding="utf-8") as f:
            subtitles = json.load(f)
        srt_content = convert_to_srt(subtitles)
        with open(srt_output_folder, "w", encoding="utf-8") as f:
            f.write(srt_content)
        return output_folder



    def gemini_json_input(srt_file):
        with open(srt_file, 'r', encoding='utf-8') as file:
            srt_content = file.read()

        pattern = re.compile(r'(\d+)\n(\d{2}:\d{2}:\d{2},\d{3} --> \d{2}:\d{2}:\d{2},\d{3})\n(.+?)(?=\n\d+|$)', re.DOTALL)
        matches = pattern.findall(srt_content)

        subtitles = []
        for match in matches:
            num, time_frame, text = match
            text = text.replace('\n', ' ')
            subtitles.append({"sub_number": int(num), "sub": text.strip()})

        return json.dumps(subtitles, ensure_ascii=False, indent=4)




class PostProcessUtil:
    def match_timings(json_file , srt_file , output_file):
        def read_srt_file(file_path):
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
            srt_pattern = re.compile(r"(\d+)\n(\d{2}:\d{2}:\d{2},\d{3}) --> (\d{2}:\d{2}:\d{2},\d{3})\n(.*?)\n", re.DOTALL)
            matches = srt_pattern.findall(content)
            lines = []
            for match in matches:
                index, start_time, end_time, text = match
                lines.append({
                    'index': int(index),
                    'start_time': start_time,
                    'end_time': end_time,
                    'text': text.strip()
                })
            return lines
        
        # Read the JSON data
        with open(json_file, 'r', encoding='utf-8') as f:
            json_data = json.load(f)['subtitles']

        # Read and process the SRT file
        srt_lines = read_srt_file(srt_file)

        # Create a dictionary to map subtitle numbers to their timestamps
        srt_dict = {line['index']: line for line in srt_lines}
        # Combine JSON lines with corresponding SRT timestamps and write in SRT format
        with open(output_file, 'w', encoding='utf-8') as f:
            for json_line in json_data:
                number = json_line['sub_number']
                text = json_line['sub']
                if number in srt_dict:
                    start_time = srt_dict[number]['start_time']
                    end_time = srt_dict[number]['end_time']
                    
                    f.write(f"{number}\n")
                    f.write(f"{start_time} --> {end_time}\n")
                    f.write(f"{text}\n\n")
                else:
                    print(f"Warning: Subtitle number {number} not found in SRT file")        
        return output_file

    def convert_srt_to_vtt(input_srt_file, output_dir):
        try:
            subs = pysrt.open(input_srt_file)
            output_file = os.path.join(output_dir, os.path.splitext(os.path.basename(input_srt_file))[0] + ".vtt")
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write("WEBVTT\n\n")
                for sub in subs:
                    start = sub.start.to_time().strftime('%H:%M:%S.%f')[:-3]
                    end = sub.end.to_time().strftime('%H:%M:%S.%f')[:-3]
                    f.write(f"{start} --> {end}\n")
                    f.write(f"{sub.text}\n\n")
            print(f"Successfully converted '{input_srt_file}' to '{output_file}'")
        except Exception as e:
            print(f"Error converting '{input_srt_file}': {e}")
        return output_file
        
    
