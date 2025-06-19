# dashboard_sections/header.py
import streamlit as st
from datetime import datetime

def render_header():
    """
    Merender bagian header aplikasi dengan logo dan deskripsi.
    """
    col_header1, col_header2 = st.columns([1, 3])

    with col_header1:
        st.image("assets/logo MSH.png", width=150)

    with col_header2:
        st.markdown(f"""
        <div style="text-align: right;">
            <p style="font-size: 1.2em; font-weight: bold; color: #4CAF50;">Dashboard Intelijen Berita v5.0</p>
            <p style="font-size: 0.9em; color: #E0E0E0;">Ditenagai oleh AI untuk Analisis Mendalam</p>
        </div>
        """, unsafe_allow_html=True)
        st.markdown(f"""
        ### Tentang Aplikasi Ini
        Di tengah lautan informasi yang tak terbatas, memahami narasi besar di balik berita bisa menjadi sebuah tantangan.
        Aplikasi ini lahir untuk mengubah kebisingan berita menjadi sinyal yang jelas.

        Dengan menggabungkan kekuatan **Analisis Sentimen**, **Ekstraksi Entitas (NER)**, dan **Peringkasan Otomatis**,
        ditambah **Analisis Topik** revolusioner, dashboard ini bukan sekadar pembaca berita, melainkan asisten intelijen pribadi Anda untuk membedah topik apa pun secara mendalam dan efisien.

        *Dibuat oleh: **MS Hadianto** | Versi Intelijen v5.0 (Build {datetime.now().strftime('%Y%m%d')})*
        """)
    st.markdown("---") # Garis pemisah