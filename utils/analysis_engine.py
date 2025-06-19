# utils/analysis_engine.py
import pandas as pd
from datetime import datetime, timedelta
from collections import Counter
from wordcloud import WordCloud
import numpy as np
import networkx as nx # NEW: Untuk representasi graf
import re # NEW: Untuk pembersihan teks lebih lanjut di relasi

def analyze_news_data(news_items, sentiment_analyzer, ner_analyzer, topic_model):
    """
    Melakukan analisis sentimen, NER, topic modeling, dan relationship extraction pada kumpulan berita.
    Mengembalikan data yang sudah diproses untuk dashboard.
    """
    all_sentiments_data = []
    all_text_for_wordcloud = []
    entity_sentiments = {} # Untuk matriks frekuensi vs sentimen
    documents_for_topic_model = [] # Untuk BERTopic
    all_sentences = [] # NEW: Untuk relationship extraction
    
    # Store all entities for relationship extraction across all articles
    # This will be a list of lists of entities per sentence for each article
    entities_per_sentence_global = [] 

    for article_idx, article in enumerate(news_items):
        clean_text = article['clean_text'] # Sudah dibersihkan di text_processor
        
        # 1. Sentiment Analysis
        sentiment_result = sentiment_analyzer(clean_text)[0]
        article['sentiment'] = sentiment_result
        score = sentiment_result['score']
        if sentiment_result['label'].lower() == 'negatif':
            score = -score
        elif sentiment_result['label'].lower() == 'netral':
            score = 0
        all_sentiments_data.append({'label': sentiment_result['label'], 'date': article['published date'], 'score': score})
        
        # 2. Named Entity Recognition (NER)
        entities = ner_analyzer(clean_text)
        article['entities'] = entities
        
        # Process entities for Entity Matrix and Relationship Extraction
        article_sentences = re.split(r'[.!?]', clean_text) # Split into sentences
        current_article_entities_per_sentence = []

        for sentence in article_sentences:
            if not sentence.strip(): continue
            all_sentences.append(sentence.strip())
            
            sentence_entities = []
            for e in entities:
                # Check if entity is within the current sentence
                if e['start'] >= clean_text.find(sentence) and e['end'] <= clean_text.find(sentence) + len(sentence):
                    word = e['word'].strip()
                    if len(word) > 2 and not any(c.isdigit() for c in word): # Filter short or numeric entities
                        if e['entity_group'] in ['PER', 'ORG', 'GPE', 'LOC']: # Consider these for relations
                            sentence_entities.append({'text': word, 'type': e['entity_group']})
                        
                        # Only consider PER (Orang) and ORG (Organisasi) for entity sentiment matrix
                        if e['entity_group'] in ['PER', 'ORG']:
                            if word not in entity_sentiments: entity_sentiments[word] = []
                            entity_sentiments[word].append(score)
            
            if sentence_entities:
                current_article_entities_per_sentence.append(sentence_entities)
        
        if current_article_entities_per_sentence:
            entities_per_sentence_global.append({'article_idx': article_idx, 'sentences_entities': current_article_entities_per_sentence})
            
        # 3. Data untuk Topic Modeling
        documents_for_topic_model.append(clean_text)
        
        # 4. Data untuk Word Cloud
        all_text_for_wordcloud.append(clean_text)

    processed_data = {}

    # --- Proses Sentimen ---
    if all_sentiments_data:
        sentiment_df = pd.DataFrame(all_sentiments_data)
        
        # Komposisi Sentimen
        sentiment_comp_df = sentiment_df['label'].value_counts().reset_index()
        sentiment_comp_df.columns = ['Kategori', 'Jumlah']
        sentiment_comp_df['Persentase'] = (sentiment_comp_df['Jumlah'] / len(sentiment_df) * 100).round(1)
        processed_data['sentiment_comp_df'] = sentiment_comp_df

        # Tren Sentimen (dengan resampling harian untuk smoothnes)
        sentiment_df['date'] = pd.to_datetime(sentiment_df['date'], utc=True)
        # Ambil rata-rata skor sentimen harian
        sentiment_trend_df = sentiment_df.groupby(sentiment_df['date'].dt.date)['score'].mean().reset_index()
        sentiment_trend_df.columns = ['date', 'average_score']
        sentiment_trend_df['date'] = pd.to_datetime(sentiment_trend_df['date']) # Konversi kembali ke datetime
        sentiment_trend_df = sentiment_trend_df.set_index('date').sort_index()
        processed_data['sentiment_trend_df'] = sentiment_trend_df

        # NEW: Event Markers
        # Deteksi event berdasarkan perubahan drastis dalam sentimen (misal: lebih dari 1.5 deviasi standar dari rata-rata harian)
        if len(sentiment_trend_df) > 3: # Butuh setidaknya beberapa poin data
            mean_score = sentiment_trend_df['average_score'].mean()
            std_score = sentiment_trend_df['average_score'].std()
            
            # Identify "events" as days where sentiment deviates significantly
            # Using a threshold of 1.5 standard deviations, adjust as needed
            event_threshold = 1.5 * std_score 
            
            events = sentiment_trend_df[
                (sentiment_trend_df['average_score'] > mean_score + event_threshold) |
                (sentiment_trend_df['average_score'] < mean_score - event_threshold)
            ].index.tolist()
            
            processed_data['sentiment_events'] = events
        else:
            processed_data['sentiment_events'] = []


    # --- Matriks Entitas (Frekuensi vs. Sentimen) ---
    matrix_data = []
    for entity, scores in entity_sentiments.items():
        if len(scores) > 1: # Hanya masukkan entitas yang muncul minimal 2 kali
            matrix_data.append({
                'Entitas': entity,
                'Frekuensi': len(scores),
                'Avg_Sentiment': np.mean(scores)
            })
    processed_data['matrix_df'] = pd.DataFrame(matrix_data) if matrix_data else pd.DataFrame()

    # --- Topic Modeling ---
    if documents_for_topic_model and len(documents_for_topic_model) > 1: # BERTopic needs at least 2 documents
        try:
            topics, probabilities = topic_model.fit_transform(documents_for_topic_model)
            
            # Mendapatkan info topik
            topic_info = topic_model.get_topic_info()
            topic_info = topic_info[topic_info['Topic'] != -1].copy() # Filter topic -1 (outliers)
            topic_info.rename(columns={'Name': 'Topik_Utama', 'Count': 'Jumlah_Artikel'}, inplace=True)
            processed_data['topic_info_df'] = topic_info

            # Menambahkan topic ke setiap artikel
            for idx, topic_id in enumerate(topics):
                if idx < len(news_items): # Ensure index is valid
                    article_info = news_items[idx]
                    article_info['topic_id'] = topic_id
                    article_info['topic_name'] = topic_model.get_topic_info(topic_id)['Name'] if topic_id != -1 else "Lain-lain"
            
            topic_keywords = []
            for topic_id in topic_info['Topic']:
                words = [word for word, score in topic_model.get_topic(topic_id)]
                topic_keywords.append({'Topic': topic_id, 'Keywords': ", ".join(words[:5])}) # Ambil 5 kata kunci teratas
            processed_data['topic_keywords'] = pd.DataFrame(topic_keywords)

        except Exception as e:
            st.warning(f"Gagal melakukan Topic Modeling: {e}. Mungkin terlalu sedikit dokumen atau model tidak dapat menemukan topik.")
            processed_data['topic_info_df'] = pd.DataFrame() # Ensure dataframe exists even if empty
            processed_data['topic_keywords'] = pd.DataFrame()
            for article in news_items: # Clear topic info if topic modeling fails
                article['topic_id'] = -1
                article['topic_name'] = "Gagal Deteksi Topik"
    else:
        st.warning("Tidak cukup dokumen untuk melakukan Topic Modeling (minimal 2 artikel).")
        processed_data['topic_info_df'] = pd.DataFrame()
        processed_data['topic_keywords'] = pd.DataFrame()
        for article in news_items:
                article['topic_id'] = -1
                article['topic_name'] = "Tidak Ada Topik"

    # --- Word Cloud ---
    if all_text_for_wordcloud:
        stopwords = set([
            'yang', 'dan', 'di', 'ke', 'dari', 'dengan', 'untuk', 'pada', 'juga', 'tersebut', 'ini', 'itu',
            'adalah', 'akan', 'sebagai', 'saat', 'telah', 'bagi', 'kata', 'oleh', 'tidak', 'bisa', 'para',
            'mereka', 'harus', 'sudah', 'melakukan', 'ada', 'pun', 'tentang', 'serta', 'seperti', 'masih',
            'maupun', 'dalam', 'antara', 'hingga', 'mengatakan', 'pihak', # Tambahan stopword umum
            'tahun', 'baru', 'kembali', 'usai', 'melalui', 'mendapatkan', 'hingga', 'selama', 'setelah'
        ])
        full_text_concat = " ".join(all_text_for_wordcloud)
        processed_data['wordcloud'] = WordCloud(
            width=800, height=400,
            background_color='black',
            stopwords=stopwords,
            collocations=False,
            colormap='viridis'
        ).generate(full_text_concat)
        
    # --- NEW: Relationship Extraction (Heuristic-based) ---
    G = nx.Graph()
    relation_counts = Counter()

    for article in news_items:
        clean_text = article['clean_text']
        sentences = re.split(r'(?<=[.!?])\s+', clean_text) # Split sentences robustly

        for sentence in sentences:
            current_sentence_entities = []
            
            # Find entities in the current sentence using their 'start' and 'end' positions
            # This is a bit tricky since NER output is for the whole article.
            # A more robust approach would be to run NER on each sentence.
            # For simplicity, we'll re-scan the sentence for the extracted entities.
            
            # Filter article's entities that appear in this specific sentence
            entities_in_sentence = [e for e in article['entities'] if e['word'].strip() in sentence]

            for ent in entities_in_sentence:
                word = ent['word'].strip()
                if len(word) > 2 and not any(c.isdigit() for c in word):
                    current_sentence_entities.append(word)

            # Create connections for co-occurring entities in the same sentence
            if len(current_sentence_entities) > 1:
                # Remove duplicates while preserving order for pairs
                unique_entities = list(dict.fromkeys(current_sentence_entities))
                for i in range(len(unique_entities)):
                    for j in range(i + 1, len(unique_entities)):
                        entity1 = unique_entities[i]
                        entity2 = unique_entities[j]
                        
                        # Ensure entity names are consistent (e.g., lowercased or title cased)
                        # For simplicity, we'll keep as extracted, but consider normalization if needed.
                        
                        # Add node to graph if not exists
                        G.add_node(entity1)
                        G.add_node(entity2)

                        # Add edge and count occurrence
                        pair = tuple(sorted((entity1, entity2)))
                        relation_counts[pair] += 1
                        
    # Add edges with weights to the graph
    for (e1, e2), count in relation_counts.items():
        # Only add edges if they appear more than N times (e.g., 1 or 2) to filter noise
        if count > 1: # Adjust threshold as needed
            G.add_edge(e1, e2, weight=count)

    processed_data['entity_graph'] = G
    processed_data['relation_counts'] = relation_counts
        
    return processed_data