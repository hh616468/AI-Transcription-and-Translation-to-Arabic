import dropbox
import os
import base64
import runpod
import time
import json
import datetime
import tempfile
from dropbox.exceptions import AuthError
from dotenv import load_dotenv

load_dotenv()
def upload_to_dropbox(file_path):
    ACCESS_TOKEN = os.getenv("dropbox_token")
    print(ACCESS_TOKEN)
    dbx = dropbox.Dropbox(ACCESS_TOKEN)
    
    try:
        dbx.users_get_current_account()
    except AuthError:
        print("ERROR: Invalid access token; try re-generating an access token from the app console on the web.")
        return None
    with open(file_path, 'rb') as f:
        dropbox_path = file_path.replace('\\', '/')
        if dropbox_path.startswith('/'):
            dropbox_path = dropbox_path[1:]

        print(f"Uploading {file_path} to Dropbox as /{dropbox_path}...")
        try:
            dbx.files_upload(f.read(), "/" + dropbox_path, mode=dropbox.files.WriteMode('overwrite'))
        except dropbox.exceptions.ApiError as err:
            if (err.error.is_path() and
                    err.error.get_path().is_insufficient_space()):
                print("ERROR: Cannot back up; insufficient space.")
                return None
            else:
                print("API error during upload:", err)
                return None
        try:
            shared_link_metadata = dbx.sharing_create_shared_link_with_settings("/" + dropbox_path)
        except dropbox.exceptions.ApiError as err:
            if err.error.get_shared_link_already_exists():
                shared_link_metadata = err.error.get_shared_link_already_exists().get_metadata()
            else:
                print("API error during sharing:", err)
                return None

        shared_link_url = shared_link_metadata.url
        print("secpmd" , shared_link_url)
        shared_link_url = shared_link_url.replace("dl=0" , "dl=1")
        return shared_link_url



def main(audio_file_path , lang):
    runpod.api_key = os.getenv("runpod_token")
    endpoint_id = os.getenv("endpoint_id")
    # Upload the audio file to Dropbox and get the direct download link
    dropbox_link = upload_to_dropbox(audio_file_path)
    print(dropbox_link)

    if dropbox_link is None:
        print("Failed to upload the audio file to Dropbox.")
        return
    print(dropbox_link)
    input_params = {
        "input": {
            "audio": dropbox_link,
            "model": "large-v2",
            "align_model" : "WAV2VEC2_ASR_LARGE_LV60K_960H",
            "print_progress": True,
            "max_line_count" : 1,
        }
    }
    if lang:
        input_params["input"]["language"] = lang
        
    # Create an endpoint object
    endpoint = runpod.Endpoint(endpoint_id)
    # Run the request
    try:
        job = endpoint.run(input_params)
        start_time = 0
        # Polling loop to wait for the job to complete
        while True:
            job_status = job.status()
            if job_status == "COMPLETED":
                result = job.output()
                print("Request successful. Response:")
                print(result.get('srt'))
                print("Job started at : " , start_time.minute , ":" , start_time.second , " and ended at : " , datetime.datetime.now().minute , ":" , datetime.datetime.now().second)
                break

            elif job_status in ["FAILED", "CANCELLED"]:
                print(f"Request failed. Status: {job_status}")
                break 
            elif job_status == "IN_PROGRESS":
                print("Job in progress...")
                if start_time == 0:
                    start_time = datetime.datetime.now()
                time.sleep(1)
            else:
                print(f"Job status: {job_status}")
                time.sleep(1)  # Wait for 5 seconds before polling again
    except Exception as e:
        print(f"Unexpected error: {e}")
    return result

