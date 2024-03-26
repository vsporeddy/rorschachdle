import random
from flask import request
from flask import Flask, jsonify
from flask_cors import CORS
import nltk
from nltk.corpus import stopwords
from nltk.sentiment import SentimentIntensityAnalyzer
from nltk.tokenize import word_tokenize
from datetime import datetime
import shelve
import spacy
from nltk.stem.wordnet import WordNetLemmatizer

nltk.download('vader_lexicon')
nltk.download('stopwords')
nltk.download('punkt')
nltk.download('wordnet')
nltk.download('omw-1.4')
nlp = spacy.load("en_core_web_md")
sia = SentimentIntensityAnalyzer()
lmtzr = WordNetLemmatizer()

app = Flask(__name__)
CORS(app)

start_date = '2024-03-03'

with open('lawful_words.txt', 'r') as file:
    content = file.read()
    lawful_list = [word.strip() for word in content.split(',')]

with open('chaotic_words.txt', 'r') as file:
    content = file.read()
    chaotic_list = [word.strip() for word in content.split(',')]

with open('good_words.txt', 'r') as file:
    content = file.read()
    good_list = [word.strip() for word in content.split(',')]

with open('evil_words.txt', 'r') as file:
    content = file.read()
    evil_list = [word.strip() for word in content.split(',')]

lawful_embeddings = [nlp(word) for word in lawful_list]
chaotic_embeddings = [nlp(word) for word in chaotic_list]
good_embeddings = [nlp(word) for word in good_list]
evil_embeddings = [nlp(word) for word in evil_list]

def create_json_grid():
    grid = []
    for row in range(5):
        grid_row = []
        for col in range(5):
            grid_row.append(random.choice([0, 1]))
        grid.append(grid_row)

    #1/3 chance of a random red square
    if random.random() < 1/3:
        flat_index = random.randint(0, 24)
        row_index = flat_index // 5
        col_index = flat_index % 5
        grid[row_index][col_index] = 3
    return grid

def get_spacy_order_scores(user_text):
    user_doc = nlp(user_text)

    lawful_score = max(word.similarity(user_doc) for word in lawful_embeddings)
    chaotic_score = max(word.similarity(user_doc) for word in chaotic_embeddings)

    return lawful_score, chaotic_score

def get_spacy_ethical_scores(user_text):
    user_doc = nlp(user_text)

    good_score = max(word.similarity(user_doc) for word in good_embeddings)
    evil_score = max(word.similarity(user_doc) for word in evil_embeddings)

    return good_score, evil_score


def get_order_alignment(text):
    # Any chaotic-lawful gap below this threshold will be considered neutral
    threshold = 0.06
    lawful, chaotic, neutral = "Lawful", "Chaotic", "Neutral"

    spacy_lawful_score, spacy_chaotic_score = get_spacy_order_scores(text)
    if spacy_lawful_score - spacy_chaotic_score > threshold:
        return lawful
    if spacy_chaotic_score - spacy_lawful_score > threshold:
        return chaotic
    return neutral

def get_ethical_alignment(text):
    sentiment_score = sia.polarity_scores(text)['compound']
    good, evil, neutral = "Good", "Evil", "Neutral"

    if sentiment_score > 0:
        return good
    if sentiment_score < 0:
        return evil
    threshold = 0.06
    spacy_good_score, spacy_evil_score = get_spacy_ethical_scores(text)
    if spacy_good_score - spacy_evil_score > threshold:
        return good
    if spacy_evil_score - spacy_good_score > threshold:
        return evil
    return neutral

@app.route("/alignment", methods=["GET"])
def get_alignment():
    text = request.args.get('text')
    text = ' '.join(sanitize(text))
    order_alignment = get_order_alignment(text)
    ethical_alignment = get_ethical_alignment(text)

    if order_alignment == ethical_alignment:
        return "True Neutral"
    return f"{order_alignment} {ethical_alignment}"

def sanitize(text):
    tokens = word_tokenize(text)  # Tokenize into words
    stop_words = set(stopwords.words('english'))
    words = set([lmtzr.lemmatize(w.lower()) for w in tokens if w.isalpha() and w not in stop_words])
    return words

@app.route("/unique", methods=["GET"])
def get_uniqueness():
    date_key = request.args.get('date')
    text = request.args.get('text')
    embedding = nlp(text)
    max_similarity = 0
    most_similar_text = ""
    all_text = load_text(date_key)
    store_text(date_key, text)

    for other in all_text:
        similarity = embedding.similarity(nlp(other))
        if similarity > max_similarity:
            most_similar_text = other
            max_similarity = similarity

    unique = max_similarity < 0.6
    return "My interpretation was unique!" if unique else f"My interpretation was {max_similarity*100:.0f}% similar to ||{most_similar_text}||!"

def store_json_grid(date_key, grid):
  with shelve.open('json_grid') as db:
    db[date_key] = grid

def load_json_grid(date_key):
  with shelve.open('json_grid') as db:
    return db.get(date_key)

def store_text(date_key, text):
    all_text = load_text(date_key)
    all_text.update(text)
    with shelve.open('words') as db:
        db[date_key] = all_text

def load_text(date_key):
    with shelve.open('words') as db:
        return db.get(date_key, set())

@app.route("/number", methods=["GET"])
def get_number():
    date_key = request.args.get('date')
    format_str = '%Y-%m-%d'
    date1_dt = datetime.strptime(start_date, format_str)
    date2_dt = datetime.strptime(date_key, format_str)

    # Calculate the difference (a timedelta object)
    difference = date2_dt - date1_dt

    return str(difference.days)

@app.route('/')
def hello():
    return "sup"

@app.route("/json-grid", methods=["GET"])
def get_json_grid():
    date_key = request.args.get('date')

    json_grid = load_json_grid(date_key)
    if not json_grid:
        json_grid = create_json_grid()
        store_json_grid(date_key, json_grid)

    return jsonify(json_grid)
