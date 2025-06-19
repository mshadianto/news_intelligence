# utils/news_fetcher.py
import streamlit as st
from gnews import GNews

def fetch_news(query, period='7d', max_results=10):
    """
    Mengambil berita dari Google News berdasarkan query dan periode waktu.
    """
    try:
        google_news = GNews(language='id', country='ID', period=period)
        google_news.max_results = max_results
        return google_news.get_news(query)
    except Exception as e:
        st.error(f"Gagal mengambil berita. Pastikan koneksi internet stabil atau coba ganti query. Error: {e}")
        return []