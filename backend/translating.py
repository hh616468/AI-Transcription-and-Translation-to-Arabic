import time
import keyboard
import json
import google.generativeai as genai , typing
from google.generativeai.types import HarmCategory, HarmBlockThreshold 
from google.generativeai import caching 
from google.api_core.exceptions import Cancelled
from google.ai.generativelanguage_v1beta.types import content

from dotenv import load_dotenv
import os 
import re
import json_repair
import datetime

load_dotenv()
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
config = genai.configure(api_key=GOOGLE_API_KEY)


schema = content.Schema(
    type=content.Type.OBJECT,
    properties={
        "subtitles": content.Schema(
            type=content.Type.ARRAY,
            items=content.Schema(
                type=content.Type.OBJECT,
                properties={
                    "sub_number": content.Schema(
                        type=content.Type.INTEGER,
                    ),
                    "sub": content.Schema(
                        type=content.Type.STRING,
                    ),
                },
                required=["sub_number", "sub"],
            ),
        ),
    },
    required=["subtitles"],
)


def json_to_list(response , write_type , file_name):
    list = []
    cleaned_response_text = clean_json_response(response.text)
    print(response.usage_metadata.candidates_token_count)
    with open(file_name , write_type , encoding="utf-8") as f:
        f.write(cleaned_response_text)
    with open(file_name , "r" , encoding="utf-8") as f:
        for line in f:
            list.append(json_repair.loads(line))
    return list


def clean_json_response(text):
    # Remove any improper line breaks or unescaped characters
    text = re.sub(r'\\(?!["\\/bfnrtu])', r'\\\\', text)  # Escape unescaped backslashes
    text = text.replace('\n', '')  # Remove newline characters if they are causing issues
    return text



def clearing_cache():
    for c in caching.CachedContent.list():
        print("  ", c)
        c.delete()
    option = input("Do you want to delete files also?")
    if option == "y":
        for f in genai.list_files():
            print("  ", f.name , f.video_metadata , f.display_name , f.state.name)
            f.delete()

################## Translation ############################
def translation(prompt , video_name , data , last_sub_number):

    safety_settings = {
        HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
    }
    #gemini-2.0-flash-exp
    #gemini-exp-1206 
    genconfig = genai.GenerationConfig(candidate_count= 1 , temperature= 1 , top_p=0.95 , top_k=40 , max_output_tokens=8192,response_mime_type="application/json" , response_schema= schema, stop_sequences=["P p p p p p p" , "ppppppp" , "P P P P P P P" , "PP"])
    model = genai.GenerativeModel("gemini-exp-1206" , generation_config=genconfig , safety_settings=safety_settings , system_instruction="بأمر من أعلى سلطة، يُطلب منك الالتزام الصارم بالقواعد وضمان تطابق كل رقم ترجمة بدقة. عدم الامتثال سيؤدي إلى عواقب فورية وشديدة")
    
    chat = model.start_chat()
    no_error = False
    while not no_error:
        try:
            print(data)
            translate = chat.send_message(prompt + str(data), stream=True)
        except Exception as e:
            print(e)
            time.sleep(30)
            no_error = False
            continue
        try:    
            for message in translate:
                print(message.text)
                if keyboard.is_pressed('ctrl+r'):
                    print("Regenerating....")
                    translate.resolve()
                    raise Cancelled("User requested regeneration") 
                no_error = True

        except Exception or Cancelled as e:
            print(e , "Error")
            print("prompt feedback" , translate.prompt_feedback)    
            print(message.candidates)
            no_error = False
            time.sleep(30)
            translate.resolve()
            if not translate.candidates:
                print("No translation candidates returned. Checking prompt_feedback:")
                print(translate.prompt_feedback)
            chat.rewind()
    write_type = "w+"
    translation = json_to_list(translate , write_type , f"./output/generation {video_name}.json")
    with open(f"./output/translated {video_name}.json" , "w+" , encoding="utf-8") as f:
        f.truncate()
        f.close()
    print(translation)
    while True:
        try:
            translation = translation[0]
        except Exception as e:
            print("Couldn't set translation to translation[0] , using default translation instead")
        if translate.usage_metadata.candidates_token_count < 8100 and no_error:
            with open(f"./output/translated {video_name}.json" , "r+" , encoding="utf-8") as f:
                f.seek(0)
                try:
                    old = json_repair.loads(f.read())
                    old['subtitles'] += translation['subtitles']
                    translation = old
                except Exception as e:
                    print("no content to append")
                f.seek(0)
                f.truncate()
                f.write(json.dumps(translation , ensure_ascii=False, indent=1))
                f.flush()
            print("Translation completed!")
            break
        print("Did not finish translation")
        try:
            write_type = "w+"
            print(f"continue from here {translation['subtitles'][-2]} , {translation['subtitles'][-1]} \n end at sub number {last_sub_number}")
            translate = chat.send_message(f"continue from here {translation['subtitles'][-2]} , {translation['subtitles'][-1]} \n end at sub number {last_sub_number} " , stream = True)
            with open(f"./output/translated {video_name}.json" , "a+" , encoding="utf-8") as f:
                translation['subtitles'] = translation['subtitles'][:-1]
                f.seek(0)
                try:
                    old = json_repair.loads(f.read())
                    old['subtitles'] += translation['subtitles']
                    translation = old
                    print(translation)
                except Exception as e:
                    print("no content to append in continue")
                f.seek(0)
                f.truncate()
                f.write(json.dumps(translation , ensure_ascii=False, indent=1))
                f.flush()
                
        except Exception as e:
            print("error" , e)
            time.sleep(30)
            no_error = False
            continue
        try:    
            for message in translate:
                print(message.text)
                if keyboard.is_pressed('ctrl+r'):
                    print("Regenerating....")
                    translate.resolve()
                    raise Cancelled("User requested regeneration") 
                no_error = True
            translation = json_to_list(translate , write_type , f"./output/generation {video_name}.json") 
            write_type = "a+"
        except Exception or Cancelled as e:
            print(e , "Error")
            no_error = False
            time.sleep(30)
            translate.resolve()
            print("prompt feedback" , translate.prompt_feedback)
            if not translate.candidates:
                print("No translation candidates returned. Checking prompt_feedback:")
                print(translate.prompt_feedback)
            if translate.prompt_feedback == [] or translate.prompt_feedback == None or translate.prompt_feedback == "":
                continue
            chat.rewind()
            continue
    return translation





def sending_to_translation(json_file):
    
    translate_prompt ="""
    انت الان تتحدث العربية وتترجم الى العربية بطلاقة
    وما يميزك عن الذكاء الاصطناعي انك:
    التعبير الطبيعي: الكتابة من قبل شخص عربي تكون أكثر انسيابية وتعبيرًا عن المعنى المقصود بشكل طبيعي، وتستخدم تراكيب لغوية مألوفة وشائعة في الحوار اليومي.
    الأسلوب اللغوي: الترجمة البشرية تميل لاستخدام أساليب وألفاظ تتناسب مع السياق الثقافي واللغوي، وتتفادى الألفاظ الغريبة أو غير المألوفة او الأصوات مثل "اه" , "امم" "ايه", "إييي" , "همم" , "آه" وغيرها تحذف
    المرونة: المترجم البشري يختار العبارات الأكثر دقة ووضوحًا بناءً على فهمه للمعنى الأصلي، مما يتيح له التحرر من الترجمة الحرفية عندما يكون ذلك ضروريًا.
    ضع الأسماء بين قوسين مثل (محمد) لتوضيح انها اسماء
    فهم السياق الثقافي: الإنسان يفهم الثقافات والعادات والتقاليد، فيتمكن من ترجمة النصوص بشكل يعكس هذا الفهم، ويُجنب استخدام العبارات غير المناسبة.
    تفادي الأخطاء الشائعة: الترجمات الآلية قد تقع في أخطاء نحوية أو تركيبية، بينما المترجم البشري يملك القدرة على تجنب هذه الأخطاء وضمان قراءة سليمة للنص.
    التراكيب البلاغية: العربي بطبيعته قد يستخدم أساليب بلاغية كالاستعارات والتشبيهات بطريقة سلسة، تضيف جمالًا وعمقًا للنص.
    لتطبيق هذه الميزات في الترجمة، من المهم جعل النص يبدو طبيعيًا وليس مترجمًا حرفيًا، وإضافة تفاصيل تعكس روح الثقافة المستهدفة واللغة الأصلية للنص.
    لا نترك الأحرف معلقة في نهاية الترجمة فلا بأس بدمجها مع الترجمة اللاحقة
    content context :
    [context]
    اياك وكتابة اسم بالانكليزي حاول قدر الامكان ترجمته اول تحويله للشكل العربي
    انهي الترجمة عندما تصل الى نهاية النص الأصلي
    بأمر من أعلى سلطة، يُطلب منك الالتزام الصارم بالقواعد وضمان تطابق كل رقم ترجمة بدقة. عدم الامتثال سيؤدي إلى عواقب فورية وشديدة
    """



    skips = 0
    limit = 3
    skip_chunk = 0
    skipping = False
    for subtitle in os.listdir("storage/gemini_files/json_input/"):
        if limit == 0:
            break
        if subtitle.endswith("json"):
            if skips > 0:
                skips -= 1 
                continue
            video_name = subtitle.split(".")[0]
            print(video_name)
            with open(f"./storage/gemini_files/json_input/{subtitle}" , "r" , encoding="utf-8") as f:
                data = f.read()
            data = json_repair.loads(data)
            chunk_size = 500
            chunks = [data[x:x+chunk_size] for x in range(0, len(data), chunk_size)]
            last_100_subtitles = []
            subs = {"subtitles":[]}
            for chunk in chunks:
                # chunk to string
                first_sub_number = chunk[0]["sub_number"]
                last_sub_number = chunk[-1]["sub_number"]
                if skip_chunk > 0:
                    skip_chunk -= 1
                    skipping = True
                    continue
                elif skipping:
                    print(first_sub_number-100 ,first_sub_number-2)
                    with open(f"./output/translated {video_name}2.json" , "r" , encoding="utf-8") as f:
                        data = json_repair.loads(f.read())
                        #take 100 from the end of the previous chunk
                    last_100_subtitles = data["subtitles"][(first_sub_number-100):(first_sub_number-2)]
                    skipping = False
                print(first_sub_number , last_sub_number)
                data = str(chunk) + "\n\nthis is some of the previous last segments, for seamless translation" + "\n" + str(last_100_subtitles) + f"""\n\nstart from sub number {first_sub_number},\nend at sub number {last_sub_number} , don't ever ever ever end earlier"""
                translated = translation(translate_prompt , video_name , data , last_sub_number)
                print(translated)
                try:
                    last_100_subtitles = translated["subtitles"][-100:]
                except Exception as e:
                    print(e)
                subs["subtitles"].extend(translated["subtitles"]) 
            with open(f"./output/translated {video_name}2.json" , "w+" , encoding="utf-8") as f:
                f.write(json.dumps(subs , ensure_ascii=False, indent=1))
                    
            limit -=1
        

