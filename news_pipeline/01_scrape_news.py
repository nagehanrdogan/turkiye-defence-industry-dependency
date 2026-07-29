# -*- coding: utf-8 -*-
"""
Otomatik haber taraması: Google News RSS + tam metin çekme.
BİRDEN FAZLA PLATFORMU TEK SEFERDE TARAR.

Bu script'i BU ortamda değil, KENDİ bilgisayarında çalıştırman gerekiyor.

KURULUM (bir kere, terminalde):
    pip install feedparser trafilatura pandas requests googlenewsdecoder

SEN NE YAPACAKSIN:
    1) Aşağıdaki PLATFORMLAR sözlüğüne yeni platform eklemek istersen,
       sadece yeni bir satır ekle -- "platform1", "platform2" gibi ayrı
       değişkenler TANIMLAMANA gerek yok, hepsi bu tek sözlükte duruyor.
    2) Script'i çalıştır, her platform için ayrı bir CSV çıkacak.
    3) Çıkan CSV'lerde "tam_metin" sütununu okuyup "Özet Metin" sütununu
       kendi cümlelerinle doldur.
"""

import feedparser
import pandas as pd
import trafilatura
import time
import urllib.parse
import requests
from googlenewsdecoder import gnewsdecoder

# Google bazen "bot" isteklerini az sonuçla (ya da hiç sonuçsuz) yanıtlıyor.
# Gerçek bir tarayıcı gibi görünmek için User-Agent ekliyoruz.
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
}

# -----------------------------------------------------------------------
# TÜM PLATFORMLARI VE SORGULARINI BURADA TANIMLA
# -----------------------------------------------------------------------
# Yeni platform eklemek istediğinde buraya yeni bir satır ekle, başka
# hiçbir yeri değiştirmene gerek yok.
PLATFORMLAR = {
    "Altay": [
        "Altay tankı motor ihracat",
        "Altay tankı Almanya ambargo",
        "Altay tankı BATU yerli motor",
        "Altay tankı Güney Kore motor tedarik",
    ],
    "T129": [
        "T129 ATAK motor ihracat",
        "T129 ATAK helikopteri ihracat izni",
        "T129 ATAK yerli motor TEI",
        "ATAK helikopteri Pakistan motor",
    ],
    "Hisar": [
        "Hisar füze sistemi ihracat",
        "Hisar A+ Aselsan yerli",
        "Hisar füze kısıtlama ihracat izni",
        "Hisar O+ radar arayıcı kafa",
        "Hisar füze sistemi yurt dışı satış",
    ],
    "KAAN": [
        "KAAN savaş uçağı motor F110",
        "KAAN motor ihracat ABD",
        "KAAN TEI yerli motor TF-X",
        "KAAN F110-GE-129 bağımlılık",
        "KAAN TF-35000 yerli motor",
        "TF-X KAAN ihracat lisansı",
    ],
    # yeni platform eklemek için buraya aynı formatta bir satır daha ekle:
    # "PlatformAdi": ["sorgu 1", "sorgu 2", ...],
}


# -----------------------------------------------------------------------
# GOOGLE NEWS RSS'TEN SONUÇLARI ÇEKEN FONKSİYON
# -----------------------------------------------------------------------
def google_news_rss(sorgu, dil="tr", ulke="TR"):
    q = urllib.parse.quote(sorgu)
    url = f"https://news.google.com/rss/search?q={q}&hl={dil}&gl={ulke}&ceid={ulke}:{dil}"

    try:
        yanit = requests.get(url, headers=HEADERS, timeout=15)
        feed = feedparser.parse(yanit.content)
    except Exception as e:
        print(f"  !! İstek hatası: {e}")
        return []

    # Teşhis bilgisi -- kaç ham girdi geldiğini görmek için
    print(f"  (ham girdi sayısı: {len(feed.entries)}, bozo={feed.bozo})")

    sonuclar = []
    for entry in feed.entries:
        sonuclar.append({
            "sorgu": sorgu,
            "baslik": entry.get("title", ""),
            "tarih": entry.get("published", ""),
            "kaynak": entry.get("source", {}).get("title", ""),
            "link": entry.get("link", ""),
        })
    return sonuclar


def gercek_linki_coz(google_link):
    """Google News'in yönlendirme linkini gerçek haber linkine çevirir."""
    try:
        sonuc = gnewsdecoder(google_link, interval=1)
        if sonuc.get("status"):
            return sonuc["decoded_url"]
    except Exception as e:
        pass
    return None


def tam_metin_cek(google_link):
    gercek_link = gercek_linki_coz(google_link)
    if not gercek_link:
        return "", ""
    try:
        indirilen = trafilatura.fetch_url(gercek_link)
        if indirilen:
            metin = trafilatura.extract(indirilen)
            return (metin if metin else ""), gercek_link
    except Exception:
        pass
    return "", gercek_link


# -----------------------------------------------------------------------
# TÜM PLATFORMLAR İÇİN DÖNGÜ -- burası "platform1, platform2..." yerine
# geçen kısım: sözlükteki her platformu sırayla işliyor.
# -----------------------------------------------------------------------
for platform_adi, sorgular in PLATFORMLAR.items():
    print(f"\n{'='*60}")
    print(f"PLATFORM: {platform_adi}")
    print(f"{'='*60}")

    tum_sonuclar = []
    for sorgu in sorgular:
        print(f"Aranıyor: {sorgu}")
        sonuclar = google_news_rss(sorgu)
        print(f"  -> {len(sonuclar)} sonuç bulundu")
        tum_sonuclar.extend(sonuclar)
        time.sleep(1)

    df = pd.DataFrame(tum_sonuclar)
    if df.empty:
        print(f"{platform_adi} için hiç sonuç bulunamadı, atlanıyor.")
        continue

    df = df.drop_duplicates(subset="link").reset_index(drop=True)
    print(f"Tekilleştirmeden sonra: {len(df)} haber (hepsi işlenecek, süre uzun olabilir)")

    tam_metinler = []
    gercek_linkler = []
    for i, row in df.iterrows():
        print(f"  [{i+1}/{len(df)}] Metin çekiliyor: {row['baslik'][:60]}...")
        metin, gercek_link = tam_metin_cek(row["link"])
        tam_metinler.append(metin)
        gercek_linkler.append(gercek_link if gercek_link else row["link"])
        time.sleep(1)  # Google'ın çözme servisini yormamak için

        # Ara kayıt: her 20 haberde bir, o ana kadarki ilerlemeyi kaydet.
        # İşlem yarıda kesilirse (hata, internet kopması vb.) her şeyi kaybetmezsin.
        if (i + 1) % 20 == 0:
            ara_df = df.iloc[:i + 1].copy()
            ara_df["tam_metin"] = tam_metinler
            ara_df["gercek_link"] = gercek_linkler
            ara_df["Platform"] = platform_adi
            ara_df["Özet Metin"] = ""
            ara_df.to_csv(f"{platform_adi}_otomatik_tarama.csv", index=False, encoding="utf-8-sig")
            print(f"  (ara kayıt yapıldı: {i + 1} haber)")

    df["tam_metin"] = tam_metinler
    df["gercek_link"] = gercek_linkler
    df["Platform"] = platform_adi
    df["Özet Metin"] = ""

    cikti_adi = f"{platform_adi}_otomatik_tarama.csv"
    df.to_csv(cikti_adi, index=False, encoding="utf-8-sig")

    basarili = sum(df["tam_metin"] != "")
    print(f"Kaydedildi: {cikti_adi} ({len(df)} haber, {basarili} tanesinde tam metin çekildi)")

print("\nTüm platformlar tamamlandı.")
