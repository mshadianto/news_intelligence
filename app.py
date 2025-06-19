# app.py
# =================================================================
# KODE APLIKASI DASHBOARD INTELIJEN BERITA v6.0 (Fitur Super Canggih)
# Oleh: M.S. Hadianto dengan panduan & perbaikan dari Gemini
# Perbaikan Utama: Arsitektur Modular, UI/UX Canggih, Topic Modeling, Relationship Extraction, Event Markers
# =================================================================

import streamlit as st
import pandas as pd
import sentencepiece # Penting untuk model Hugging Face
from datetime import datetime

# Import komponen dari folder models
from models.loader import load_sentiment_model, load_summarizer_model, load_ner_model, load_topic_model

# Import utilitas dari folder utils
from utils.news_fetcher import fetch_news
from utils.text_processor import clean_text_for_analysis
from utils.analysis_engine import analyze_news_data

# Import komponen dashboard dari folder dashboard_sections
from dashboard_sections.header import render_header
from dashboard_sections.search_input import render_search_input
from dashboard_sections.aggregate_dashboard import render_aggregate_dashboard
from dashboard_sections.article_details import render_article_details

# --- Konfigurasi Aplikasi Streamlit ---
st.set_page_config(
    page_title="Dashboard Intelijen Berita v6.0",
    page_icon="👑",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Injeksi CSS Kustom
with open("assets/custom.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# --- LOADING MODEL AI (Dilakukan sekali saat aplikasi pertama kali diakses) ---
with st.spinner("Menginisialisasi Sistem Intelijen AI Tingkat Lanjut (Ini mungkin butuh waktu pertama kali)..."):
    sentiment_analyzer = load_sentiment_model()
    summarizer = load_summarizer_model()
    ner_analyzer = load_ner_model()
    topic_model = load_topic_model()
st.success("Sistem Intelijen AI v6.0 siap beroperasi! Mari berburu insight.")
st.markdown("---")

# --- STATE MANAGEMENT (Penting untuk mempertahankan data antar interaksi) ---
if 'news_items' not in st.session_state:
    st.session_state.news_items = []
if 'processed_data' not in st.session_state:
    st.session_state.processed_data = None
if 'last_query' not in st.session_state:
    st.session_state.last_query = ""
if 'last_period' not in st.session_state:
    st.session_state.last_period = ""
if 'last_num_articles' not in st.session_state:
    st.session_state.last_num_articles = 0

# --- RENDER HEADER APLIKASI ---
render_header()

# --- RENDER BAGIAN PENCARIAN ---
query, period_code, num_articles, generate_button_pressed = render_search_input()

# --- LOGIKA GENERASI LAPORAN INTELIJEN ---
if generate_button_pressed or (
    query != st.session_state.last_query or
    period_code != st.session_state.last_period or
    num_articles != st.session_state.last_num_articles
):
    if query:
        st.session_state.news_items = []
        st.session_state.processed_data = None

        with st.spinner(f"Melakukan Operasi Intelijen: Mengumpulkan {num_articles} berita terkait '{query}' dan menganalisis secara mendalam..."):
            raw_news_items = fetch_news(query, period=period_code, max_results=num_articles)

            if not raw_news_items:
                st.error("Intelijen tidak menemukan berita relevan. Coba ganti kata kunci atau rentang waktu Anda.")
                st.session_state.last_query = ""
                st.stop()

            # Bersihkan dan tambahkan clean_text ke setiap artikel
            for article in raw_news_items:
                article['clean_text'] = clean_text_for_analysis(article.get('title', ''), article.get('description', ''))

            # Lakukan analisis mendalam
            st.session_state.news_items = raw_news_items
            st.session_state.processed_data = analyze_news_data(
                st.session_state.news_items,
                sentiment_analyzer,
                ner_analyzer,
                topic_model
            )
        st.success("Laporan Intelijen Selesai! Insight strategis siap disajikan.")

        # Update last search parameters
        st.session_state.last_query = query
        st.session_state.last_period = period_code
        st.session_state.last_num_articles = num_articles
    else:
        st.warning("Masukkan Topik Intelijen untuk memulai operasi analisis.")

# --- TAMPILKAN DASHBOARD DAN DETAIL ---
if st.session_state.processed_data:
    render_aggregate_dashboard(st.session_state.processed_data)
    render_article_details(st.session_state.news_items, summarizer)
elif not generate_button_pressed and not st.session_state.news_items:
    st.info("Dashboard Intelijen Anda menunggu perintah. Masukkan topik di atas dan klik 'Hasilkan Laporan Intelijen & Analisis' untuk memulai misi.")


# --- Footer ---
st.markdown("---")
st.caption("""
**Disclaimer Intelijen Tingkat Tinggi:** Hasil analisis ini dihasilkan oleh sistem AI dan merupakan interpretasi prediksi berdasarkan data teks yang tersedia.
Informasi ini bersifat intelijen mentah dan tidak selalu mencerminkan opini atau fakta absolut.
**Selalu lakukan verifikasi silang** dari berbagai sumber untuk keputusan strategis.
""")
# Version is now in header.py