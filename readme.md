# 🧠 News Intelligence Dashboard

![Streamlit](https://img.shields.io/badge/Powered%20By-Streamlit-red?logo=streamlit)
![Python](https://img.shields.io/badge/Built%20With-Python-blue?logo=python)
![Status](https://img.shields.io/badge/Status-Active-brightgreen)
![Creator](https://img.shields.io/badge/Creator-MS%20Hadianto-orange)

> **Satu Dashboard. Ribuan Berita. Insight Tanpa Batas.**

---

## 🌟 Deskripsi Singkat

**News Intelligence Dashboard** adalah aplikasi berbasis Streamlit untuk:
- Menganalisis ribuan berita secara otomatis
- Mengekstrak sentimen, topik utama, dan entitas kunci
- Menampilkan relasi antar aktor dalam bentuk jaringan interaktif
- Mempermudah pengambilan keputusan berbasis data media

---

## 🚀 Fitur Unggulan

| Modul | Deskripsi |
|-------|-----------|
| 📈 **Tren Sentimen** | Visualisasi skor sentimen harian lengkap dengan event marker |
| 🧠 **Komposisi Sentimen** | Pie chart distribusi sentimen positif, netral, negatif |
| 🧬 **Matriks Entitas** | Scatter plot posisi aktor berdasarkan frekuensi & sentimen |
| 🔍 **Analisis Topik** | Otomatisasi BERTopic + keyword per topik |
| ☁️ **Word Cloud** | Representasi kata dominan dalam kumpulan artikel |
| 🔗 **Jaringan Entitas** | Visualisasi relasi antar entitas (orang, organisasi, lokasi) |

---

## 🛠️ Teknologi

- `Python 3.10+`
- `Streamlit`
- `Plotly`, `Matplotlib`
- `BERTopic`, `spaCy`, `NLTK`
- `streamlit-agraph`
- `pandas`, `numpy`

---

## 🧩 Struktur Folder
📁 Proyek Berita/
├── app.py # Entry point
├── requirements.txt
├── README.md
├── dashboard_sections/
│ ├── aggregate_dashboard.py # Semua tampilan dashboard
│ └── ...
├── data/
│ └── hasil scraping atau olahan
└── utils/
└── preprocessor.py, sentiment.py


---

## ⚙️ Cara Menjalankan Lokal

```bash
git clone https://github.com/mshadianto/news_intelligence.git
cd news_intelligence
pip install -r requirements.txt
streamlit run app.py

👨‍💻 Developer
MS Hadianto
Auditor • Analyst • AI-Enthusiast • Trail Runner
🔗 LinkedIn: https://www.linkedin.com/in/m-sopian-hadianto-se-ak-m-m-cacp%C2%AE-ccfa%C2%AE-qia%C2%AE-ca%C2%AE-grcp%C2%AE-grca%C2%AE-cgp%C2%AE-2ab1a718/

🪪 Lisensi
MIT License © 2025 — MS Hadianto