# models/loader.py
import streamlit as st
from transformers import pipeline
from bertopic import BERTopic
from sklearn.feature_extraction.text import TfidfVectorizer # Untuk BERTopic

@st.cache_resource(show_spinner=False)
def load_sentiment_model():
    # st.write("Memuat model Analisis Sentimen...") # Kita hilangkan ini untuk tampilan lebih bersih
    return pipeline("sentiment-analysis", model="taufiqdp/indonesian-sentiment")

@st.cache_resource(show_spinner=False)
def load_summarizer_model():
    # st.write("Memuat model Peringkas Berita...")
    return pipeline("summarization", model="panggi/t5-base-indonesian-summarization-cased")

@st.cache_resource(show_spinner=False)
def load_ner_model():
    # st.write("Memuat model Ekstraksi Entitas...")
    return pipeline("ner", model="cahya/bert-base-indonesian-NER", grouped_entities=True)

@st.cache_resource(show_spinner=False)
def load_topic_model():
    # st.write("Memuat model Topic Modeling...")
    # Menggunakan representasi TF-IDF sebagai fallback untuk BERTopic
    # Jika Anda memiliki model sentence-transformer yang spesifik untuk bahasa Indonesia, bisa diubah di sini
    vectorizer_model = TfidfVectorizer(stop_words=None, ngram_range=(1, 2), min_df=5)
    # Model BERTopic dasar. Untuk performa lebih baik, bisa pakai model bahasa Indonesia yang lebih besar
    return BERTopic(
        language="indonesian",
        calculate_probabilities=True,
        # Untuk model yang lebih cepat atau jika ingin mengontrol embeddings:
        # embedding_model="indonesian-sbert", # Contoh: "indonesian-sbert" jika ada model sentence-transformers yang diinstal
        # vectorizer_model=vectorizer_model,
        verbose=False
    )

# Catatan: Relationship Extraction akan lebih kompleks, mungkin membutuhkan model terpisah
# atau pendekatan berbasis aturan/pola yang lebih canggih. Untuk tahap awal, kita fokus ke NER dan Topic.