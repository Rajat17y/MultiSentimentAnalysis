import joblib
import os
from tensorflow import keras
import numpy as np

# Get the directory of this script
script_dir = os.path.dirname(os.path.abspath(__file__))

# Load the three saved components with absolute paths
model     = keras.models.load_model(os.path.join(script_dir, 'best_sentiment_model.keras'))
tokenizer = joblib.load(os.path.join(script_dir, 'tokenizerB.joblib'))
encoder   = joblib.load(os.path.join(script_dir, 'encoderB.joblib'))

print("Model, Tokenizer, and Encoder loaded successfully.")
print("Label classes:", encoder.classes_)
# Output → ['negative' 'neutral' 'positive']

import re
from nltk.corpus import stopwords

keep_words = [
    'no','nor','not',
    'don',"don't",'didn',"didn't",'isn',"isn't",'aren',"aren't",
    'wasn',"wasn't",'weren',"weren't",'haven',"haven't",
    'hasn',"hasn't",'hadn',"hadn't",'won',"won't",
    'wouldn',"wouldn't",'shouldn',"shouldn't",
    'couldn',"couldn't",'mightn',"mightn't",
    'mustn',"mustn't",'needn',"needn't",'shan',"shan't",
    'but','against',
    'very','too','more','most',
    'should','could','would','can','will'
]

def expand_contractions(text):
    contractions = {
        "won't":  "will not",    "can't":  "can not",   # ← fixed
        "don't":  "do not",      "doesn't":"does not",
        "didn't": "did not",     "isn't":  "is not",
        "aren't": "are not",     "wasn't": "was not",
        "weren't":"were not",    "haven't":"have not",
        "hasn't": "has not",     "hadn't": "had not",
        "wouldn't":"would not",  "couldn't":"could not",
        "shouldn't":"should not","mightn't":"might not",
        "mustn't":"must not",    "needn't":"need not",
        "shan't": "shall not",   "i'm":    "i am",
        "he's":   "he is",       "she's":  "she is",
        "it's":   "it is",       "we're":  "we are",
        "they're":"they are",    "i've":   "i have",
        "we've":  "we have",     "they've":"they have",
        "i'd":    "i would",     "you'd":  "you would",
        "he'd":   "he would",    "i'll":   "i will",
        "we'll":  "we will",     "they'll":"they will",
        "that's": "that is",
    }
    text = text.lower()
    for contraction, expansion in contractions.items():
        text = text.replace(contraction, expansion)
    return text

NEGATION_WORDS = {'not', 'no', 'never', 'nobody', 'nothing',
                  'neither', 'nor', 'nowhere', 'hardly', 'barely', 'scarcely'}
CLAUSE_PUNCTUATION = {'.', '!', '?', ',', ';', ':'}

def apply_negation_scope(text):
    """
    Tags words after a negation word with _NEG until a clause boundary.
    Must be called on ALREADY-expanded (no contractions) text.
    """
    tokens = re.split(r'(\s+|[.!?,;:])', text)  # split but keep separators
    negating = False
    result = []
    for token in tokens:
        if not token.strip():  # whitespace separator
            result.append(token)
            continue
        if token in CLAUSE_PUNCTUATION:
            negating = False  # reset at boundary
            result.append(token)
        elif token.lower() in NEGATION_WORDS:
            negating = True
            result.append(token)
        elif negating:
            result.append(token + '_NEG')
        else:
            result.append(token)
    return ''.join(result)

def cleanText_single(text):
    all_stopwords = stopwords.words('english')
    stop_words_set = set(all_stopwords) - set(keep_words)

    text   = expand_contractions(str(text).lower())          # Step 1
    text   = apply_negation_scope(text)                      # Step 2
    review = re.sub('[^a-zA-Z_]', ' ', text)                 # Step 3 ← updated
    review = review.split()
    review = [
        word for word in review
        if word not in stop_words_set
        and not (word.endswith('_NEG') and word[:-4] in stop_words_set)  # Step 4 ← added
    ]
    return ' '.join(review)

    import numpy as np
from tensorflow.keras.preprocessing.sequence import pad_sequences

MAX_LEN = 100  # Must match training

def analyze_social_media_sentiments(social_media_dict):
    """
    Processes comments from multiple social media platforms and returns
    sentiment analysis results.

    Args:
        social_media_dict (dict): {
            "platform_name": ["comment1", "comment2", ...]
        }

    Returns:
        dict: {
            "platform_name": [
                ["comment1", "sentiment", confidence],
                ["comment2", "sentiment", confidence],
                ...
            ]
        }
    """
    results = {}

    for platform, comments in social_media_dict.items():
        print(f"\n📱 Processing: {platform} ({len(comments)} comments)...")
        platform_results = []

        for comment in comments:
            # --- Preprocessing ---
            cleaned  = cleanText_single(str(comment))
            sequence = tokenizer.texts_to_sequences([cleaned])
            padded   = pad_sequences(sequence, maxlen=MAX_LEN,
                                     padding='post', truncating='post')

            # --- Prediction ---
            probs      = model.predict(padded, verbose=0)[0]
            pred_idx   = np.argmax(probs)
            sentiment  = encoder.classes_[pred_idx]
            confidence = round(float(probs[pred_idx]) * 100, 2)

            platform_results.append([comment, sentiment, confidence])

        results[platform] = platform_results
        print(f"   ✅ Done — {len(platform_results)} comments processed.")

    return results

def single_prediction(text):
    cleaned = cleanText_single(str(text))
    sequence = tokenizer.texts_to_sequences([cleaned])
    padded = pad_sequences(sequence,maxlen=MAX_LEN,padding='post',truncating='post')
    #Prediction
    probs = model.predict(padded,verbose=0)[0]
    pred_idx = np.argmax(probs)
    sentiment = encoder.classes_[pred_idx]
    confidence = round(float(probs[pred_idx]) * 100, 2)
    return [sentiment,confidence]