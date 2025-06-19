# dashboard_sections/aggregate_dashboard.py
"""
Renders the aggregate news‑intelligence dashboard with multiple tabs:
1. Sentiment trend & composition
2. Entity frequency‑sentiment matrix
3. Automatic topic analysis
4. Word cloud
5. Entity‑relationship network graph

Updates:
- Replace `st.agraph` → `agraph` (from streamlit_agraph).
- Add explicit `import pandas as pd` (used for relation table).
"""

import streamlit as st
import plotly.express as px
import matplotlib.pyplot as plt
import pandas as pd  # NEW: required for relation_df
from streamlit_agraph import agraph, Node, Edge, Config  # graph visualisation


def render_aggregate_dashboard(processed_data):
    """Render the aggregate dashboard section."""
    st.markdown(
        "<h2 style='text-align: center; color: #4CAF50;'>\U0001F4CA Dashboard Intelijen Agregat</h2>",
        unsafe_allow_html=True,
    )
    st.markdown("---")

    # Tabs for better organisation
    tab1, tab2, tab3, tab4, tab5 = st.tabs(
        [
            "\U0001F4C8 Sentimen & Tren",
            "\U0001F4A1 Matriks Entitas",
            "\U0001F4DA Analisis Topik",
            "\u2601\ufe0f Word Cloud",
            "\U0001F517 Jaringan Relasi Entitas",
        ]
    )

    # ------------------------------------------------------------------
    # Tab 1 – Sentiment Trend & Composition
    # ------------------------------------------------------------------
    with tab1:
        st.subheader("\U0001F4C8 Tren Sentimen & Komposisi")
        col_s1, col_s2 = st.columns([2, 1])

        # Line chart – sentiment trend
        with col_s1:
            st.markdown("### Tren Sentimen Harian")
            if (
                "sentiment_trend_df" in processed_data
                and not processed_data["sentiment_trend_df"].empty
            ):
                df_trend = processed_data["sentiment_trend_df"]
                fig_trend = px.line(
                    df_trend,
                    x=df_trend.index,
                    y="average_score",
                    labels={"index": "Tanggal", "average_score": "Skor Sentimen Rata-rata"},
                    title="Evolusi Sentimen Terhadap Topik",
                    line_shape="spline",
                    render_mode="svg",
                )
                fig_trend.update_layout(
                    hovermode="x unified",
                    plot_bgcolor="#1E1E1E",
                    paper_bgcolor="#1E1E1E",
                    font_color="#E0E0E0",
                )
                fig_trend.update_xaxes(showgrid=True, gridwidth=0.5, gridcolor="#3A3A3A")
                fig_trend.update_yaxes(
                    showgrid=True, gridwidth=0.5, gridcolor="#3A3A3A", range=[-1, 1]
                )

                # Event markers (optional)
                if "sentiment_events" in processed_data and processed_data["sentiment_events"]:
                    for event_date in processed_data["sentiment_events"]:
                        event_score = df_trend.loc[event_date]["average_score"]
                        fig_trend.add_scatter(
                            x=[event_date],
                            y=[event_score],
                            mode="markers",
                            marker=dict(size=12, color="red", symbol="star"),
                            name=f"Event ({event_date.strftime('%Y-%m-%d')})",
                            hoverinfo="text",
                            hovertext=(
                                f"**Event Penting:** {event_date.strftime('%Y-%m-%d')}<br>Sentimen: {event_score:.2f}"
                            ),
                        )
                    st.warning(
                        "⭐️ Titik merah menunjukkan potensi peristiwa yang memicu perubahan sentimen signifikan."
                    )

                st.plotly_chart(fig_trend, use_container_width=True)
            else:
                st.info("Tidak ada data untuk menampilkan tren sentimen.")

        # Pie chart – sentiment composition
        with col_s2:
            st.markdown("### Komposisi Sentimen")
            if (
                "sentiment_comp_df" in processed_data
                and not processed_data["sentiment_comp_df"].empty
            ):
                fig_pie = px.pie(
                    processed_data["sentiment_comp_df"],
                    values="Jumlah",
                    names="Kategori",
                    title="Distribusi Sentimen Berita",
                    color_discrete_map={
                        "positif": "#28a745",
                        "netral": "#ffc107",
                        "negatif": "#dc3545",
                    },
                )
                fig_pie.update_layout(
                    plot_bgcolor="#1E1E1E",
                    paper_bgcolor="#1E1E1E",
                    font_color="#E0E0E0",
                )
                st.plotly_chart(fig_pie, use_container_width=True)
            else:
                st.info("Tidak ada data untuk menampilkan komposisi sentimen.")

    # ------------------------------------------------------------------
    # Tab 2 – Entity Matrix (frequency vs sentiment)
    # ------------------------------------------------------------------
    with tab2:
        st.subheader("\U0001F4A1 Matriks Frekuensi vs. Sentimen Entitas")
        st.info(
            "Menganalisis posisi aktor dan institusi dalam pemberitaan. "
            "Semakin kanan semakin sering disebut, semakin atas semakin positif."
        )
        if "matrix_df" in processed_data and not processed_data["matrix_df"].empty:
            df_matrix = processed_data["matrix_df"]
            fig_matrix = px.scatter(
                df_matrix,
                x="Frekuensi",
                y="Avg_Sentiment",
                text="Entitas",
                title="Posisi Aktor & Institusi dalam Pemberitaan",
                labels={
                    "Avg_Sentiment": "← Cenderung Negatif | Cenderung Positif →",
                    "Frekuensi": "Frekuensi Penyebutan",
                },
                size="Frekuensi",
                color="Avg_Sentiment",
                color_continuous_scale="RdYlGn",
                hover_name="Entitas",
                size_max=60,
            )
            fig_matrix.add_hline(
                y=0,
                line_dash="dash",
                line_color="grey",
                annotation_text="Sentimen Netral",
                annotation_position="bottom right",
                annotation_font_color="#E0E0E0",
            )

            median_freq = df_matrix["Frekuensi"].median()
            fig_matrix.add_vline(
                x=median_freq,
                line_dash="dash",
                line_color="grey",
                annotation_text=f"Median Frekuensi ({median_freq:.0f})",
                annotation_position="top right",
                annotation_font_color="#E0E0E0",
            )

            fig_matrix.update_traces(textposition="top center")
            fig_matrix.update_layout(
                plot_bgcolor="#1E1E1E",
                paper_bgcolor="#1E1E1E",
                font_color="#E0E0E0",
                xaxis_title="Frekuensi Penyebutan",
                yaxis_title="Sentimen Rata-rata",
            )
            st.plotly_chart(fig_matrix, use_container_width=True)
        else:
            st.warning("Tidak cukup data entitas (minimal 2x muncul) untuk membuat matriks ini.")

    # ------------------------------------------------------------------
    # Tab 3 – Topic Analysis
    # ------------------------------------------------------------------
    with tab3:
        st.subheader("\U0001F4DA Analisis Topik Otomatis")
        st.info("Sistem secara otomatis mengidentifikasi tema-tema utama yang muncul dari berita.")
        if (
            "topic_info_df" in processed_data and not processed_data["topic_info_df"].empty
        ):
            st.dataframe(
                processed_data["topic_info_df"].set_index("Topic").style.format(
                    {"Jumlah_Artikel": "{:,}"}
                ),
                use_container_width=True,
            )

            if (
                "topic_keywords" in processed_data
                and not processed_data["topic_keywords"].empty
            ):
                st.subheader("Kata Kunci Utama per Topik")
                st.dataframe(
                    processed_data["topic_keywords"].set_index("Topic"),
                    use_container_width=True,
                )

            st.markdown("---")
            st.subheader("Visualisasi Topik (Interaktif)")
            st.info("Visualisasi BERTopic dapat diaktifkan di sini.")
            fig_topic_dist = px.bar(
                processed_data["topic_info_df"],
                x="Topik_Utama",
                y="Jumlah_Artikel",
                title="Distribusi Topik Artikel",
                color_discrete_sequence=px.colors.qualitative.Plotly,
            )
            fig_topic_dist.update_layout(
                plot_bgcolor="#1E1E1E",
                paper_bgcolor="#1E1E1E",
                font_color="#E0E0E0",
            )
            st.plotly_chart(fig_topic_dist, use_container_width=True)
        else:
            st.warning(
                "Tidak ada topik yang dapat diidentifikasi. Mungkin jumlah artikel terlalu sedikit atau topiknya terlalu beragam."
            )

    # ------------------------------------------------------------------
    # Tab 4 – Word Cloud
    # ------------------------------------------------------------------
    with tab4:
        st.subheader("\u2601\ufe0f Word Cloud Topik Utama")
        st.info(
            "Representasi visual kata-kata yang paling sering muncul dalam berita terkait topik Anda."
        )
        if "wordcloud" in processed_data:
            fig, ax = plt.subplots(figsize=(10, 5))
            ax.imshow(processed_data["wordcloud"], interpolation="bilinear")
            ax.axis("off")
            st.pyplot(fig)
        else:
            st.info("Tidak cukup teks untuk membuat word cloud.")

    # ------------------------------------------------------------------
    # Tab 5 – Entity Relationship Graph
    # ------------------------------------------------------------------
    with tab5:
        st.subheader("\U0001F517 Jaringan Relasi Entitas")
        st.info("Melihat bagaimana entitas (Orang, Organisasi, Lokasi) saling terhubung dalam berita.")

        G = processed_data.get("entity_graph")
        if G and G.number_of_nodes() > 0:
            nodes: list[Node] = []
            edges: list[Edge] = []

            # Nodes
            for node_id in G.nodes():
                nodes.append(
                    Node(
                        id=node_id,
                        label=node_id,
                        size=20,
                        font={"color": "#E0E0E0"},
                    )
                )

            # Edges
            for u, v, data in G.edges(data=True):
                weight = data.get("weight", 1)
                edges.append(
                    Edge(
                        source=u,
                        target=v,
                        value=weight,
                        title=f"Koneksi: {weight} kali",
                        color={"color": "#4CAF50", "highlight": "#5cb85c"},
                        width=min(5, weight),
                    )
                )

            # Graph config
            config = Config(
                width=700,
                height=500,
                directed=False,
                physics=True,
                edges={"smooth": True, "color": {"inherit": "from"}},
                nodes={"font": {"size": 12, "color": "#E0E0E0"}},
                interaction={"hover": True, "zoomView": True},
            )

            # ---> Fixed: call agraph directly
            agraph(nodes=nodes, edges=edges, config=config)

            # Relation table
            st.markdown("---")
            st.subheader("Tabel Relasi Ditemukan")
            if (
                "relation_counts" in processed_data
                and processed_data["relation_counts"]
            ):
                relation_df = pd.DataFrame(
                    processed_data["relation_counts"].items(),
                    columns=["Entitas_Pair", "Frekuensi"],
                )
                relation_df["Entitas_1"] = relation_df["Entitas_Pair"].apply(lambda x: x[0])
                relation_df["Entitas_2"] = relation_df["Entitas_Pair"].apply(lambda x: x[1])
                relation_df = relation_df[["Entitas_1", "Entitas_2", "Frekuensi"]].sort_values(
                    by="Frekuensi", ascending=False
                )
                st.dataframe(relation_df, use_container_width=True)
            else:
                st.info("Tidak ada relasi entitas signifikan yang ditemukan (atau frekuensi di bawah threshold).")
        else:
            st.info("Tidak cukup entitas untuk membangun jaringan relasi. Pastikan ada artikel yang diproses.")
