# Türkiye Defence Industry: Component-Level Dependency Analysis

**Devam eden doktora tez sahası çalışması (PhD dissertation fieldwork) · NLP / text-as-data**

Bu depo, geç kapitalistleşen ülkelerdeki savunma sanayisi gelişimini inceleyen daha geniş bir
araştırma programının parçası olarak, Türkiye'nin dört ana savunma platformunda (Altay tankı,
T129 ATAK, Hisar hava savunma sistemi, TAI KAAN) bileşen düzeyinde yabancı tedarik
bağımlılığını haritalandırmayı amaçlar. Amaç, SIPRI'nin platform düzeyindeki transfer
verisindeki bir boşluğu — hangi alt sistemin (motor, sensör, vb.) hangi platforma, hangi
tedarikçiden geldiğine dair açık bir bağlantının bulunmaması — kısmen kapatacak bir
**kriterlik matrisi** (functional necessity × export restriction × substitution availability)
geliştirmektir.

> Bu, aktif olarak devam eden bir saha çalışmasıdır; script'ler ve veri kapsamı zaman içinde
> genişleyecektir.

## Metodolojik yaklaşım

Bağımlılık iddiaları üç ayrı, birbirini tamamlayan kaynaktan çapraz doğrulanır:

1. **SIPRI Arms Transfers Database** üzerinden istatistiksel/zamansal eşleştirme
   (`criticality_matrix/`) — yerli üretim platformları ile aynı döneme denk gelen alt sistem
   ithalatlarını aday bağımlılık olarak işaretler.
2. **ABD (DSCA/State Dept.) ve Almanya (Rüstungsexportbericht) resmi ihracat bildirimleri**
   (`external_validation/`) — SIPRI'nin kapsamadığı/eşik altı kalan vakalar için resmi ihracat
   izni kayıtlarından bağımsız doğrulama.
3. **Türkçe basın taraması** (`news_pipeline/`) — 530+ haberden oluşan otomatik toplanmış ve
   tekilleştirilmiş bir korpus üzerinde konu modelleme (BERTopic) ile ambargo/ihracat kısıtlaması,
   yerli ikame geliştirme ve yabancı tedarik anlaşması temalarının platform bazında izlenmesi.

Ayrıca `budget_crossvalidation/` klasöründe, Türkiye'nin resmî bütçe kanunu rakamları ile
Muhasebat gerçekleşme istatistikleri SIPRI Military Expenditure Database ile çapraz
karşılaştırma için tek bir tidy veri setinde birleştirilir.

**Önemli sınırlama:** SIPRI/DSCA/basın eşleştirmeleri istatistiksel ve zamansal yakınlığa
dayanır; kanıtlanmış bir tedarik zinciri bağlantısı değildir. Her script kendi çıktısında bu
sınırlamayı ve manuel doğrulama için bir şablonu (`To_Verify_External`) ayrıca üretir.

## Klasör yapısı

```
criticality_matrix/         SIPRI trade_register.csv üzerinden platform x alt sistem eşleştirmesi
                             ve üç katmanlı zincirleme bağımlılık analizi (orijinal tedarikçi ->
                             Türkiye [lisanslı üretim] -> üçüncü ülke)

external_validation/
  dsca_scraper/              DSCA (Major Arms Sales) ve State Dept. bildirimlerini tarayan scraper;
                              indirilen CN PDF'leri
  german_reports/             Almanya Rüstungsexportbericht'lerini (2014-2024) indirip 'Türkei'
                              geçen yerleri tarayan script

budget_crossvalidation/      Türkiye savunma bütçesi (kanun + gerçekleşme) verisinin tidy
                              formatta birleştirilmesi, SIPRI Milex ile çapraz kontrol

news_pipeline/                Türkçe haber tarama -> tekilleştirme -> BERTopic konu modelleme
                              pipeline'ı (4 platform: Altay, T129, Hisar, KAAN)
  01_scrape_news.py            Google News RSS taraması + tam metin çekme
  02_prepare_for_summary.py    Boş/kısa metin eleme + fuzzy-matching ile tekrar eleme + taslak özet
  03_topic_model_single_platform.py   Tek platform (Altay) için BERTopic (keşifedici + zero-shot)
  04_topic_model_multi_platform.py    4 platform birleşik BERTopic + platform x tema çapraz tablosu
  pilot_altay/                  İlk pilot çalışma (yalnızca Altay) — notebook + ham veri
  multi_platform_run/           4 platformlu tam çalıştırma — notebook + ham veri
```

## Veri hakkında not

Ham ve işlenmiş veri dosyaları (`.csv`, `.xlsx`, `.pdf`) bilinçli olarak `.gitignore` ile bu
depoya dahil edilmiyor; yalnızca kod, notebook'lar ve metodoloji bu depoda paylaşılıyor. Veri
dosyaları yerel makinede kalmaya devam ediyor.

## Kurulum

Her alt klasördeki script'in başındaki docstring, o script'e özel `pip install` komutunu içerir
(ör. `pip install bertopic sentence-transformers umap-learn hdbscan` BERTopic script'leri için,
`pip install selenium webdriver-manager pdfplumber` DSCA scraper için). Script'ler kendi
klasörlerinden çalıştırılmak üzere tasarlanmıştır (girdi/çıktı dosya adları o klasöre görelidir).
