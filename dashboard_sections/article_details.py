# dashboard_sections/article_details.py
import streamlit as st
from utils.text_processor import visualize_ner # Import dari utils
import html

def render_article_details(news_items, summarizer):
    """
    Merender daftar artikel dengan detail analisis mendalam (sentimen, ringkasan, NER).
    """
    st.markdown("<h2 style='text-align: center; color: #4CAF50;'>📄 Detail Laporan Artikel</h2>", unsafe_allow_html=True)
    st.markdown("---")

    if not news_items:
        st.info("Tidak ada artikel untuk ditampilkan. Silakan lakukan pencarian terlebih dahulu.")
        return

    for i, article in enumerate(news_items):
        sentiment_label = article['sentiment']['label'].capitalize()
        sentiment_score = article['sentiment']['score']

        # Box untuk setiap artikel dengan warna sentimen
        if sentiment_label.lower() == 'positif':
            st.success(f"**Positif** ({sentiment_score:.2f}) | **{article['title']}**")
        elif sentiment_label.lower() == 'negatif':
            st.error(f"**Negatif** ({sentiment_score:.2f}) | **{article['title']}**")
        else:
            st.info(f"**Netral** ({sentiment_score:.2f}) | **{article['title']}**")

        with st.expander(f"Analisis Mendalam & Ringkasan Artikel {i+1} (Klik untuk Lihat)"):
            st.subheader("📜 Ringkasan Otomatis")
            # Ringkasan hanya dilakukan saat expander dibuka
            with st.spinner("Meringkas artikel..."):
                try:
                    summary = summarizer(article['clean_text'], max_length=150, min_length=30, do_sample=False)[0]['summary_text']
                except IndexError:
                    summary = "Tidak dapat membuat ringkasan untuk artikel ini (teks terlalu pendek atau masalah model)."
                except Exception as e:
                    summary = f"Terjadi kesalahan saat meringkas: {e}"
            st.write(summary)

            st.subheader("🎨 Analisis Entitas dalam Teks")
            # Pastikan teks yang divisualisasikan adalah teks asli dari artikel
            # dan bersihkan sedikit jika ada karakter aneh dari GNews
            display_text = html.escape(article['clean_text']) # Escape HTML entities to prevent injection
            st.markdown(visualize_ner(display_text, article['entities']), unsafe_allow_html=True)

            # Tambahkan info topik jika tersedia
            if 'topic_name' in article:
                st.markdown(f"**Topik Teridentifikasi:** `{article['topic_name']}` (ID: {article['topic_id']})")

            st.markdown("---")
            st.caption(f"**Sumber:** {article.get('publisher', {}).get('title', 'N/A')} | **Tanggal Publikasi:** {article.get('published date', 'N/A')}")
            st.link_button("Baca Artikel Lengkap di Sumber Asli", article['url'])