# =================================================================
# KODE APLIKASI DASHBOARD INTELIJEN BERITA v4.2 (Dengan Header)
# Oleh: M.S. Hadianto dengan panduan & perbaikan dari Gemini
# Perbaikan Utama: Penambahan header dengan logo dan deskripsi
# =================================================================

import streamlit as st
from transformers import pipeline
from gnews import GNews
import pandas as pd
import sentencepiece # Meskipun tidak dipanggil langsung, ini penting untuk model
import re
from datetime import datetime
from collections import Counter # Not explicitly used, but good to keep if planning to use for word counts
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import plotly.express as px

# --- Konfigurasi Aplikasi ---
st.set_page_config(page_title="Dashboard Intelijen Berita", page_icon="👑", layout="wide")

# --- FUNGSI-FUNGSI MODEL (Menggunakan cache untuk efisiensi) ---
@st.cache_resource
def load_sentiment_model():
    st.write("Memuat model Analisis Sentimen...")
    return pipeline("sentiment-analysis", model="taufiqdp/indonesian-sentiment")

@st.cache_resource
def load_summarizer_model():
    st.write("Memuat model Peringkas Berita...")
    return pipeline("summarization", model="panggi/t5-base-indonesian-summarization-cased")

@st.cache_resource
def load_ner_model():
    st.write("Memuat model Ekstraksi Entitas...")
    return pipeline("ner", model="cahya/bert-base-indonesian-NER", grouped_entities=True)

# --- FUNGSI BANTUAN ---
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

def visualize_ner(text, entities):
    """
    Menyorot entitas yang ditemukan dalam teks dengan warna berbeda.
    """
    if not entities: return text
    # Sort entities by their start position to avoid overlapping issues
    entities = sorted(entities, key=lambda x: x['start'])
    
    last_idx, highlighted_text = 0, ""
    colors = {"PER": "#ffadad", "ORG": "#a0c4ff", "GPE": "#fdffb6", "LOC": "#fdffb6"}
    entity_map = {"PER": "Orang", "ORG": "Organisasi", "GPE": "Lokasi", "LOC": "Lokasi"}
    
    for entity in entities:
        start, end, label = entity['start'], entity['end'], entity['entity_group']
        
        # Add text before the current entity
        highlighted_text += text[last_idx:start]
        
        # Get color and label for the entity
        color, label_text = colors.get(label, "#e0e0e0"), entity_map.get(label, label)
        
        # Add the highlighted entity
        highlighted_text += f"<mark style='background-color: {color}; padding: 0.2em 0.3em; margin: 0 0.25em; line-height: 1.5; border-radius: 0.25em;'>"
        highlighted_text += f"{text[start:end]} <span style='font-size: 0.8em; font-weight: bold; color: #555;'>{label_text}</span></mark>"
        last_idx = end
        
    # Add any remaining text after the last entity
    highlighted_text += text[last_idx:]
    return highlighted_text

# --- TAMPILAN UTAMA APLIKASI ---
st.title("👑 Dashboard Intelijen Berita")

# --- AWAL BAGIAN HEADER BARU ---
col_header1, col_header2 = st.columns([1, 3])

with col_header1:
    # Pastikan file 'logo MSH.png' ada di folder yang sama dengan script aplikasi
    st.image("logo MSH.png", width=150) 

with col_header2:
    st.markdown("""
    ### Tentang Aplikasi Ini
    Di tengah lautan informasi yang tak terbatas, memahami narasi besar di balik berita bisa menjadi sebuah tantangan. 
    Aplikasi ini lahir untuk mengubah kebisingan berita menjadi sinyal yang jelas.
    
    Dengan menggabungkan kekuatan **Analisis Sentimen**, **Ekstraksi Entitas (NER)**, dan **Peringkasan Otomatis**, 
    dashboard ini bukan sekadar pembaca berita, melainkan asisten intelijen pribadi Anda untuk membedah topik apa pun secara mendalam dan efisien.
    
    *Dibuat oleh: **MS Hadianto***
    """)

# Tambahkan garis pemisah
st.markdown("---")
# --- AKHIR BAGIAN HEADER BARU ---

# Load AI models with a spinner for user feedback
with st.spinner("Mempersiapkan model AI... Ini mungkin butuh waktu lama saat pertama kali dijalankan."):
    sentiment_analyzer = load_sentiment_model()
    summarizer = load_summarizer_model()
    ner_analyzer = load_ner_model()
st.success("Semua model AI telah siap!")

# Initialize session state variables if they don't exist
if 'news_items' not in st.session_state: st.session_state.news_items = []
if 'processed_data' not in st.session_state: st.session_state.processed_data = None

st.header("Pencarian Berita")
PERIOD_OPTIONS = {"24 Jam Terakhir": "1d", "Seminggu Terakhir": "7d", "Sebulan Terakhir": "1m", "Tiga Bulan Terakhir": "3m"}
col_input1, col_input2, col_input3 = st.columns([2, 1, 1])
with col_input1:
    query = st.text_input("Masukkan Topik Berita:", value="Ibu Kota Nusantara")
with col_input2:
    selected_period_label = st.selectbox("Pilih Rentang Waktu:", options=list(PERIOD_OPTIONS.keys()))
with col_input3:
    num_articles = st.number_input("Jumlah Berita:", min_value=5, max_value=100, value=20)

if st.button("🚀 Hasilkan Dashboard & Analisis", type="primary", use_container_width=True):
    # Reset session state for new search
    st.session_state.news_items = []
    st.session_state.processed_data = None
    
    period_code = PERIOD_OPTIONS[selected_period_label]
    news_items = fetch_news(query, period=period_code, max_results=num_articles)

    if not news_items:
        st.error("Tidak ada berita yang ditemukan untuk topik dan periode yang dipilih.")
        st.stop() 

    with st.spinner("Melakukan analisis agregat pada semua berita... Ini mungkin perlu waktu sejenak."):
        all_sentiments, all_text = [], ""
        entity_sentiments = {}

        for article in news_items:
            # Clean text by concatenating title and description, removing HTML tags
            clean_text = f"{article['title']}. {re.sub('<[^<]+?>', '', article.get('description', ''))}"
            article['clean_text'] = clean_text
            all_text += clean_text + " " # Accumulate all text for word cloud

            # Perform sentiment analysis
            sentiment_result = sentiment_analyzer(clean_text)[0]
            article['sentiment'] = sentiment_result
            
            # Adjust score for plotting: positive is positive, negative is negative, neutral is near zero
            score = sentiment_result['score']
            if sentiment_result['label'].lower() == 'negatif':
                score = -score # Make negative scores truly negative for better visualization
            elif sentiment_result['label'].lower() == 'netral':
                score = 0 # Neutral scores are zero
                
            all_sentiments.append({'label': sentiment_result['label'], 'date': article['published date'], 'score': score})
            
            # Perform NER and associate entities with their sentiment scores
            entities = ner_analyzer(clean_text)
            article['entities'] = entities
            for e in entities:
                if e['entity_group'] in ['PER', 'ORG']: # Only consider Persons and Organizations for entity sentiment
                    word = e['word'].strip()
                    if word not in entity_sentiments: entity_sentiments[word] = []
                    entity_sentiments[word].append(score)
        
        st.session_state.news_items = news_items # Store news items in session state
        
        processed_data = {}
        
        if all_sentiments:
            sentiment_df = pd.DataFrame(all_sentiments)

            # Sentiment Composition
            sentiment_comp_df = sentiment_df['label'].value_counts().reset_index()
            sentiment_comp_df.columns = ['Kategori', 'Jumlah']
            sentiment_comp_df['Persentase'] = (sentiment_comp_df['Jumlah'] / len(sentiment_df) * 100).round(1)
            processed_data['sentiment_comp_df'] = sentiment_comp_df

            # Sentiment Trend
            sentiment_df['date'] = pd.to_datetime(sentiment_df['date'], utc=True)
            sentiment_trend_df = sentiment_df[['date', 'score']].set_index('date').sort_index()
            processed_data['sentiment_trend_df'] = sentiment_trend_df

        # Entity Matrix Data
        # Filter entities that appear at least twice to make the matrix more meaningful
        matrix_data = [{'Entitas': entity, 'Frekuensi': len(scores), 'Avg_Sentiment': sum(scores)/len(scores)} 
                       for entity, scores in entity_sentiments.items() if len(scores) > 1]
        processed_data['matrix_df'] = pd.DataFrame(matrix_data) if matrix_data else pd.DataFrame()

        # Word Cloud Data
        if all_text.strip():
            # You might want to expand this stopword list or use a pre-defined Indonesian stopword list
            stopwords = set(['dan', 'di', 'ke', 'dari', 'yang', 'ini', 'itu', 'atau', 'telah', 'akan', 'dengan', 'untuk', 'pada', 'juga', 'tersebut'])
            processed_data['wordcloud'] = WordCloud(width=800, height=400, background_color='white', stopwords=stopwords).generate(all_text)
        
        st.session_state.processed_data = processed_data # Store processed data in session state

# --- TAMPILAN DASHBOARD ---
if st.session_state.processed_data:
    st.header("📊 Dashboard Intelijen Agregat")
    data = st.session_state.processed_data

    col_dash1, col_dash2 = st.columns([2, 1])
    with col_dash1:
        st.subheader("📈 Tren Sentimen")
        if 'sentiment_trend_df' in data and not data['sentiment_trend_df'].empty:
            # Use Plotly for better interactivity
            fig_trend = px.line(data['sentiment_trend_df'], x=data['sentiment_trend_df'].index, y='score',
                                 labels={'x':'Tanggal', 'score':'Skor Sentimen (Positif ke Negatif)'},
                                 title='Tren Sentimen Harian')
            fig_trend.update_layout(hovermode="x unified")
            st.plotly_chart(fig_trend, use_container_width=True)
        else:
            st.info("Tidak ada data untuk menampilkan tren sentimen.")
    with col_dash2:
        st.subheader("📊 Komposisi Sentimen")
        if 'sentiment_comp_df' in data and not data['sentiment_comp_df'].empty:
            fig_pie = px.pie(data['sentiment_comp_df'], values='Jumlah', names='Kategori',
                             title='Distribusi Sentimen Berita',
                             color_discrete_map={'positif':'green', 'netral':'gold', 'negatif':'red'})
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.info("Tidak ada data untuk menampilkan komposisi sentimen.")

    st.markdown("---")
    
    col_dash3, col_dash4 = st.columns([1.5, 1])
    with col_dash3:
        st.subheader("💡 Matriks Frekuensi vs. Sentimen")
        if 'matrix_df' in data and not data['matrix_df'].empty:
            fig = px.scatter(data['matrix_df'], x='Frekuensi', y='Avg_Sentiment', text='Entitas', 
                             title="Posisi Aktor & Institusi dalam Pemberitaan",
                             labels={'Avg_Sentiment': 'Sentimen Rata-rata (Negatif <-> Positif)', 
                                     'Frekuensi': 'Frekuensi Penyebutan'},
                             size='Frekuensi', color='Avg_Sentiment', color_continuous_scale='RdYlGn',
                             hover_name="Entitas") # Add hover_name for better tooltip
            fig.add_hline(y=0, line_dash="dash", line_color="grey", annotation_text="Sentimen Netral", 
                          annotation_position="bottom right")
            fig.add_vline(x=data['matrix_df']['Frekuensi'].median(), line_dash="dash", line_color="grey", 
                          annotation_text=f"Median Frekuensi ({data['matrix_df']['Frekuensi'].median():.0f})", 
                          annotation_position="top right")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Tidak cukup data entitas (minimal 2x muncul) untuk membuat matriks.")
            
    with col_dash4:
        st.subheader("☁️ Word Cloud Topik")
        if 'wordcloud' in data:
            fig, ax = plt.subplots(figsize=(10,5))
            ax.imshow(data['wordcloud'], interpolation='bilinear')
            ax.axis("off")
            st.pyplot(fig)
        else:
            st.info("Tidak cukup teks untuk membuat word cloud.")

# --- TAMPILKAN DAFTAR ARTIKEL ---
if st.session_state.news_items:
    st.header("📄 Detail Artikel Berita")
    for i, article in enumerate(st.session_state.news_items):
        sentiment_label = article['sentiment']['label'].capitalize()
        sentiment_score = article['sentiment']['score']
        
        # Display article title with sentiment color coding
        if sentiment_label.lower() == 'positif':
            st.success(f"**Positif** ({sentiment_score:.2f}) | {article['title']}")
        elif sentiment_label.lower() == 'negatif':
            st.error(f"**Negatif** ({sentiment_score:.2f}) | {article['title']}")
        else:
            st.info(f"**Netral** ({sentiment_score:.2f}) | {article['title']}")

        with st.expander(f"Lihat Analisis Mendalam & Ringkasan (Artikel {i+1})"):
            with st.spinner("Memproses..."):
                # Summarization might fail if clean_text is too short or malformed
                try:
                    summary = summarizer(article['clean_text'], max_length=150, min_length=30, do_sample=False)[0]['summary_text']
                except IndexError: # Handle cases where summarizer might return empty list
                    summary = "Tidak dapat membuat ringkasan untuk artikel ini."
                except Exception as e:
                    summary = f"Terjadi kesalahan saat meringkas: {e}"

                st.subheader("📜 Ringkasan Otomatis")
                st.write(summary)
                
                st.subheader("🎨 Analisis Entitas dalam Teks")
                st.markdown(visualize_ner(article['clean_text'], article['entities']), unsafe_allow_html=True)
                
                # Use st.link_button for a more prominent link
                st.caption(f"Sumber: {article.get('publisher', {}).get('title', 'N/A')}")
                st.link_button("Baca Artikel Lengkap", article['url'])

# --- Footer ---
st.markdown("---")
st.caption("""
**Disclaimer:** Hasil analisis ini dihasilkan oleh model AI dan merupakan prediksi berdasarkan data teks. 
Hasil ini tidak selalu mencerminkan opini atau fakta absolut dan hanya boleh digunakan sebagai referensi.
""")
app_version = f"4.2 (Branded Build {datetime.now().strftime('%Y%m%d')})"
st.caption(f"Developed by MS Hadianto | Versi {app_version}")
