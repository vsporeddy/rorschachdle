import random
from flask import request
from flask import Flask
from flask_cors import CORS
import nltk
from nltk.corpus import stopwords
from nltk.sentiment import SentimentIntensityAnalyzer
from nltk.tokenize import word_tokenize
from datetime import datetime
import shelve
import spacy


nltk.download('vader_lexicon')
nltk.download('stopwords')
nltk.download('punkt')
nlp = spacy.load("en_core_web_md")
sia = SentimentIntensityAnalyzer()

app = Flask(__name__)
CORS(app)

start_date = '2024-03-03'

with open('lawful_words.txt', 'r') as file:
    content = file.read()
    lawful_list = [word.strip() for word in content.split(',')]

with open('chaotic_words.txt', 'r') as file:
    content = file.read()
    chaotic_list = [word.strip() for word in content.split(',')]

lawful_embeddings = [nlp(word) for word in lawful_list]
chaotic_embeddings = [nlp(word) for word in chaotic_list]

def create_grid():
    grid = ""
    for row in range(4):
        for col in range(5):
            grid += random.choice(["⬛", "⬜"])
        grid += "\n"
    return grid

def get_spacy_order_scores(user_text):
    user_doc = nlp(user_text)

    lawful_score = max(word.similarity(user_doc) for word in lawful_embeddings)
    chaotic_score = max(word.similarity(user_doc) for word in chaotic_embeddings)

    return lawful_score, chaotic_score


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
    return neutral

@app.route("/alignment", methods=["GET"])
def get_alignment():
    text = request.args.get('text')
    order_alignment = get_order_alignment(text)
    ethical_alignment = get_ethical_alignment(text)

    if order_alignment == ethical_alignment:
        return "True Neutral"
    return f"{order_alignment} {ethical_alignment}"

@app.route("/unique", methods=["GET"])
def get_uniqueness():
    date_key = request.args.get('date')
    text = request.args.get('text')
    tokens = word_tokenize(text)  # Tokenize into words
    stop_words = set(stopwords.words('english'))

    # Filter out stop words and basic punctuation
    words = set([w.lower() for w in tokens if w.isalpha() and w not in stop_words])
    all_words = load_words(date_key)
    unique = not (words & all_words)
    store_words(date_key, words)
    return "My interpretation was unique!" if unique else "My interpretation was not unique 😔"

def store_grid(date_key, grid):
  with shelve.open('grid') as db:
    db[date_key] = grid

def load_grid(date_key):
  with shelve.open('grid') as db:
    return db.get(date_key)

def store_words(date_key, words):
    all_words = load_words(date_key)
    all_words.update(words)
    with shelve.open('words') as db:
        db[date_key] = all_words

def load_words(date_key):
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

@app.route("/daily-grid", methods=["GET"])
def get_daily_grid():
    date_key = request.args.get('date')

    grid = load_grid(date_key)
    if not grid:
        grid = create_grid()
        store_grid(date_key, grid)

    return grid
