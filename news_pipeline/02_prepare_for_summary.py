# -*- coding: utf-8 -*-
"""
Toplanan haberleri özetlemeye hazırlama: eleme + taslak özet çıkarma.

Bu script, haber_tarama.py'nin ürettiği CSV'leri (tam_metin dolu olanları)
alıp, sana ELLE ÖZETLEME için çok daha küçük ve düzenli bir liste hazırlar.

KURULUM:
    pip install pandas rapidfuzz

KULLANIM:
    python ozet_hazirla.py
"""

import pandas as pd
from rapidfuzz import fuzz

PLATFORMLAR = ["Altay", "Hisar", "KAAN", "T129"]

for platform in PLATFORMLAR:
    dosya = f"{platform}_otomatik_tarama.csv"
    try:
        df = pd.read_csv(dosya, encoding="utf-8-sig")
    except FileNotFoundError:
        print(f"{dosya} bulunamadı, atlanıyor.")
        continue

    once = len(df)

    # -----------------------------------------------------------------
    # 1) ELEME: boş / çok kısa tam metinleri çıkar
    # -----------------------------------------------------------------
    df = df[df["tam_metin"].notna()]
    df = df[df["tam_metin"].astype(str).str.len() > 100]
    print(f"\n{platform}: {once} -> {len(df)} (boş/kısa metinler elendikten sonra)")

    # -----------------------------------------------------------------
    # 2) TEKRAR ELEME: birbirine çok benzeyen haberleri çıkar
    #    (ajans haberleri birçok sitede birebir/neredeyse birebir yayınlanır)
    # -----------------------------------------------------------------
    df = df.reset_index(drop=True)
    tutulacak = [True] * len(df)
    metinler = df["tam_metin"].astype(str).tolist()

    for i in range(len(metinler)):
        if not tutulacak[i]:
            continue
        for j in range(i + 1, len(metinler)):
            if not tutulacak[j]:
                continue
            benzerlik = fuzz.ratio(metinler[i][:300], metinler[j][:300])
            if benzerlik > 85:  # %85+ benzerse aynı haber sayılır
                tutulacak[j] = False  # ikinciyi ele, ilkini tut

    df = df[tutulacak].reset_index(drop=True)
    print(f"{platform}: tekrar eleme sonrası {len(df)} haber kaldı")

    # -----------------------------------------------------------------
    # 3) TASLAK ÖZET: metnin ilk 2 cümlesini ayıkla
    # -----------------------------------------------------------------
    def ilk_iki_cumle(metin):
        # basit cümle ayırma (noktadan böl)
        parcalar = metin.replace("\n", " ").split(". ")
        secilen = ". ".join(parcalar[:2]).strip()
        if secilen and not secilen.endswith("."):
            secilen += "."
        return secilen

    df["taslak_ozet"] = df["tam_metin"].astype(str).apply(ilk_iki_cumle)

    # -----------------------------------------------------------------
    # 4) SEN DOLDURACAKSIN
    # -----------------------------------------------------------------
    df["Özet Metin"] = ""  # taslak_ozet'i okuyup kendi cümlenle burayı dolduracaksın

    # En önemli sütunları öne al, okumayı kolaylaştır
    sutunlar = ["Platform", "tarih", "kaynak", "baslik", "taslak_ozet",
                "Özet Metin", "gercek_link", "tam_metin"]
    sutunlar = [s for s in sutunlar if s in df.columns]
    df = df[sutunlar]

    cikti = f"{platform}_ozetlemeye_hazir.csv"
    df.to_csv(cikti, index=False, encoding="utf-8-sig")
    print(f"{platform}: '{cikti}' oluşturuldu ({len(df)} satır, özetlenmeyi bekliyor)")

print("\nTamamlandı. Her platform için '_ozetlemeye_hazir.csv' dosyalarını aç,")
print("'taslak_ozet' sütununu oku, 'Özet Metin' sütununa kendi cümleni yaz.")
print("Alakasız veya yanlış eşleşmiş satırları da bu aşamada silebilirsin.")
