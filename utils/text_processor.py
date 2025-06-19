# utils/text_processor.py
import re

def clean_text_for_analysis(title, description):
    """
    Menggabungkan judul dan deskripsi, membersihkan tag HTML dan spasi berlebih.
    """
    full_text = f"{title}. {re.sub('<[^<]+?>', '', description or '')}"
    return ' '.join(full_text.split()).strip() # Menghapus spasi berlebih

def visualize_ner(text, entities):
    """
    Menyorot entitas yang ditemukan dalam teks dengan warna berbeda.
    """
    if not entities: return text
    # Sort entities by their start position to avoid overlapping issues
    entities = sorted(entities, key=lambda x: x['start'])
    
    last_idx, highlighted_text = 0, ""
    colors = {"PER": "#ffadad", "ORG": "#a0c4ff", "GPE": "#fdffb6", "LOC": "#fdffb6", "TIME": "#caffbf", "MISC": "#bdb2ff"}
    entity_map = {"PER": "Orang", "ORG": "Organisasi", "GPE": "Lokasi", "LOC": "Lokasi", "TIME": "Waktu", "MISC": "Lain-lain"}
    
    for entity in entities:
        start, end, label = entity['start'], entity['end'], entity['entity_group']
        
        # Ensure we don't go out of bounds or process empty entities
        if start < 0 or end > len(text) or start >= end:
            continue

        # Add text before the current entity
        highlighted_text += text[last_idx:start]
        
        # Get color and label for the entity
        color, label_text = colors.get(label, "#e0e0e0"), entity_map.get(label, label)
        
        # Add the highlighted entity
        highlighted_text += f"<mark style='background-color: {color};'>"
        highlighted_text += f"{text[start:end]} <span style='font-size: 0.75em; font-weight: bold; color: #555;'>{label_text}</span></mark>"
        last_idx = end
        
    # Add any remaining text after the last entity
    highlighted_text += text[last_idx:]
    return highlighted_text