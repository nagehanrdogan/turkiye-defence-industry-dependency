"""
Türkiye savunma bütçesi verilerini tek bir tidy CSV'de birleştirir.

Girdi:
  1) savunma_butce_2018_2026_tidy.csv                       -> kanun rakamları (baslangic_odenegi)
  2) savunma_kurumlari_odenek_gerceklesme_2018_2025.csv      -> Muhasebat MYB istatistikleri
     (baslangic/yil_sonu/gerceklesme)

Çıktı:
  milex_turkiye_2018_2026.csv  -> yil, kurum, odenek_turu, tutar_tl, kaynak, not
"""

import pandas as pd

# ---------------------------------------------------------------------------
# 0) Sabitler
# ---------------------------------------------------------------------------

DOSYA1 = "savunma_butce_2018_2026_tidy.csv"
DOSYA2 = "savunma_kurumlari_odenek_gerceklesme_2018_2025.csv"
CIKTI = "milex_turkiye_2018_2026.csv"

# Dosya 2'deki uzun kurum adlarını, dosya 1'deki kısa adlara eşleyen sözlük.
# Bu eşleme kod içinde açık tutuluyor ki hangi ismin hangisine karşılık
# geldiği tek bakışta görülebilsin.
KURUM_ESLEME = {
    "Millî Savunma Bakanlığı": "MSB",
    "Jandarma Genel Komutanlığı": "Jandarma",
    "Sahil Güvenlik Komutanlığı": "Sahil_Guvenlik",
    "Savunma Sanayii Başkanlığı": "SSB",
}

# ---------------------------------------------------------------------------
# 1) Dosya 1'i oku: kanundaki başlangıç ödenekleri (zaten TL, zaten tidy)
# ---------------------------------------------------------------------------

df1 = pd.read_csv(DOSYA1, encoding="utf-8-sig")

# Beklenen sütunlar: Yil, Kurum, Tutar_TL, Odenek_Turu, Kaynak
# Bu dosyada tek odenek_turu var: baslangic_odenegi. Başka bir tür varsa
# (ör. ileride eklenirse) burada patlamak, sessizce yanlış veri üretmekten iyidir.
assert set(df1["Odenek_Turu"].unique()) == {"baslangic_odenegi"}, (
    "Dosya 1'de beklenmeyen bir Odenek_Turu bulundu."
)

df1 = df1.rename(
    columns={
        "Yil": "yil",
        "Kurum": "kurum",
        "Tutar_TL": "tutar_tl",
        "Kaynak": "kaynak",
    }
)[["yil", "kurum", "tutar_tl", "kaynak"]]

# ---------------------------------------------------------------------------
# 2) Dosya 2'yi oku: Muhasebat gerçekleşme istatistikleri
#    - encoding="utf-8-sig" BOM'u otomatik siler
#    - pandas'ın C parser'ı \r\n satır sonlarını zaten doğru okur,
#      bu yüzden ekstra bir işlem gerekmiyor
# ---------------------------------------------------------------------------

df2 = pd.read_csv(DOSYA2, encoding="utf-8-sig")

# Beklenen sütunlar:
# kurum, yil, baslangic_odenegi_bin_tl, yil_sonu_odenegi_bin_tl,
# gerceklesme_bin_tl, kaynak

# Uzun kurum adlarını kısa adlara çevir.
df2["kurum"] = df2["kurum"].map(KURUM_ESLEME)
assert df2["kurum"].isna().sum() == 0, (
    "KURUM_ESLEME sözlüğünde karşılığı olmayan bir kurum adı var."
)

# Bin TL -> TL çevirisi (üç ödenek/gerçekleşme sütunu için).
# Bazı yıllarda (2022 sonrası) kuruşlu (ondalıklı) değerler geliyor;
# TL'ye çevirdikten sonra en yakın tam sayıya yuvarlayacağız (adım 5'te).
for kol in ["baslangic_odenegi_bin_tl", "yil_sonu_odenegi_bin_tl", "gerceklesme_bin_tl"]:
    df2[kol] = df2[kol] * 1000

# ---------------------------------------------------------------------------
# 3) baslangic_odenegi satırları: SADECE dosya 1'den (kanun rakamı esas)
# ---------------------------------------------------------------------------

satir_baslangic = df1.copy()
satir_baslangic["odenek_turu"] = "baslangic_odenegi"
satir_baslangic["not"] = ""

# ---------------------------------------------------------------------------
# 4) ek_butce_dahil_odenek satırları: dosya 2'nin baslangic_odenegi'nden,
#    yalnızca dosya 1'deki kanun rakamından FARKLI olduğu yıl-kurumlar için.
#    Fark kod tarafından tespit ediliyor; elle yıl yazılmıyor.
# ---------------------------------------------------------------------------

df2_baslangic = df2[["yil", "kurum", "baslangic_odenegi_bin_tl", "kaynak"]].rename(
    columns={"baslangic_odenegi_bin_tl": "tutar_tl_dosya2"}
)

karsilastirma = df1.merge(
    df2_baslangic, on=["yil", "kurum"], how="inner", suffixes=("_dosya1", "_dosya2")
)
karsilastirma["fark"] = karsilastirma["tutar_tl_dosya2"] - karsilastirma["tutar_tl"]

farkli_olanlar = karsilastirma[karsilastirma["fark"] != 0].copy()

satir_ek_butce = farkli_olanlar[["yil", "kurum"]].copy()
satir_ek_butce["tutar_tl"] = farkli_olanlar["tutar_tl_dosya2"]
satir_ek_butce["kaynak"] = farkli_olanlar["kaynak_dosya2"]
satir_ek_butce["odenek_turu"] = "ek_butce_dahil_odenek"
satir_ek_butce["not"] = ""

# ---------------------------------------------------------------------------
# 5) yilsonu_odenegi satırları: dosya 2'den.
#    2025 için tüm kurumlarda yil_sonu_odenegi_bin_tl boş (NaN) -> bu satırlar
#    zaten NaN olduğu için doğal olarak dışarıda kalıyor (dropna).
# ---------------------------------------------------------------------------

satir_yilsonu = df2.dropna(subset=["yil_sonu_odenegi_bin_tl"])[
    ["yil", "kurum", "yil_sonu_odenegi_bin_tl", "kaynak"]
].rename(columns={"yil_sonu_odenegi_bin_tl": "tutar_tl"})
satir_yilsonu["odenek_turu"] = "yilsonu_odenegi"
satir_yilsonu["not"] = ""

# ---------------------------------------------------------------------------
# 6) gerceklesme satırları: dosya 2'den.
#    2025 satırlarına "gecici_veri" notu ekleniyor (kesin hesap henüz yasalaşmadı).
# ---------------------------------------------------------------------------

satir_gerceklesme = df2[["yil", "kurum", "gerceklesme_bin_tl", "kaynak"]].rename(
    columns={"gerceklesme_bin_tl": "tutar_tl"}
)
satir_gerceklesme["odenek_turu"] = "gerceklesme"
satir_gerceklesme["not"] = satir_gerceklesme["yil"].apply(
    lambda y: "gecici_veri" if y == 2025 else ""
)

# ---------------------------------------------------------------------------
# 7) Doğrulama kontrolü (b): gerceklesme > yilsonu_odenegi olan yıl-kurumlar.
#    Bu satırlarda gerçekleşme, yıl sonu ödenek tavanını aşıyor demektir;
#    bu yüzden "kontrol_edilecek" notu gerceklesme satırına ekleniyor.
#    (Not: kıyaslama yil_sonu_odenegi_bin_tl NaN olan 2025 için tanımsız
#    olduğundan otomatik olarak bu kontrolün dışında kalır.)
# ---------------------------------------------------------------------------

gerc_vs_yilsonu = df2.dropna(subset=["yil_sonu_odenegi_bin_tl"])[
    ["yil", "kurum", "yil_sonu_odenegi_bin_tl", "gerceklesme_bin_tl"]
].copy()
gerc_vs_yilsonu["fazla_gerceklesme"] = (
    gerc_vs_yilsonu["gerceklesme_bin_tl"] > gerc_vs_yilsonu["yil_sonu_odenegi_bin_tl"]
)
kontrol_edilecekler = gerc_vs_yilsonu[gerc_vs_yilsonu["fazla_gerceklesme"]]

kontrol_anahtarlari = set(
    zip(kontrol_edilecekler["yil"], kontrol_edilecekler["kurum"])
)


def _gerceklesme_notu_ekle(row):
    anahtar = (row["yil"], row["kurum"])
    if anahtar in kontrol_anahtarlari:
        mevcut = row["not"]
        return (mevcut + "; kontrol_edilecek").strip("; ") if mevcut else "kontrol_edilecek"
    return row["not"]


satir_gerceklesme["not"] = satir_gerceklesme.apply(_gerceklesme_notu_ekle, axis=1)

# ---------------------------------------------------------------------------
# 8) Tüm satırları birleştir, tutarları tam sayıya yuvarla, sütunları sırala
# ---------------------------------------------------------------------------

sonuc = pd.concat(
    [satir_baslangic, satir_ek_butce, satir_yilsonu, satir_gerceklesme],
    ignore_index=True,
)

# Ondalıklı (kuruşlu) tutarları en yakın tam sayı TL'ye yuvarla.
sonuc["tutar_tl"] = sonuc["tutar_tl"].round(0).astype("int64")

sonuc = sonuc[["yil", "kurum", "odenek_turu", "tutar_tl", "kaynak", "not"]]
sonuc = sonuc.sort_values(["yil", "kurum", "odenek_turu"]).reset_index(drop=True)

sonuc.to_csv(CIKTI, index=False, encoding="utf-8-sig")

# ---------------------------------------------------------------------------
# 9) Doğrulama raporu
# ---------------------------------------------------------------------------

print("=" * 70)
print("DOĞRULAMA RAPORU (a): Başlangıç ödenekleri, dosya 1 vs dosya 2")
print("=" * 70)

rapor_a = karsilastirma.copy()
rapor_a["yuzde_fark"] = (rapor_a["fark"] / rapor_a["tutar_tl"] * 100).round(2)
rapor_a["tutuyor_mu"] = rapor_a["fark"].apply(lambda f: "TUTUYOR" if f == 0 else "TUTMUYOR")

for _, r in rapor_a.sort_values(["kurum", "yil"]).iterrows():
    print(
        f"{r['kurum']:<15} {r['yil']}  dosya1={r['tutar_tl']:>15,.0f}  "
        f"dosya2={r['tutar_tl_dosya2']:>15,.0f}  fark={r['fark']:>15,.0f}  "
        f"(%{r['yuzde_fark']:>6.2f})  -> {r['tutuyor_mu']}"
    )

tutmayanlar = rapor_a[rapor_a["fark"] != 0][["kurum", "yil"]]
print()
print("Tutmayan kurum-yıllar:", list(tutmayanlar.itertuples(index=False, name=None)))

print()
print("=" * 70)
print("DOĞRULAMA RAPORU (b): gerceklesme > yilsonu_odenegi olan satırlar")
print("=" * 70)

if kontrol_edilecekler.empty:
    print("Bulunamadı.")
else:
    for _, r in kontrol_edilecekler.sort_values(["kurum", "yil"]).iterrows():
        print(
            f"{r['kurum']:<15} {r['yil']}  yil_sonu={r['yil_sonu_odenegi_bin_tl']:>15,.0f}  "
            f"gerceklesme={r['gerceklesme_bin_tl']:>15,.0f}  "
            f"fark={r['gerceklesme_bin_tl'] - r['yil_sonu_odenegi_bin_tl']:>15,.0f}"
        )

print()
print(f"Toplam satır sayısı: {len(sonuc)}")
print(f"Çıktı dosyası: {CIKTI}")
