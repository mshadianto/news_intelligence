# dashboard_sections/search_input.py
import streamlit as st

def render_search_input():
    """
    Merender bagian input pencarian berita.
    Mengembalikan query, selected_period_code, dan num_articles.
    """
    st.header("Pencarian Berita Canggih")
    PERIOD_OPTIONS = {"24 Jam Terakhir": "1d", "Seminggu Terakhir": "7d", "Sebulan Terakhir": "1m", "Tiga Bulan Terakhir": "3m"}
    
    col_input1, col_input2, col_input3 = st.columns([2, 1, 1])
    with col_input1:
        query = st.text_input("Topik Intelijen (Kata Kunci Berita):", value="Ibu Kota Nusantara")
    with col_input2:
        selected_period_label = st.selectbox("Rentang Waktu Laporan:", options=list(PERIOD_OPTIONS.keys()))
    with col_input3:
        num_articles = st.number_input("Jumlah Artikel Maksimal:", min_value=5, max_value=100, value=20)

    period_code = PERIOD_OPTIONS[selected_period_label]
    
    # Tombol aksi utama
    if st.button("🚀 Hasilkan Laporan Intelijen & Analisis", type="primary", use_container_width=True):
        return query, period_code, num_articles, True # True menandakan tombol ditekan
    
    return query, period_code, num_articles, False # False jika tombol belum ditekan