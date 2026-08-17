import os

# ============================================================
# RENDER CPU CONFIGURATION
# ============================================================

# Force TensorFlow to use CPU only
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"

# Limit TensorFlow CPU thread usage
os.environ["TF_NUM_INTRAOP_THREADS"] = "1"
os.environ["TF_NUM_INTEROP_THREADS"] = "1"

import joblib
import re
import numpy as np

import tensorflow as tf
from tensorflow import keras
from tensorflow.keras.preprocessing.sequence import pad_sequences

from nltk.corpus import stopwords


# ============================================================
# TENSORFLOW CPU CONFIGURATION
# ============================================================

try:
    tf.config.set_visible_devices([], "GPU")
except Exception:
    pass

try:
    tf.config.threading.set_intra_op_parallelism_threads(1)
    tf.config.threading.set_inter_op_parallelism_threads(1)
except Exception:
    pass


# ============================================================
# PATHS
# ============================================================

script_dir = os.path.dirname(os.path.abspath(__file__))

MODEL_PATH = os.path.join(
    script_dir,
    "best_sentiment_model.keras"
)

TOKENIZER_PATH = os.path.join(
    script_dir,
    "tokenizerB.joblib"
)

ENCODER_PATH = os.path.join(
    script_dir,
    "encoderB.joblib"
)


# ============================================================
# GLOBAL OBJECTS
# ============================================================

# IMPORTANT:
# Do NOT load the TensorFlow model when Django starts.
model = None

# These are small and can safely be loaded during import.
tokenizer = joblib.load(TOKENIZER_PATH)
encoder = joblib.load(ENCODER_PATH)

print("Tokenizer and Encoder loaded successfully.")
print("Label classes:", encoder.classes_)


# ============================================================
# LAZY MODEL LOADING
# ============================================================

def get_model():
    """
    Load the TensorFlow model only when it is actually required.

    This prevents Render/Gunicorn from loading the large model
    during Django startup.
    """

    global model

    if model is None:

        print("Loading sentiment model...")

        model = keras.models.load_model(
            MODEL_PATH,
            compile=False
        )

        print("Sentiment model loaded successfully.")

    return model


# ============================================================
# TEXT PREPROCESSING
# ============================================================

keep_words = {
    'no', 'nor', 'not',
    'don', "don't",
    'didn', "didn't",
    'isn', "isn't",
    'aren', "aren't",
    'wasn', "wasn't",
    'weren', "weren't",
    'haven', "haven't",
    'hasn', "hasn't",
    'hadn', "hadn't",
    'won', "won't",
    'wouldn', "wouldn't",
    'shouldn', "shouldn't",
    'couldn', "couldn't",
    'mightn', "mightn't",
    'mustn', "mustn't",
    'needn', "needn't",
    'shan', "shan't",

    'but',
    'against',
    'very',
    'too',
    'more',
    'most',
    'should',
    'could',
    'would',
    'can',
    'will'
}


# Load stopwords ONCE instead of every prediction
all_stopwords = set(stopwords.words('english'))

stop_words_set = all_stopwords - keep_words


# ============================================================
# CONTRACTION EXPANSION
# ============================================================

CONTRACTIONS = {
    "won't": "will not",
    "can't": "can not",
    "don't": "do not",
    "doesn't": "does not",
    "didn't": "did not",
    "isn't": "is not",
    "aren't": "are not",
    "wasn't": "was not",
    "weren't": "were not",
    "haven't": "have not",
    "hasn't": "has not",
    "hadn't": "had not",
    "wouldn't": "would not",
    "couldn't": "could not",
    "shouldn't": "should not",
    "mightn't": "might not",
    "mustn't": "must not",
    "needn't": "need not",
    "shan't": "shall not",
    "i'm": "i am",
    "he's": "he is",
    "she's": "she is",
    "it's": "it is",
    "we're": "we are",
    "they're": "they are",
    "i've": "i have",
    "we've": "we have",
    "they've": "they have",
    "i'd": "i would",
    "you'd": "you would",
    "he'd": "he would",
    "i'll": "i will",
    "we'll": "we will",
    "they'll": "they will",
    "that's": "that is",
}


def expand_contractions(text):

    text = text.lower()

    for contraction, expansion in CONTRACTIONS.items():
        text = text.replace(
            contraction,
            expansion
        )

    return text


# ============================================================
# NEGATION
# ============================================================

NEGATION_WORDS = {
    'not',
    'no',
    'never',
    'nobody',
    'nothing',
    'neither',
    'nor',
    'nowhere',
    'hardly',
    'barely',
    'scarcely'
}

CLAUSE_PUNCTUATION = {
    '.',
    '!',
    '?',
    ',',
    ';',
    ':'
}


def apply_negation_scope(text):

    tokens = re.split(
        r'(\s+|[.!?,;:])',
        text
    )

    negating = False
    result = []

    for token in tokens:

        if not token.strip():
            result.append(token)
            continue

        if token in CLAUSE_PUNCTUATION:

            negating = False
            result.append(token)

        elif token.lower() in NEGATION_WORDS:

            negating = True
            result.append(token)

        elif negating:

            result.append(
                token + '_NEG'
            )

        else:

            result.append(token)

    return ''.join(result)


# ============================================================
# TEXT CLEANING
# ============================================================

def cleanText_single(text):

    text = expand_contractions(
        str(text).lower()
    )

    text = apply_negation_scope(text)

    review = re.sub(
        r'[^a-zA-Z_]',
        ' ',
        text
    )

    review = review.split()

    review = [
        word
        for word in review
        if word not in stop_words_set
        and not (
            word.endswith('_NEG')
            and word[:-4] in stop_words_set
        )
    ]

    return ' '.join(review)


# ============================================================
# MODEL CONFIGURATION
# ============================================================

MAX_LEN = 100


# ============================================================
# SINGLE PREDICTION
# ============================================================

def single_prediction(text):

    # Load model only when needed
    model_instance = get_model()

    cleaned = cleanText_single(
        str(text)
    )

    sequence = tokenizer.texts_to_sequences(
        [cleaned]
    )

    padded = pad_sequences(
        sequence,
        maxlen=MAX_LEN,
        padding='post',
        truncating='post'
    )

    # Prediction
    probs = model_instance.predict(
        padded,
        verbose=0
    )[0]

    pred_idx = int(
        np.argmax(probs)
    )

    sentiment = encoder.classes_[
        pred_idx
    ]

    confidence = round(
        float(probs[pred_idx]) * 100,
        2
    )

    return [
        sentiment,
        confidence
    ]


# ============================================================
# SOCIAL MEDIA BATCH PREDICTION
# ============================================================

def analyze_social_media_sentiments(
    social_media_dict
):

    # Load model once
    model_instance = get_model()

    results = {}

    for platform, comments in social_media_dict.items():

        print(
            f"\n📱 Processing: "
            f"{platform} "
            f"({len(comments)} comments)..."
        )

        platform_results = []

        # ----------------------------------------------------
        # PREPROCESS ALL COMMENTS FIRST
        # ----------------------------------------------------

        cleaned_comments = [
            cleanText_single(str(comment))
            for comment in comments
        ]

        # ----------------------------------------------------
        # TOKENIZE ALL COMMENTS
        # ----------------------------------------------------

        sequences = tokenizer.texts_to_sequences(
            cleaned_comments
        )

        padded = pad_sequences(
            sequences,
            maxlen=MAX_LEN,
            padding='post',
            truncating='post'
        )

        # ----------------------------------------------------
        # BATCH PREDICTION
        # ----------------------------------------------------

        probs_batch = model_instance.predict(
            padded,
            batch_size=32,
            verbose=0
        )

        # ----------------------------------------------------
        # PROCESS RESULTS
        # ----------------------------------------------------

        for comment, probs in zip(
            comments,
            probs_batch
        ):

            pred_idx = int(
                np.argmax(probs)
            )

            sentiment = encoder.classes_[
                pred_idx
            ]

            confidence = round(
                float(probs[pred_idx]) * 100,
                2
            )

            platform_results.append(
                [
                    comment,
                    sentiment,
                    confidence
                ]
            )

        results[platform] = platform_results

        print(
            f"   ✅ Done — "
            f"{len(platform_results)} "
            f"comments processed."
        )

    return results