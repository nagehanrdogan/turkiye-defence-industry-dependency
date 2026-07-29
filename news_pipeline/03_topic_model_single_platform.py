# -*- coding: utf-8 -*-
"""
Altay Motor CSV'si için gerçek multilingual embedding modeliyle BERTopic analizi.

KURULUM (bir kere, terminalde çalıştır):
    pip install bertopic sentence-transformers umap-learn hdbscan pandas

ÇALIŞTIRMA:
    python bertopic_altay.py

Bu script iki ayrı analiz sunar:
    A) KEŞİFEDİCİ MOD  -> HDBSCAN kendi kümelerini kendisi bulur (kaç konu çıkacağını bilmiyoruz)
    B) ZERO-SHOT MOD   -> senin matrisindeki kategorileri önceden veriyoruz, model metinleri
                          bu kategorilere eşleştirmeye çalışıyor

İkisini de dene, hangisi senin araştırma sorunla daha uyumlu sonuç veriyor karşılaştır.
"""

import pandas as pd
from sentence_transformers import SentenceTransformer
from bertopic import BERTopic
from umap import UMAP
from hdbscan import HDBSCAN
from sklearn.feature_extraction.text import CountVectorizer

# -----------------------------------------------------------------------
# 0) VERİYİ YÜKLE
# -----------------------------------------------------------------------
# CSV'nin script ile aynı klasörde olduğundan emin ol, ya da tam path ver.
CSV_YOLU = "Altay_Motor_temiz.csv"

df = pd.read_csv(CSV_YOLU)
docs = df["metin_temiz"].tolist()
print(f"Toplam döküman: {len(docs)}")

# -----------------------------------------------------------------------
# 1) EMBEDDING — gerçek multilingual sentence-transformer
# -----------------------------------------------------------------------
# İlk çalıştırmada bu model internetten (Hugging Face) indirilecek (~470 MB).
# Türkçe dahil 50+ dili anlıyor, cümle düzeyinde (kelime değil) embedding üretir.
print("Embedding modeli indiriliyor / yükleniyor...")
embedding_model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
embeddings = embedding_model.encode(docs, show_progress_bar=True)
print(f"Embedding matrisi boyutu: {embeddings.shape}")

# -----------------------------------------------------------------------
# TÜRKÇE STOPWORDS — c-TF-IDF adımında "ve, bir, için" gibi kelimelerin
# önemini düşürmek için. Kendi listeni genişletebilirsin.
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
    "yoksa", "yüz", "zaten",
]

vectorizer_model = CountVectorizer(stop_words=TURKCE_STOPWORDS, ngram_range=(1, 2))

# -----------------------------------------------------------------------
# A) KEŞİFEDİCİ MOD — HDBSCAN kendi kümelerini bulsun
# -----------------------------------------------------------------------
print("\n" + "=" * 60)
print("A) KEŞİFEDİCİ MOD")
print("=" * 60)

# Küçük veri seti (30-50 satır) için parametreleri düşürüyoruz.
# Veri büyüdükçe (200+ satır) bu sayıları artırabilirsin (varsayılanlara yakınsar).
umap_model = UMAP(n_neighbors=5, n_components=5, min_dist=0.0, random_state=42)
hdbscan_model = HDBSCAN(min_cluster_size=3, min_samples=1, metric="euclidean")

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

print("\n--- Konu özeti ---")
print(topic_model.get_topic_info()[["Topic", "Count", "Name"]].to_string(index=False))

print("\n--- Her konunun temsilci kelimeleri ---")
for t in sorted(set(topics)):
    if t == -1:
        print("Topic -1 (outlier): hiçbir kümeye net uymayan haberler")
        continue
    kelimeler = ", ".join([w for w, _ in topic_model.get_topic(t)[:8]])
    print(f"Topic {t}: {kelimeler}")

# Hiyerarşi ve heatmap görselleştirmeleri (tarayıcıda açılan HTML dosyaları)
if len(set(topics) - {-1}) > 1:
    fig_hier = topic_model.visualize_hierarchy()
    fig_hier.write_html("hiyerarsi.html")
    fig_heat = topic_model.visualize_heatmap()
    fig_heat.write_html("heatmap.html")
    print("\nGörselleştirmeler kaydedildi: hiyerarsi.html, heatmap.html")

# Sonucu CSV'ye ekle
df["kesif_topic"] = topics
df.to_csv("altay_kesif_sonuc.csv", index=False)

# -----------------------------------------------------------------------
# B) ZERO-SHOT MOD — kendi kategorilerini önceden ver
# -----------------------------------------------------------------------
print("\n" + "=" * 60)
print("B) ZERO-SHOT MOD")
print("=" * 60)

# Kendi component criticality matrisindeki kategorileri buraya yaz.
# Kısa ama açıklayıcı olsun -- model bunları da embedding'e çevirip
# dökümanlarla karşılaştıracak.
zeroshot_kategoriler = [
    "Almanya ambargosu ihracat lisansı kısıtlaması",
    "Güney Kore'den motor tedariki anlaşması",
    "yerli BATU motor geliştirme ve ikame",
    "tank teslimatı ve genel platform haberleri",
]

zeroshot_model = BERTopic(
    embedding_model=embedding_model,
    vectorizer_model=vectorizer_model,
    zeroshot_topic_list=zeroshot_kategoriler,
    zeroshot_min_similarity=0.5,   # 0.3-0.6 arası dene, düşürürsen daha çok eşleşme olur
    umap_model=umap_model,
    hdbscan_model=hdbscan_model,
    language="turkish",
)

zs_topics, _ = zeroshot_model.fit_transform(docs, embeddings=embeddings)

print("\n--- Zero-shot konu özeti ---")
print(zeroshot_model.get_topic_info()[["Topic", "Count", "Name"]].to_string(index=False))

df["zeroshot_topic"] = zs_topics
df.to_csv("altay_zeroshot_sonuc.csv", index=False)

print("\nTamamlandı. Çıktı dosyaları: altay_kesif_sonuc.csv, altay_zeroshot_sonuc.csv")
print("İstersen zeroshot_min_similarity değerini değiştirip tekrar dene --")
print("çok satır -1'e (eşleşmedi) düşüyorsa değeri düşür (örn. 0.3).")
