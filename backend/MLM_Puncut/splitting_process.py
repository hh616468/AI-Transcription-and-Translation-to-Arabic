import json
import pandas as pd
import sys
import os
from backend.MLM_Puncut.MLM_Splitter import score_text , load_model

def interpolate_nans(x, method='cubic'):
    if x.notnull().sum() > 1:
        return x.interpolate(method=method).ffill().bfill()

    else:
        return x.ffill().bfill()

def split_text(data , lang):
    complete_sub = []
    for i in range(0, len(data["segments"])):
        if len(data["segments"][i]["text"].split()) <= 10:
            complete_sub.append(
                {"text": data["segments"][i]["text"],
                "start": data["segments"][i]["start"], 
                "end": data["segments"][i]["end"]})
            continue
        
        long_sub = {"text": data["segments"][i]["text"], 
                    "start": data["segments"][i]["start"],
                    "end": data["segments"][i]["end"] ,
                    "words" : data["segments"][i]["words"]}
        
        new_sub = ""
        new_starts = []
        new_ends = []
        
        for idx , word in enumerate(long_sub["words"]):
            print(word)
            if word.get("start") is not None:
                new_starts.append(word["start"])
                new_ends.append(word["end"])
            else:
                start_series = pd.Series([word.get("start", None) for word in long_sub["words"]])
                end_series = pd.Series([word.get("end", None) for word in long_sub["words"]])
                start_series = interpolate_nans(start_series).to_list()
                end_series = interpolate_nans(end_series).to_list()
                new_starts.append(start_series[idx])
                new_ends.append(end_series[idx])
                print(long_sub["words"])
            new_sub += word["word"] + " "
        
        print("WHOPP" , len(new_sub.split()))
        print("Splitting text: ", new_sub)
        multi_segments = []
        model, mask_token = load_model()
        while len(new_sub) > 0:
            candidates = score_text(new_sub , lang_code=lang , new_starts=new_starts , new_ends=new_ends , model=model , mask_token=mask_token)
            best = max(candidates, key=lambda x: x["score"])
            print("best: ", best)
            print("chunk :" , best["text"])
            new_sub = best["remaining"]
            new_starts = new_starts[len(best["starts"]):]
            new_ends = new_ends[len(best["ends"]):]
            multi_segments.append({"text": best["text"], "start": best["starts"][0], "end": best["ends"][-1]})
        s = 0
        while s < len(multi_segments):
            print("Text :" , multi_segments[s]["text"] ,"\n", "Text Length :" , len(multi_segments[s]["text"].split()))
            start = multi_segments[s]["start"]
            end = multi_segments[s]["end"]
            duration = end - start
            # 2 short lines, 2 short timings
            if s+1 < len(multi_segments) :
                if len(multi_segments[s]["text"]) + len(multi_segments[s+1]["text"]) <= 85 and multi_segments[s+1]["end"] - start <= 7:
                    print("When 2 short lines, 2 short timings")
                    complete_sub.append({"text": multi_segments[s]["text"] + " " +  multi_segments[s+1]["text"], "start": multi_segments[s]["start"], "end": multi_segments[s+1]["end"]})
                    s += 2
                    continue
                
                #1 short line, with short timing 
                elif len(multi_segments[s]["text"])/duration > 25 :
                    if len(multi_segments[s]["text"]) + len(multi_segments[s+1]["text"]) <= 95 and multi_segments[s+1]["end"] - start <= 7:
                        print("When 1 short line, with short timing, next is better")
                        complete_sub.append({"text": multi_segments[s]["text"] + " " +  multi_segments[s+1]["text"], "start": multi_segments[s]["start"], "end": multi_segments[s+1]["end"]})
                        s += 2
                        continue
                    elif len(multi_segments[s]["text"]) + len(complete_sub[-1]["text"]) <= 95 and complete_sub[-1]["start"] - end <= 7 and s > 0:
                        print("When 1 short line, with short timing, previous is better")
                        complete_sub[-1]["text"] += " " + multi_segments[s]["text"]
                        complete_sub[-1]["end"] = multi_segments[s]["end"]
                        s += 1
                        continue
            # if the current segment is short and it's the last segment 
            if multi_segments[s] == multi_segments[-1] and len(multi_segments[s]["text"]) + len(complete_sub[-1]["text"]) <= 95 and complete_sub[-1]["start"] - end <= 7:
                print("When the current segment is short and it's the last segment")
                complete_sub[-1]["text"] += " " + multi_segments[s]["text"]
                complete_sub[-1]["end"] = multi_segments[s]["end"]
                s+=1
            else:
                print("Ignore all")
                complete_sub.append(multi_segments[s])
                s+=1
                
            print(complete_sub)
    return complete_sub

