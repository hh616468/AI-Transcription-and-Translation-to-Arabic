import json
import os


# Function to convert time to SRT format
def format_time(seconds):
    milliseconds = int((seconds - int(seconds)) * 1000)
    minutes, seconds = divmod(int(seconds), 60)
    hours, minutes = divmod(minutes, 60)
    return f"{hours:02}:{minutes:02}:{seconds:02},{milliseconds:03}"

# Convert to SRT format
def convert_to_srt(subtitles):
    srt_output = []
    for idx, subtitle in enumerate(subtitles, start=1):
        start_time = format_time(subtitle["start"])
        end_time = format_time(subtitle["end"])
        srt_output.append(f"{idx}")
        srt_output.append(f"{start_time} --> {end_time}")
        srt_output.append(subtitle["text"].strip())
        srt_output.append("")  # Add a blank line between entries
    return "\n".join(srt_output)

