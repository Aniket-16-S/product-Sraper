import time
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
os.environ["TRANSFORMERS_VERBOSITY"] = "critical"    # Suppress warnings and logs shown during setup and initialisation.
os.environ["HF_HUB_DISABLE_PROGRESS_BARS"] = "1" 
import logging
import warnings
tf_logger = logging.getLogger('tensorflow')
tf_logger.setLevel(logging.ERROR)
warnings.filterwarnings("ignore")
from sentence_transformers import SentenceTransformer, util
import json
import os

"""
cacher.check( new_Query ) -> Query (present in cache ), Presence = True  or new_Query, presence = False

"""
model = SentenceTransformer('all-MiniLM-L6-v2', cache_folder='models/')

BEST = 0.7
CONFUSION_LOW = 0.5
WORST = 5

CACHE_FILE = 'cache_test.json'

if os.path.exists(CACHE_FILE):
    with open(CACHE_FILE, 'r') as f:
        try :
            query_cache = json.load(f)
        except Exception as e :
            query_cache = {}
else:
    query_cache = {}



def preprocess(query):
    ## Comming Soon . . .
    return query

def are_similar(sent1, sent2):
    emb1 = model.encode(sent1, convert_to_tensor=True)
    emb2 = model.encode(sent2, convert_to_tensor=True)
    similarity = util.cos_sim(emb1, emb2).item()
    return  similarity

def handle_query(new_query):
    new_query = preprocess(new_query)
    words = new_query.split()
    low_thresh = len(words) <= 3
    all = {}

    for old_query, group in query_cache.items():
        for cached_variant in group:
            comp = preprocess(cached_variant)
            sim_score = are_similar(new_query, comp)
            all[(old_query, cached_variant)] = sim_score 

    all = sorted(all.items(), key=lambda kv: kv[1], reverse=True)

    for (old_query, variant), score in all:
        oq = old_query.lower().split()
        nq = new_query.lower().split()

        if any(g in oq for g in ["mens", "boys"]) and any(g in nq for g in ["womens", "ladies", "girls"]):
            continue
        if any(g in oq for g in ["womens", "ladies", "girls"]) and any(g in nq for g in ["mens", "boys"]):
            continue

        if score >= BEST:
            return old_query, True
        elif CONFUSION_LOW <= score < BEST and not low_thresh:
            query_cache[old_query].append(new_query)
            save_cache()
            return old_query, True
        elif WORST < score <= BEST and low_thresh:
            if len(new_query) == len(old_query) :
                if new_query.lower() == old_query.lower() :
                    return old_query, True, score
                else :
                    return new_query, False, str(score) + old_query
            query_cache[old_query].append(new_query)
            save_cache()
            return old_query, True
    
    query_cache[new_query] = [new_query]
    save_cache()
    return new_query, False


def save_cache():
    with open(CACHE_FILE, 'w') as f:
        json.dump(query_cache, f, indent=2)


def check(s_query:str) :
    return handle_query(s_query)
