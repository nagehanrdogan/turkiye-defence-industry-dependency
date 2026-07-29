# -*- coding: utf-8 -*-
"""
4 platformlu (Altay, Hisar, KAAN, T129) birleşik veri seti için BERTopic analizi.

KURULUM (bir kere, terminalde):
    pip install bertopic sentence-transformers umap-learn hdbscan pandas

ÇALIŞTIRMA:
    python bertopic_coklu_platform.py

Bu script:
    A) KEŞİFEDİCİ MOD  -> HDBSCAN kendi kümelerini bulur
    B) ZERO-SHOT MOD   -> senin matrisindeki kategorilere göre eşleştirir
    C) PLATFORM KARŞILAŞTIRMASI -> hangi platformda hangi tema baskın, tablo halinde
"""

import pandas as pd
import csv
from sentence_transformers import SentenceTransformer
from bertopic import BERTopic
from umap import UMAP
from hdbscan import HDBSCAN
from sklearn.feature_extraction.text import CountVectorizer

# -----------------------------------------------------------------------
# 0) VERİYİ YÜKLE (ayracı otomatik tespit ederek -- Excel bazen virgülü
#    noktalı virgüle çeviriyor, bunu elle uğraşmadan çözüyoruz)
# -----------------------------------------------------------------------
CSV_YOLU = "ana_veri_seti.csv"

with open(CSV_YOLU, encoding="utf-8-sig") as f:
    ornek = f.read(5000)
try:
    ayrac = csv.Sniffer().sniff(ornek, delimiters=",;").delimiter
except csv.Error:
    ayrac = ","
print(f"Tespit edilen ayraç: {repr(ayrac)}")

df = pd.read_csv(CSV_YOLU, sep=ayrac, encoding="utf-8-sig", engine="python", on_bad_lines="warn")
df = df[df["Özet Metin"].notna() & (df["Özet Metin"].str.strip() != "")].reset_index(drop=True)
docs = df["Özet Metin"].tolist()
print(f"Toplam döküman: {len(docs)}")
print(df["Platform"].value_counts())

# -----------------------------------------------------------------------
# 1) EMBEDDING — gerçek multilingual sentence-transformer
# -----------------------------------------------------------------------
print("\nEmbedding modeli yükleniyor...")
embedding_model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
embeddings = embedding_model.encode(docs, show_progress_bar=True)
print(f"Embedding matrisi boyutu: {embeddings.shape}")

# -----------------------------------------------------------------------
# TÜRKÇE STOPWORDS
# -----------------------------------------------------------------------
TURKCE_STOPWORDS = [
    "acaba", "altmış", "altı", "ama", "ancak", "arada", "aslında", "ayrıca",
    "bana", "bazı", "belki", "ben", "benden", "beni", "benim", "beri", "bile",
    "bin", "bir", "birçok", "biri", "birkaç", "birkez", "birşey", "biz",
    "bizden", "bize", "bizi", "bizim", "bu", "buna", "bunda", "bundan", "bunu",
    "bunun", "burada", "böyle", "böylece", "da", "daha", "dahi", "de", "defa",
    "değil", "diğer", "diye", "doksan", "dokuz", "dolayı", "dolayısıyla",
    "dört", "edecek", "eden", "ederek", "edilecek", "ediliyor", "edilmesi",
    "ediyor", "eğer", "elli", "en", "etmesi", "etti", "ettiği", "ettiğini",
    "gibi", "göre", "halen", "hangi", "hatta", "hem", "henüz", "hep", "hepsi",
    "her", "herhangi", "herkesin", "hiç", "hiçbir", "için", "iki", "ile",
    "ilgili", "ise", "işte", "itibaren", "itibariyle", "kadar", "karşın",
    "kendi", "kendilerine", "kendini", "kendisi", "kendisine", "kendisini",
    "kez", "ki", "kim", "kimden", "kime", "kimi", "kimse", "kırk", "milyar",
    "milyon", "mu", "mü", "mı", "nasıl", "ne", "neden", "nedenle", "nerde",
    "nerede", "nereye", "niye", "niçin", "o", "olan", "olarak", "oldu",
    "olduğu", "olduğunu", "olduklarını", "olmadı", "olmadığı", "olmak",
    "olması", "olmayan", "olmaz", "olsa", "olsun", "olup", "olur", "olursa",
    "oluyor", "on", "ona", "ondan", "onlar", "onlardan", "onları", "onların",
    "onu", "onun", "otuz", "oysa", "öyle", "pek", "rağmen", "sadece", "sanki",
    "sekiz", "seksen", "sen", "senden", "seni", "senin", "siz", "sizden",
    "sizi", "sizin", "sonra", "şey", "şeyden", "şeyi", "şeyler", "şöyle",
    "şu", "şuna", "şunda", "şundan", "şunları", "şunu", "tarafından", "tüm",
    "üç", "üzere", "var", "vardı", "ve", "veya", "ya", "yani", "yapacak",
    "yapılan", "yapılması", "yapıyor", "yapmak", "yaptı", "yaptığı",
    "yaptığını", "yaptıkları", "yedi", "yerine", "yetmiş", "yine", "yirmi",
    "yoksa", "yüz", "zaten", "türkiye", "türkiye'nin", "türkiye'ye",
]

vectorizer_model = CountVectorizer(stop_words=TURKCE_STOPWORDS, ngram_range=(1, 2))

# -----------------------------------------------------------------------
# A) KEŞİFEDİCİ MOD
# -----------------------------------------------------------------------
print("\n" + "=" * 60)
print("A) KEŞİFEDİCİ MOD")
print("=" * 60)

umap_model = UMAP(n_neighbors=10, n_components=5, min_dist=0.0, random_state=42)
hdbscan_model = HDBSCAN(min_cluster_size=5, min_samples=2, metric="euclidean")

topic_model = BERTopic(
    embedding_model=embedding_model,
    umap_model=umap_model,
    hdbscan_model=hdbscan_model,
    vectorizer_model=vectorizer_model,
    language="turkish",
    calculate_probabilities=False,
    verbose=True,
)

topics, _ = topic_model.fit_transform(docs, embeddings=embeddings)
df["kesif_topic"] = topics

print("\n--- Konu özeti ---")
print(topic_model.get_topic_info()[["Topic", "Count", "Name"]].to_string(index=False))

print("\n--- Her konunun temsilci kelimeleri ---")
for t in sorted(set(topics)):
    if t == -1:
        print("Topic -1 (outlier)")
        continue
    kelimeler = ", ".join([w for w, _ in topic_model.get_topic(t)[:8]])
    print(f"Topic {t}: {kelimeler}")

# Görselleştirmeler
if len(set(topics) - {-1}) > 1:
    topic_model.visualize_hierarchy().write_html("hiyerarsi_coklu.html")
    topic_model.visualize_heatmap().write_html("heatmap_coklu.html")
    print("\nGörselleştirmeler kaydedildi: hiyerarsi_coklu.html, heatmap_coklu.html")

# -----------------------------------------------------------------------
# C) PLATFORM KARŞILAŞTIRMASI -- hangi platformda hangi tema baskın
# -----------------------------------------------------------------------
print("\n" + "=" * 60)
print("C) PLATFORM x KONU ÇAPRAZ TABLOSU")
print("=" * 60)

df["konu_adi"] = df["kesif_topic"].apply(
    lambda t: "outlier" if t == -1 else
    "_".join([w for w, _ in topic_model.get_topic(t)[:3]])
)

capraz = pd.crosstab(df["Platform"], df["konu_adi"])
print(capraz)
capraz.to_csv("platform_konu_capraz.csv", encoding="utf-8-sig")

# Yüzdesel görünüm (her platformun kendi içinde hangi tema ne kadar ağırlıklı)
capraz_yuzde = capraz.div(capraz.sum(axis=1), axis=0).round(2)
print("\n--- Platform içi yüzdeler ---")
print(capraz_yuzde)

df.to_csv("ana_veri_seti_kesif_sonuc.csv", index=False, encoding="utf-8-sig")

# -----------------------------------------------------------------------
# B) ZERO-SHOT MOD — component criticality matrisin
# -----------------------------------------------------------------------
print("\n" + "=" * 60)
print("B) ZERO-SHOT MOD")
print("=" * 60)

zeroshot_kategoriler = [
    "ihracat lisansı ambargo kısıtlaması engel",
    "yerli üretim motor geliştirme ikame bağımlılığı azaltma",
    "yabancı tedarikçi anlaşması motor alımı",
    "teslimat envanter tören ihracat anlaşması genel duyuru",
]

zeroshot_model = BERTopic(
    embedding_model=embedding_model,
    vectorizer_model=vectorizer_model,
    zeroshot_topic_list=zeroshot_kategoriler,
    zeroshot_min_similarity=0.45,
    umap_model=umap_model,
    hdbscan_model=hdbscan_model,
    language="turkish",
)

zs_topics, _ = zeroshot_model.fit_transform(docs, embeddings=embeddings)
df["zeroshot_topic"] = zs_topics

print("\n--- Zero-shot konu özeti ---")
print(zeroshot_model.get_topic_info()[["Topic", "Count", "Name"]].to_string(index=False))

zs_capraz = pd.crosstab(df["Platform"], df["zeroshot_topic"])
print("\n--- Platform x Zero-shot konu ---")
print(zs_capraz)

df.to_csv("ana_veri_seti_tam_sonuc.csv", index=False, encoding="utf-8-sig")

print("\nTamamlandı. Çıktılar:")
print(" - ana_veri_seti_tam_sonuc.csv (her satır + iki mod sonucu)")
print(" - platform_konu_capraz.csv (platform x tema tablosu)")
print(" - hiyerarsi_coklu.html, heatmap_coklu.html (tarayıcıda aç)")
