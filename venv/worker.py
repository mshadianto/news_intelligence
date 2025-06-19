# worker.py - Otomatisasi Ambil Berita Harian + NLTK Path Fix
import json
import os
import re
import sqlite3
from datetime import datetime
import nltk
nltk.data.path.append(r"C:\\Users\\use\\AppData\\Roaming\\nltk_data")
nltk.download('punkt')
from nltk.tokenize import sent_tokenize
from transformers import pipeline
from gnews import GNews

# --- Konfigurasi ---
DB_FILE = os.path.join(os.getcwd(), "news_intelligence.db")
TOPIC_FILE = os.path.join(os.getcwd(), "topic_config.json")

ASPECT_KEYWORDS = {
    "kebijakan": ["pemerintah", "kebijakan", "regulasi"],
    "harga": ["harga", "mahal", "murah"],
    "lingkungan": ["lingkungan", "emisi", "polusi", "hijau"]
}

# --- Load model ---
sentiment_analyzer = pipeline("sentiment-analysis", model="taufiqdp/indonesian-sentiment")
summarizer = pipeline("summarization", model="panggi/t5-base-indonesian-summarization-cased")

# --- Fungsi ABSA ---
def absa_analysis(clean_text, aspect_dict):
    sentences = sent_tokenize(clean_text)
    result = []
    for aspect, keywords in aspect_dict.items():
        related_sentences = [s for s in sentences if any(k in s.lower() for k in keywords)]
        for sent in related_sentences:
            sentiment = sentiment_analyzer(sent)[0]
            result.append({
                "aspect": aspect,
                "related_text": sent,
                "sentiment_label": sentiment['label'],
                "sentiment_score": sentiment['score']
            })
    return result

# --- Fungsi Utama ---
def load_topics():
    with open(TOPIC_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def fetch_news(query, period="1d", max_results=10):
    return GNews(language='id', period=period, max_results=max_results).get_news(query)

def article_exists(conn, url):
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM articles WHERE url = ?", (url,))
    return cursor.fetchone() is not None

def init_db():
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS articles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            url TEXT UNIQUE,
            description TEXT,
            clean_text TEXT,
            published_date TIMESTAMP,
            publisher TEXT,
            sentiment_label TEXT,
            sentiment_score REAL,
            summary TEXT,
            topic_query TEXT,
            fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS article_aspects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            article_id INTEGER,
            aspect TEXT,
            related_text TEXT,
            sentiment_label TEXT,
            sentiment_score REAL,
            FOREIGN KEY(article_id) REFERENCES articles(id)
        )
        """)
        conn.commit()

def run_worker():
    init_db()
    topics = load_topics()
    print(f"[INFO] Memulai worker untuk topik: {topics}")

    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        for topic in topics:
            news_items = fetch_news(topic, period="1d", max_results=15)
            print(f"[TOPIK] {topic} - {len(news_items)} berita ditemukan.")

            for article in news_items:
                if not article_exists(conn, article['url']):
                    clean_text = f"{article['title']}. {re.sub('<[^<]+?>', '', article.get('description', ''))}"
                    sentiment_result = sentiment_analyzer(clean_text)[0]
                    summary = summarizer(clean_text, max_length=150, min_length=30, do_sample=False)[0]['summary_text']

                    cursor.execute("""
                        INSERT INTO articles (title, url, description, clean_text, published_date, publisher, sentiment_label, sentiment_score, summary, topic_query)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        article['title'], article['url'], article.get('description', ''), clean_text,
                        article['published date'], article.get('publisher', {}).get('title', 'N/A'),
                        sentiment_result['label'], sentiment_result['score'], summary, topic
                    ))

                    article_id = cursor.execute("SELECT id FROM articles WHERE url = ?", (article['url'],)).fetchone()[0]
                    absa_results = absa_analysis(clean_text, ASPECT_KEYWORDS)
                    for absa in absa_results:
                        cursor.execute("""
                            INSERT INTO article_aspects (article_id, aspect, related_text, sentiment_label, sentiment_score)
                            VALUES (?, ?, ?, ?, ?)
                        """, (article_id, absa['aspect'], absa['related_text'], absa['sentiment_label'], absa['sentiment_score']))
        conn.commit()
    print("[SELESAI] Worker selesai menyimpan semua berita baru.")

if __name__ == "__main__":
    run_worker()
