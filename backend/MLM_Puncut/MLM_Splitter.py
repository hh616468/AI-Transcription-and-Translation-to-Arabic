# Copyright 2024 VICOMTECH (FUNDACIÓN CENTRO DE TECNOLOGÍAS DE INTERACCIÓN VISUAL Y COMUNICACIONES VICOMTECH). All rights reserved.
# DO NOT DISTRIBUTE.

# Unless required by applicable law or agreed to in writing, software is distributed "AS IS",
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.

# The code below illustrates the subtitle segmentation approach described in the following paper:
#
#   David Ponce, Thierry Etchegoyhen, and Victor Ruiz. 2023. Unsupervised Subtitle Segmentation with Masked Language Models. 
#   In Proceedings of the 61st Annual Meeting of the Association for Computational Linguistics (Volume 2: Short Papers), pages 771–781, Toronto, Canada. 
#   Association for Computational Linguistics.
#
# Although functional, this code snippet does not implement the full approach and is meant only for educational purposes. 

# Author: David Ponce adponce@vicomtech.org 

from transformers import pipeline
from transformers import AutoTokenizer
import json
import torch
from backend.MLM_Puncut.conjunctions import get_conjunctions


def load_model():
    device = "cuda" if torch.cuda.is_available() else "cpu" # Check if GPU is available
    #model_name ="google-bert/bert-base-uncased"
    model_name ="bert-base-multilingual-uncased"

    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = pipeline('fill-mask', model=model_name,
                                tokenizer=tokenizer, device=device)
    mask_token = tokenizer.mask_token
    return model, mask_token

def score_text(text, new_starts ,lang_code, new_ends, model , mask_token ,min_words=7, max_words=12 , separators = ['.', ',', '?', '!', ':', ';']):
    # Split into words
    words = text.split()
    # Get all possible splitting candidates
    candidates = [{"text": words[0:i], "remaining": words[i:], "last_token": words[i-1][-1] , "starts": new_starts[0:i] , "ends": new_ends[0:i]} for i in range(1, len(words))]
    # Filter out candidates that are too short or too long
    # You can filter by words, characters, or any other metric
    # This is bascially a list loop
    candidates = [c for c in candidates if len(c["text"]) >= min_words and len(c["text"]) <= max_words]
    # filter candidates that end with a conjuction
    conj = get_conjunctions(lang_code)
    candidates = [c for c in candidates if c["text"][-1] not in conj]
    if len(candidates) == 0:
        # No candidates left to fill the min_words requirement, return the original text
        # You can implements methods to try to avoid this by not using just a greedy algorithm to get the best split
        return [{"text": text, "remaining": "", "last_token": text[-1], "score": 0 , "starts": new_starts , "ends": new_ends}]
    
    # Join the words back into strings
    candidates = [{"text": ' '.join(c["text"]), "remaining": ' '.join(c["remaining"]), "last_token": c["last_token"], "starts": c["starts"], "ends": c["ends"]} for c in candidates]
    # If a candidate ends with a separator, remove the separator - we want to predict it so it shouldn't be part of the input
    for c in candidates:
        c["input_text"] = c["text"][:-1] if c["last_token"] in separators else c["text"]    
    # We are going to create the inputs by inserting a [MASK] token between the two parts of the split
    inputs = [f"{c['input_text']} {mask_token} {c['remaining']}" for c in candidates]

    # Get the separators probabilities for each candidate
    scores = model(inputs, targets=separators , batch_size=16)
    # If there is only one candidate, wrap it in a list (pipeline returns a dict otherwise)
    if len(inputs) == 1:
        scores = [scores]

    # Get only the maximum score for each candidate
    for i, c in enumerate(candidates):
        c["score"] = max([s["score"] for s in scores[i]])
        
        # If the score was a separator, increase it by 1 (heuristic to prefer splitting at separators)
        if c["last_token"] in separators:
            c["score"] += 1
    return candidates



