import random
import io
from flask import Flask, send_file
from flask import request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
import nltk
from nltk.corpus import stopwords
from nltk.sentiment import SentimentIntensityAnalyzer
from nltk.tokenize import word_tokenize
from PIL import Image, ImageDraw, ImageFilter
from noise import pnoise2
from datetime import datetime
import spacy


nltk.download('vader_lexicon')
nltk.download('stopwords')
nltk.download('punkt')

sia = SentimentIntensityAnalyzer()

app = Flask(__name__)
CORS(app)

SQLALCHEMY_DATABASE_URI = "mysql+mysqlconnector://{username}:{password}@{hostname}/{databasename}".format(
    username="",
    password="",
    hostname="",
    databasename="",
)
app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI
app.config["SQLALCHEMY_POOL_RECYCLE"] = 299
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)
db.create_all()

start_date = '2024-03-03'

grids = {}
all_words = {}
numbers = {}
number = 3

def create_grid():
    global number
    grid = ""
    for row in range(4):
        for col in range(5):
            grid += random.choice(["⬛", "⬜"])
        grid += "\n"
    number += 1
    return grid

def generate_rorschach(width=500, height=500, seed=None):
    """Generates a Rorschach-like image with fractals and dark gray inkblots."""

    random.seed(seed)  # Optional to set a specific seed for reproducibility

    image = Image.new("RGB", (width, height), (255, 255, 255))  # White background
    draw = ImageDraw.Draw(image)

    for _ in range(5):
        x_start = random.randint(0, width)
        y_start = random.randint(0, height)
        noise_size = width * 2  # Scale noise for interesting texture
        noise_img = Image.new('L', (noise_size, noise_size)) # Grayscale
        draw = ImageDraw.Draw(noise_img)
        for i in range(noise_size):
            for j in range(noise_size):
                n = pnoise2(i/noise_size, j/noise_size, octaves=2, base=random.randint(0, 255))
                n = (n + 1) / 2  # Map to 0-1 range
                color = int(n * 128 + 128)  # Map noise to grayscale (0-255)
                color = int(color * 0.2)

                draw.point((i, j), fill=color)

        # Place on original canvas and apply thresholding/color adjustments as needed
        noise_img = noise_img.resize((width, height))
        image.paste(noise_img, (x_start, y_start))

    # Mirror onto the right half
    right_half = image.crop((width // 2, 0, width, height))
    right_half = right_half.transpose(Image.FLIP_LEFT_RIGHT)
    image.paste(right_half, (width // 2, 0))

    # Add slight blurring for a softer look
    image = image.filter(ImageFilter.GaussianBlur(radius=1))

    return image

def get_humorous_rating(sentiment_score):
    """Converts a sentiment score into a humorous rating, with finer increments."""

    ratings = {
        -1.0: "Ultimate Doom Prophet",
        -0.95: "Apocalyptic Visionary",
        -0.85: "Angsty Edgelord",
        -0.8: "Pessimistic Poet",
        -0.75: "Brooding Philosopher",
        -0.7: "Existential Analyst",
        -0.65: "Cynical Critic",
        -0.6: "Sarcastic Soul",
        -0.55: "Skeptical Realist",
        -0.5: "World-Weary Observer",
        -0.45: "Mildly Disgruntled",
        -0.4: "Subtly Skeptical",
        -0.3: "Somewhat Apathetic",
        -0.25: "Ambivalently Indifferent",
        -0.2: "Cautiously Optimistic",
        -0.15: "Reservedly Hopeful",
        -0.1: "Contemplative Realist",
        -0.02: "Hopeful Idealist",
        0.0: "Realistically Neutral",
        0.02: "Quietly Content",
        0.1: "Cheerful Optimist",
        0.15: "Gently Enthusiastic",
        0.2: "Smiling Sunflower",
        0.25: "Sunshine and Rainbows",
        0.3: "Playful Puppy",
        0.35: "Joyful Dreamer",
        0.4: "Sparkling Sprite",
        0.45: "Blissful Butterfly",
        0.5: "Giggling Gerbil",
        0.55: "Beaming Bunny",
        0.6: "Fluffy Bunny Overlord",
        0.65: "Radiating Positivity",
        0.7: "Exploding With Positivity",
        0.75: "Bursting with Bliss",
        0.8: "Euphorically Enthusiastic",
        0.85: "Boundlessly Blessed",
        0.9: "Celestial Cheerleader",
        0.95: "Unicorn Riding a Rainbow",
        1.0: "Cosmic Ray of Sunshine"
    }

    # Find the correct sentiment category
    for threshold, rating in ratings.items():
        if sentiment_score <= threshold:
            return rating

def calculate_uniqueness(text):
    nlp = spacy.load('en_core_web_md')  # Or your preferred model

    doc = nlp(text.lower())
    total_similarity = 0
    word_count = 0

    for token in doc:
        if token.is_alpha and not token.is_stop:
            most_similar_word = find_most_similar(token, all_words)
            if most_similar_word is not None:
                similarity = token.similarity(most_similar_word)
                total_similarity += similarity
                word_count += 1
            else:
                # Unique word (consider a higher bonus)
                total_similarity += 1
                word_count += 1

    # Update all_words with the new words
    update_all_words(doc, all_words)

    if word_count > 0:
        average_similarity = total_similarity / word_count
        return 1 - average_similarity  # Map to a uniqueness score
    else:
        return 1 # Handle the case of no relevant words

def find_most_similar(token, word_dict):
    max_similarity = 0
    most_similar_word = None

    for word, count in word_dict.items():
        if token.has_vector and word.has_vector:  # Check if words have vectors
            similarity = token.similarity(word)
            if similarity > max_similarity:
                max_similarity = similarity
                most_similar_word = word

    return most_similar_word

def update_all_words(doc, word_dict):
    for token in doc:
        if token.is_alpha and not token.is_stop:
              word_dict[token] = word_dict.get(token, 0) + 1

def get_uniqueness_category(uniqueness_score):
    """Converts a uniqueness score into a humorous category based on its value."""

    categories = {
        0.0: "Unoriginal Sheep",
        0.1: "Follower of the Flock",
        0.2: "Conventionally Conventional",
        0.3: "Predictably Plain",
        0.4: "Distinctly Dull",
        0.5: "Uninspiringly Uninspired",
        0.6: "Somewhat Similar",
        0.7: "Reasonably Repetitive",
        0.8: "Mildly Mainstream",
        0.9: "Creatively Conventional",
        1.0: "Refreshingly Original"
    }

    # Find the correct category (inequality reversed)
    for threshold, category in categories.items():
        if uniqueness_score <= threshold:
            return category

    # Handle unexpected scores (shouldn't happen)
    return "Uniqueness Anomaly"

@app.route("/uniqueness", methods=["GET"])
def get_uniqueness():
    text = request.args.get('text')
    tokens = word_tokenize(text)  # Tokenize into words
    stop_words = set(stopwords.words('english'))

    # Filter out stop words and basic punctuation
    words = [w.lower() for w in tokens if w.isalpha() and w not in stop_words]
    word_counts = {}
    for word in words:
        word_counts[word] = word_counts.get(word, 0) + 1

    # Calculate the uniqueness rating
    uniqueness_score = 0.0
    total_word_count = max(sum(all_words.values()), 1)  # Total count of all words

    for word, count in word_counts.items():
        word_frequency = all_words.get(word, 0) / total_word_count
        word_uniqueness = 1 - word_frequency
        uniqueness_score += word_uniqueness * count  # Weight by word's count

    for word, count in word_counts.items():
        all_words[word] = all_words.get(word, 0) + count

    average_uniqueness = uniqueness_score / len(word_counts)
    return get_uniqueness_category(average_uniqueness)

@app.route("/sentiment", methods=["GET"])
def get_sentiment():
    text = request.args.get('text')
    sentiment_score = sia.polarity_scores(text)['compound']
    return get_humorous_rating(sentiment_score)

@app.route("/number", methods=["GET"])
def get_number():
    date_key = request.args.get('date')
    format_str = '%Y-%m-%d'
    date1_dt = datetime.strptime(start_date, format_str)
    date2_dt = datetime.strptime(date_key, format_str)

    # Calculate the difference (a timedelta object)
    difference = date2_dt - date1_dt

    return str(difference.days)

@app.route('/rorschach')
def get_rorschach():
    """Generates and returns a Rorschach image."""

    image = generate_rorschach()

    # Save to in-memory buffer
    img_io = io.BytesIO()
    image.save(img_io, 'PNG')
    img_io.seek(0)

    return send_file(img_io, mimetype='image/png')

@app.route('/')
def hello():
    return "sup"

@app.route("/daily-grid", methods=["GET"])
def get_daily_grid():
    date_key = request.args.get('date')
    if date_key in grids.keys():
        return grids[date_key]
    grid = create_grid()
    grids[date_key] = grid
    return grid
