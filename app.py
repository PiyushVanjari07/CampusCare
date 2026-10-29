import csv
import json
import os
from datetime import datetime

from flask import Flask, render_template, request, jsonify
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__)

THRESHOLD = 0.25
LOG_FILE = os.path.join(BASE_DIR, "chat_log.csv")
FEEDBACK_FILE = os.path.join(BASE_DIR, "feedback_log.csv")
FALLBACK = (
    "Sorry, I could not understand that. Please try asking about admissions, "
    "fees, exams, timetable, scholarships, library, study plans, attendance or placements, "
    "or contact the college office."
)

# 1. Load knowledge base
with open(os.path.join(BASE_DIR, "faq.json"), encoding="utf-8") as f:
    FAQ = json.load(f)

# 2. Flatten all sample questions and remember which FAQ entry owns them
questions, owners = [], []
for index, item in enumerate(FAQ):
    for q in item["questions"]:
        questions.append(q.lower())
        owners.append(index)

# 3. Build TF-IDF matrix once at start-up
# Common filler words (English + Hinglish) are ignored so they do not cause wrong matches
STOP_WORDS = [
    "what", "is", "the", "how", "to", "for", "of", "a", "an", "are", "can", "i",
    "me", "my", "do", "does", "in", "on", "and", "when", "where", "which",
    "kya", "hai", "ka", "ki", "ke", "ko", "se", "mein", "me", "karna", "kaise",
]
vectorizer = TfidfVectorizer(ngram_range=(1, 2), stop_words=STOP_WORDS)
matrix = vectorizer.fit_transform(questions)


def get_answer(text):
    vec = vectorizer.transform([text.lower()])
    scores = cosine_similarity(vec, matrix)[0]
    best = scores.argmax()
    score = float(scores[best])
    if score < THRESHOLD:
        return FALLBACK, "unknown", round(score, 2)
    item = FAQ[owners[best]]
    return item["answer"], item["tag"], round(score, 2)


def log_chat(message, tag, score):
    new_file = not os.path.exists(LOG_FILE)
    with open(LOG_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if new_file:
            writer.writerow(["time", "message", "topic", "score"])
        writer.writerow([datetime.now().strftime("%Y-%m-%d %H:%M:%S"), message, tag, score])


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/ask", methods=["POST"])
def ask():
    data = request.get_json(silent=True) or {}
    message = (data.get("message") or "").strip()
    if not message:
        return jsonify({"reply": "Please type a question.", "topic": "empty", "score": 0})
    reply, tag, score = get_answer(message)
    log_chat(message, tag, score)
    return jsonify({"reply": reply, "topic": tag, "score": score})


@app.route("/feedback", methods=["POST"])
def feedback():
    data = request.get_json(silent=True) or {}
    fb_type = data.get("type", "Suggestion")
    rating = data.get("rating", "5")
    message = (data.get("message") or "").strip()
    if not message:
        return jsonify({"status": "error", "message": "Message cannot be empty."}), 400
    new_file = not os.path.exists(FEEDBACK_FILE)
    with open(FEEDBACK_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if new_file:
            writer.writerow(["time", "type", "rating", "message"])
        writer.writerow([datetime.now().strftime("%Y-%m-%d %H:%M:%S"), fb_type, rating, message])
    return jsonify({"status": "ok", "message": "Feedback submitted successfully!"})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
