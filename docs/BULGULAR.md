# BULGULAR — ölçülmüş sonuçlar ve dürüstlük kayıtları

> Bu dosya `DEVIR.md` ve `kenar_mimarisi.md`'yi **tamamlar**, yerine geçmez.
> Kural: buraya sadece **ölçülmüş** şeyler yazılır. Tahmin yazılmaz.
> Tarih: 27 Ağustos 2026

---

## 1. DOĞRULANAN İDDİALAR

### 1.1 `N` keşif üretiyor — TEST 2b, izole edildi
```
N AÇIK  : A A A A A A B B A B A B
N KAPALI: A A A A A A A A A A A A
```
İki kenar da **hep doğru** (err=0), yani `q` ayırt edemiyor. Tek fark `N`.
Ayrı keşif algoritması yok. `edge.py::test_kesif_izole()` — artık kodda,
markdown'da değil.

### 1.2 Nöron > tek kenar
tek kenar 0.670 → nöron 0.983.

### 1.3 Birleştirme kuralı — DEVIR.md açık soru 1 CEVAPLANDI
5 kural, 5 tohum, aynı havuz:

| kural | doğruluk |
|---|---|
| `max_qeff` (eski) | 0.980 |
| `agirlikli_oy` | 0.996 |
| `en_ozel` | 0.995 |
| **`isabet_oy`** | **0.999** |
| **`ozel_isabet`** | **0.999** |

Kazanan: **en özel eşleşen kural konuşur, eşitlikte isabetli olan.**
`max_qeff` yenildi.

### 1.4 Bisimulation kârlı — kenar_mimarisi §5.5 DOĞRULANDI
Dünyaya tuzak eş-anlamlı sayılar kondu (4≡boş, 5≡duvar). Ajana söylenmedi.

```
5 ham değer → 3 TİP:  T0={0,4}  T1={1,5}  T2={3}
```
Etiket yok, isim yok. Ve maliyeti:

| φ dili | kenar | doğruluk |
|---|---|---|
| ham değer | 530 → 221 canlı | 0.990 |
| **bisim tipi** | **280 → 91 canlı** | **0.998** |

Yarı kenar, daha iyi doğruluk. Prior kârlı.

### 1.5 Parça paylaşımı — Adem'in "nokta vektör olmalı" itirazı DOĞRU
Değer `6` eklendi: geçilebilir **ama** sayaç artırır.
```
6 ile 0 ortak parça: hareket(1,0)
6 ile 3 ortak parça: hareket(1,0), sayaç+1
```
`6` hiçbir şeyle aynı **tip** değil ama parçalarını paylaşıyor.
Localist tek-sayı temsili bu akrabalığı **kaybediyor**, parça kümesi koruyor.

### 1.6 DOĞUM çalışıyor — havuz vermeden
4 kaba kuraldan (`eylem=k → k yönü`) başlandı, havuz YOK:
```
adım 400 → 0.900 (16 kenar)
adım 4000 → 0.992 (30 kenar)     [elle havuz: 280-530 kenar]
```
Kendi doğurduğu kural:
```
eylem=1 & hedef_parça=hareket(0,0) & hedef_tip=2 & otesi_parça=hareket(1,0) → D(0,1)
eylem=1 & hedef_parça=hareket(0,0) & hedef_tip=2 & otesi_tip=1             → D(0,0)
```
**Kutu itme fiziğini kendi buldu.** "Kutu" kelimesi hiçbir yerde geçmiyor.
Katmanlı doğruluk: T0 1.000, T1 1.000, T3 1.000, T2 (kutu, n=92) 0.761.

### 1.7 KÂSE = ağırlık dosyası — DEVIR.md açık soru 6 CEVAPLANDI
| | LLM | Biz |
|---|---|---|
| ağırlık | sayı | **kural** |
| dosya | `.pt` (okunamaz) | `.kase` (JSON, **okunur**) |
| eğitim | biter, donar | bitmez |

Kaydet→yükle: 400 tahminin 400'ü aynı.

---

## 2. DÜRÜSTLÜK KAYITLARI — negatif / kısıtlı sonuçlar

### 2.1 ⚠ BİLEŞİM: küçük dünyada KÂR ETMİYOR
Bileşim kuruldu ve çalıştı — bir nöronun çıktısı (`("noron", ad, değer)`)
başka bir nöronun φ'sinde yüklem oldu. 3 bileşik kenar doğdu.

**Sonra budama onları sildi.** Çünkü bu küçük dünyada düz bir kural aynı işi
daha ucuza yapıyor. MDL doğru davrandı.

> **Bileşim ancak bileşik kavram düzünden UCUZ olduğunda kâr eder.**
> Küçük/sığ dünyada düz kural kazanır. **Büyük dünyaya geçince tekrar ölç.**
> Ölçüt: bileşik kenarlar budamadan sağ kalıyor mu?

Düz kenarın ölçülmüş sınırı: 1 tik 0.998 → **2 tik 0.672** (ψ kümesi doğru
verildiği halde). Yani ihtiyaç gerçek, sadece bu dünyada bedeli ödemiyor.

### 2.2 ⚠ `N`'in FAZ GEÇİŞİ — varsayılan parametreler KRİTİK NOKTADA
Analitik: sürekli kullanılan kenarın bütçesi sabit noktaya oturur.
```
N* = Nmax + 1 − τ
q_eff tabanı = q_kullanılan · (Nmax+1−τ)/Nmax
KRİTİK:  τ* = Nmax(1−r) + 1      r = q_rakip / q_kullanılan
```
`τ ≤ τ*` → kenar hiç susmaz, **keşif YOK** (greedy ile birebir aynı).
`τ > τ*` → keşif var.

Ölçüldü (Nmax=4, r=0.5 ⇒ τ*=3.00):
```
τ ≤ 3.00 → 1/10 kural denendi   (N YOK ile AYNI)
τ > 3.00 → 2-4/10 kural denendi
```
Teori 12 farklı (Nmax, r) ayarında test edildi: **12/12 tuttu.**

> **DEVIR.md'nin varsayılanı `Nmax=4, τ=3` tam kritik noktada.**
> TEST 2b'nin çalışma sebebi: orada q_A=0.60/q_B=0.55 ⇒ r=0.55 ⇒ τ*=2.8.
> Pay sadece **0.2**. Mekanizma gerçek ama gösterim bıçak sırtındaydı.

### 2.3 ⚠ Ödül sinyali varken UCB1 bizi 7 kat yeniyor
Aynı görev: UCB1 4471.6, N-bütçe 630.0, greedy 630.0.
`N`'in iddiası örnek verimliliği **değil**: global sayaç gerektirmemesi ve
keşfin **dönüşümlü** olması (UCB'nin bonusu kalıcı söner, N dolar).

### 2.4 TEST N5/N6 ilk halleri YANILTICIYDI
- N6 null çıktı (1.000 vs 1.000) çünkü kutu bağlamı nadir, ortalama yuttu.
  Katmanlı ölçünce gerçek fark çıktı: **0.911 vs 0.578**.
- N5 hileliydi: 2-tik hedefinin ψ değerleri havuzda hiç yoktu.
  Düzeltilince: 0.998 vs 0.672.

Ders (TEST 2 ile aynı ders): **ortalama, nadir ve belirleyici bağlamı gizler.**

---

## 3. BULUNAN VE DÜZELTİLEN HATALAR

| # | Hata | Etki | Öğrettiği |
|---|---|---|---|
| 1 | Yeni doğan kenar sırf **özgül** olduğu için kararı gaspediyordu | 0.62 → 0.43 | Özgüllük **hak edilmeli** (p ≥ 0.70) |
| 2 | Kardeş kuralın ψ'si tüm hatalardan seçiliyordu | yanlış kural | Bağlam karıştırılmamalı |
| 3 | **Ölüm doğumdan hızlıydı** — `eylem=0` 3 hatada ölüyordu, doğum 4+4 örnek istiyordu | `eylem=0` için **hiç kural doğmadı** | Kenar, **daralma şansını kullanmadan ölemez** (kenar_mimarisi §3) |
| 4 | Nadir bağlam (kutu %3) 60'lık pencerede boğuluyordu | doğum tetiklenmiyor | **Sürpriz daha uzun hatırlanmalı** (ayrı hata tamponu) |
| 5 | Kapsama budaması `uses` sayacına bakıyordu, `uses` hep 0 | budama hiç çalışmadı | `gorulme` ayrı sayaç |
| 6 | Nöron kendini kelime olarak kullandı → sonsuz döngü | çökme | **Bileşim döngüsüz olmalı → KATMAN** |

Hata 3'ün düzeltilmesi: **0.744 → 0.992.**

---

## 4. AÇIK KALANLAR

- Bileşimin büyük dünyada kâr edip etmediği (bkz. 2.1) — **ölçülecek**
- `τ`'nun `r`'ye göre otomatik ayarlanması (bkz. 2.2)
- Alfabenin kendisinin üretimi (şu an: seçim var, icat kısmi —
  `("noron",...)` atomu üzerinden)
- T2 (kutu) doğruluğu 0.761 — nadir bağlam, daha çok örnek mi gerek?

---

## 5. ZAMAN EKSENİ — `[x,y]` → `[x,y,t]`  (DEVIR.md 5.6 ölçümü)

Test: kendi kendine hareket eden nesne bir sonraki tikte nereye gidecek?
Yönü **şimdiki kareden okunamaz** (koridorda iki yanı da boş).

### 5.1 YETENEK — t olmadan görev çözülemiyor
| EKSENLER | alfabe | doğruluk | canlı kenar |
|---|---|---|---|
| `[x,y]` | 15 | **0.000** | 0 |
| `[x,y,t]` | 30 | **1.000** | 6 |

Mutlak konum atomu eklendiğinde bile `[x,y]` 0.000 — çünkü sekmeli devriyede
her hücre **iki yönde de** ziyaret ediliyor, konum yönü belirlemiyor.

Öğrenilen kurallar (konumdan bağımsız, 1 kaba kuraldan doğdu):
```
nokta(-1,0,t-1)=GEZGİN & nokta(+1,0,t)=BOŞ    → D(+1,0)    "soldan geldim, önüm açık → devam"
nokta(-1,0,t-1)=GEZGİN & nokta(+1,0,t)=DUVAR  → D(-1,0)    "soldan geldim, önüm duvar → dön"
```
**Hız ve sekme, tek kenar çiftinde.** DEVIR.md 5.6'nın "hareket yerel bir
özellik olur" iddiası doğrulandı.

### 5.2 ⚠ SIKIŞTIRMA — halka dünyasında GEÇMEDİ (dürüst negatif)
Tek yönde dönen halka (16 hücre), konum yönü belirliyor → ezber de mümkün:

| EKSENLER | doğruluk | canlı kenar |
|---|---|---|
| `[x,y]` | 1.000 | 17 |
| `[x,y,t]` | 1.000 | **17** (aynı) |

Kenar sayısı **düşmedi**. Sebep: halkada duvar geometrisi zaten yönü belli
ediyor, sistem hiçbir `t` atomu kullanmadı (öğrenilen kuralların hepsi dt=0).

> **ÇIKAN GENEL KURAL:**
> `t` ekseni tam olarak **şimdiki kare geleceği belirsiz bırakıyorsa** kâr eder.
> Belirsizlik yoksa `t` sadece alfabeyi büyütür, hiçbir şey katmaz.
> **ARC'de kullanmadan önce sor: bu oyunda şimdiki kare yeterli mi?**

### 5.3 Bulunan hata: ORİJİN SABİT KALMALI
`dt=1` için uzaysal orijini de geçmişe kaydırınca nesne kendi geçmişinde
hep `(0,0)`'da duruyor ve **hız görünmez** oluyor — tam da görmek istenen şey.
Düzeltme: zaman ekseni **kareyi** değiştirir, **orijini** değil.
Bu düzeltme 0.000 → 0.916 yaptı.

---

## 6. GERÇEK ARC OYUNLARI — BRAIN ↔ AGI köprüsü

`CODE/arc_kopru.py` gerçek `environment_files` oyunlarını açıyor.
Hedef değişken: **bir tıklamanın etki büyüklüğü** (kova: 0 / ≤4 / ≤30 / >30 hücre).
Bu `solver_gorev.md`'deki "ölü-hamle atlama"nın genellenmiş hali.

### 6.1 Bisimulation gerçek oyunlarda çalışıyor
Renkler **davranışlarına** göre gruplanıyor, isim yok:

| oyun | renk | → BİSİM TİP | gruplar |
|---|---|---|---|
| vc33 | 6 | 2 | T0={0,3,4,5,7} T1={9} |
| tn36 | 7 | **1** | hepsi aynı |
| r11l | 6 | 4 | T0={0,5} T1={1,2} T2={3} T3={15} |
| cd82 | 6 | 2 | T0={0,2,3,5,15} T1={4} |
| cn04 | 6 | 3 | T0={0} T1={4,10} T2={8,12,14} |
| dc22 | 9 | 4 | T0={0,2,3,4,5} T1={8} T2={9} T3={13,14} |

### 6.2 Öğrenme — oyuna göre ikiye ayrılıyor

| oyun | taban | öğrenilen | kenar | sonuç |
|---|---|---|---|---|
| **r11l** | 0.718 | **0.924** | 86 | **+20.6 puan** |
| bp35 | 0.952 | 0.968 | 5 | +1.6 |
| vc33 | 0.990 | 0.988 | 2 | ≈ taban (öğrenilecek şey yok) |
| tn36 | 1.000 | 1.000 | 1 | tek tip, tek etki |
| cd82 | 0.638 | 0.360 | 1 | **başarısız** |
| cn04 | 0.535 | 0.524 | 1 | **başarısız** |
| dc22 | 0.485 | 0.488 | 1 | **başarısız** |

### 6.3 ⚠ Başarısızlığın sebebi ALFABE, parametre DEĞİL — ölçüldü
Doğum ayırma eşiği tarandı:

| oyun | eşik 0.55 | 0.35 | 0.20 | 0.10 | taban |
|---|---|---|---|---|---|
| r11l | 0.924 (86 kenar) | 0.920 (122) | 0.912 (124) | 0.912 (124) | 0.718 |
| cd82 | 0.360 (1) | 0.496 (23) | 0.596 (192) | 0.600 (267) | 0.638 |
| cn04 | 0.524 (1) | 0.492 (49) | 0.492 (**1145**) | 0.492 (1386) | 0.535 |
| dc22 | 0.488 (1) | 0.148 (7) | 0.424 (289) | 0.428 (399) | 0.485 |

> Eşik düşünce **kenar patlıyor ama genelleme gelmiyor** — cn04'te 1145 kenar,
> doğruluk hâlâ tabanın altında. Bu, DEVIR.md risk 1'in (`φ` patlaması)
> **gerçek veride ölçülmüş hali**.
>
> **Gereken ayrım alfabede ifade edilebiliyorsa makine çalışıyor (r11l).**
> **Edilemiyorsa hiçbir parametre kurtarmıyor (cn04, dc22).**

**Sıradaki adım net:** alfabe `AGI/agent/perception.py`'deki NESNELERden
gelmeli. "Bu tıklama şu nesnenin içinde mi" — cd82/cn04'te eksik olan
ayrım tam olarak bu. İki proje burada birleşiyor.

### 6.4 Bulunan hata: ψ REVİZYONU (hamle 1) hiç yazılmamıştı
`kenar_mimarisi.md §3` hata anında üç yarışan hamle sayıyor:
1. **ψ'yi revize et** ← kodda YOKTU
2. q'yu düşür
3. φ'yi daralt (doğum)

Sadece 2 ve 3 vardı. Sonuç: **hiç doğru olmayan** bir kenar doğum yapamıyor
(doğum hem isabet hem hata kümesi ister, isabet kümesi boş). Kenar sadece
ölüyor, yerine bir şey gelmiyor. Gerçek oyunlarda doğruluk **0.000**'da
kalıyordu. Hamle 1 eklendi → r11l 0.000 → 0.920.

### 6.5 Bulunan hata: nöron son kenarını da kaybedebiliyordu
Bütün kenarlar ölünce nöron **sessizleşiyor** ve bir daha hiçbir şey
öğrenemiyor (geri dönüş yolu yok). Artık en az bir kenar ayakta kalıyor;
ψ revizyonu onu tekrar işe yarar hale getirebiliyor.

---

## 7. "DOĞRU" DİYE BİR ŞEY YOK — etki-güdümlü keşif

### Adem'in itirazı (mimariyi değiştirdi, kayda geçsin)
> "Bir şeyin doğru olduğunu nereden biliyorsun? ARC-AGI'de doğru olanı kimse
> bilmiyor. Sistem kendi mantığını kurmalı. Eylem yapmalı, eylem seviye
> geçiriyorsa 'bu iyi' demeli. **Bir bloğu hareket ettirmek ile seviye geçmek
> aynı şey olmalı.** Amacı hep yeni eylemler keşfetmek."

Haklı. Bölüm 1-6'daki tüm ölçümler **tahmin doğruluğunu** optimize ediyordu.
Doğruluk dışarıdan etiket kullanmıyor (sistem kendi tahminini kendi gözlemiyle
karşılaştırıyor), ama yine de **yanlış amaç** — araç, amaç değil.

### `CODE/kesif.py` — tek para birimi ETKİ İMZASI

| | ÖNCE | ŞİMDİ |
|---|---|---|
| amaç | tahmin doğruluğu | **yeni etki keşfetmek** |
| değerin kaynağı | isabet | **yenilik** |
| seviye | (ölçülüyordu) | **sadece başka bir etki — özel kod YOK** |

`q` artık "tahminim doğru mu" değil, **"buraya basmak yeni bir şey getiriyor mu"**.
`N` aynı işi yapıyor: bir fikri tüketince sırayı başkasına ver.

Etki imzası oyun-nötr: `(kova, giden_tipler, gelen_tipler, yayılım)`.
`"seviye"` kelimesi ajanın kodunda **hiç geçmiyor**.

### Sonuç — 800 tıklama bütçesi, 2 tohum

| oyun | rastgele sv | **keşif sv** | etki tipi | bağlam | ilk seviye @ |
|---|---|---|---|---|---|
| **vc33** | 0 | **1** | 4 | 66 | **24. tıklama** |
| **tn36** | 0 | **1** | 6 | 128 | 89 |
| r11l | 1 | 1 | 21 | **1367** | 77 |
| cd82 | 0 | 0 | 4 | 95 | — |

**Ödül sinyali olmadan, hedef verilmeden, "doğru" tanımlanmadan iki oyunda
seviye geçildi.** Rastgele tıklama ikisinde de 0.

Kıyas notu (dürüst): `SONUC.md`'deki temel ajan vc33'te seviye 1'e **277 ve 23**
aksiyonda ulaşıyordu (ort 150). Buradaki 24, iyi tohumla aynı seviyede —
**net üstünlük iddiası için aynı koşullarda çok tohumlu ölçüm gerek.**

⚠ r11l'de **1367 bağlam** — φ patlaması burada da var, bağlam imzası
(3×3 tip penceresi) fazla ince. Bisimulation'ın eylem uzayında da
uygulanması gerekiyor.

---

## 8. NESNE ALFABESİ — 25 oyunun tamamı

### Adem'in tasarımı
> "Her nesne bir token: genişlik, uzunluk, xy, şekli (yuvarlak/kare),
> kapladığı alan, rengi, durumu. Bu bir alfabe gibi."

`CODE/nesne.py`. Token = `(renk, genişlik, uzunluk, alan, kare_mi, şekil, simetri)`
— hepsi ölçüm, hiçbiri isim. Şekil = doluluk oranı (dolu / yuvarlak / seyrek).

**İki kazanç birden:** φ'nin alfabesi *ve* eylem uzayı. 4096 hücre → ~25 token.

### Sonuç (800 eylem/oyun, 2 tohum, ödül yok, hedef yok, "doğru" yok)

| | rastgele | **nesne-alfabe** |
|---|---|---|
| toplam seviye | 2 | **5** |
| seviye 1'e ulaşan oyun | 2/25 | **5/25** |

Seviye geçen oyunlar: **vc33 (@75), tn36 (@33), cd82 (@390), r11l (@448), sp80 (@122)**

### Kıyas (dürüst)
`DEVIR.md` §3: mevcut ajan **4/25** oyunda seviye 1 geçiyor (2000 adım bütçe,
yanlış-eleme sezgisi ile). Burada **5/25**, **800 adım** bütçeyle, ve:
- planner YOK
- ödül sinyali YOK
- "doğru" tanımı YOK
- "seviye" kelimesi ajanın kodunda GEÇMİYOR

⚠ Aynı koşullarda çok-tohumlu ölçüm yapılmadı; net üstünlük iddiası için gerek.

### Alfabe kabalığı kritik — ölçüldü
İlk denemede `şekil = tam kanonik maske` kullanıldı → **107 token**, 0 seviye.
Kabalaştırınca (doluluk oranı kovası) → **28 token**, 2 oyunda seviye.
> **Alfabe fazla ince olursa hiçbir kural genellemez.** φ patlamasının
> alfabe seviyesindeki hali.

### Bulunan hata
Nesnenin **merkezine** tıklanıyordu; ARC'de nesnenin belirli hücresi gerekir.
Rastgele hücresine tıklamaya çevrilince vc33 ve tn36 seviye geçti.

---

## 9. EYLEM BİSİMULATION + SEVİYE REÇETESİ HAFIZASI

### Yapılanlar (`CODE/nesne.py`)
- **Eylem uzayında bisimulation:** aynı etki kümesini üreten `(token, eylem)`
  çiftleri ayırt edilemez → `q` ve `N` paylaşılır.
- **Seviye reçetesi hafızası (Adem'in tasarımı):** seviye geçiren
  `(token, eylem)` kaydedilir; yeni seviyede taze bütçe + yüksek öncelikle
  geri gelir. `N` hâlâ çalıştığı için reçete tutmazsa tükenir ve sıra keşfe
  geçer — "yolda öğrenme" bedavaya geliyor, ayrı kod yok.

### ⚠ ÖLÇÜLEN HATA: gevşek bisimulation SEVİYE KAYBETTİRDİ
İlk eşik (2 gözlem yeterli): cd82'de **441 birleşme** → toplam seviye **5 → 4**.
İki çift tesadüfen aynı 2 etkiyi görmüş diye aynı değildir.
Eşik yükseltildi (≥8 kullanım + ≥2 farklı etki) → birleşmeler 441 → 0.

> **Bisimulation KANIT ister.** Erken birleştirme ayrımı yok eder.
> Alfabe fazla ince olursa genellemez (§8); fazla kaba olursa ayırt edemez.
> İkisinin arası ölçümle bulunuyor.

### ⚠ DÜRÜSTLÜK: 2 tohumda gürültü, etkiden büyük
Üç koşu: 5, 4, 4 toplam seviye. `cd82` bir koşuda geçti (@390), diğerlerinde
geçmedi. `ft09` aynı şekilde.

**Tutarlı geçenler: vc33, tn36, r11l, sp80 → 4/25.**
`cd82`/`ft09` sınırda.

> Eylem-bisimulation'ın net faydası **ölçülemedi** — tohum gürültüsü etkiden
> büyük. Gerçek karar için ≥5 tohum × daha büyük bütçe gerek.

---

## 10. PLANNER ve ÇUKUR

### 10.1 Etki-uzayı planner
Eylem uzayında 3-dizi araması = 150³ ≈ 3.4M, 800 adımda bulunamaz.
Çözüm: **etki uzayında planla** (~5 etki → 3-dizi = 125). Modeli ters çevir:
"bu etkiyi kim üretiyor?" Arama yok.

Sonuç: **5/25 seviye**, ve **m0r0 ilk kez açıldı**. cd82/cn04/dc22 kapalı.

### 10.2 ÇUKUR — mimariye bağlanışı
Çukur ayrı bir nesne DEĞİL, **zamanda doğmuş kenar**:
```
kenar_mimarisi §2 :  e = (φ, ψ, q, p, N, g)
çukur             :  φ = giriş koşulu (sahnedeki tokenlar)
                     gövde = eylem dizisi        ← zamandaki uzunluk
                     ψ = beklenen değişim
                     q, p, N = AYNI fizik
φ daraltma = UZAYDA doğum.   Çukur = ZAMANDA doğum.
Çukur birleşmesi = §4 hiyerarşi (bir çukurun çıkışı ötekinin φ'si).
```
Tek amaç: **değişim büyüklüğü**. Ödül yok, "doğru" yok, "seviye" kelimesi
karar kodunda geçmiyor. Seviye en büyük değişim olduğu için kendiliğinden hedef.

### 10.3 ⚠ ÇUKUR BÜYÜMESİ HİÇ ÇALIŞMADI — ölçüldü
**Toplam seviye: rastgele 2 → çukur 5** (planner ile aynı).
Ama merkezi mekanizma ölü:
```
birleşme = 0  → 19/25 oyunda
en_uzun  = 4  → 20/25 oyunda   (= keşif penceresi; hiç büyümemiş)
```
5 seviyenin tamamı **tek-adım keşiften** geldi, çukur birleşmesinden değil.

**Kilit sebep zinciri:**
1. Çukura giriş şartı GÖRELİ yazıldı: `değer ≥ 0.6 × en_büyük_değişim`
2. `en_deg` bir kez fırlayınca (bp35: 4213 hücre) hiçbir çukur eşiği geçemedi
3. Çukura hiç girilmedi → `uses` = 0
4. Birleşme `uses ≥ 1` istiyor → hiç birleşme yok
5. Çukur hiç uzamadı

> **Sistem kendi başarısı yüzünden kilitlendi.** Bir kez büyük değişim
> gördükten sonra kendi çukurlarını "yeterince iyi" bulmuyor.
>
> **Düzeltme:** giriş şartı en büyük değişimle kıyaslanmamalı. Çukur
> KENDİ geçmişine göre değerlendirilmeli — `q_eff` ve `p` zaten bunu ölçüyor.

### 10.4 Yol boyunca bulunan hatalar
| # | Hata | Etki |
|---|---|---|
| 1 | Her turda sıfırlayıp zinciri baştan oynama | bütçe tekrara gitti, vc33'te 0 seviye |
| 2 | Budama hiç tetiklenmiyordu (`t % 120`, `t` değişken adımla artıyor) | 180 çukur birikti, koşu yavaşladı |
| 3 | Şartsız birleştirme | 200 doğum / **199 birleşme** — ayırt edicilik yok oldu |
| 4 | Aşırı sıkı birleştirme şartı | 190 doğum / **0 birleşme** |

Hata 3 ve 4 aynı dersin iki ucu: **birleştirme kanıt ister, ama fazla kanıt
istenirse hiç birleşmez.** (§9'daki eylem-bisimulation dersiyle aynı.)

---

## 11. ÇUKUR — düzeltilmiş hali (en iyi sonuç)

### Yapılan 6 düzeltme
| # | Hata / eksik | Düzeltme |
|---|---|---|
| 1 | Giriş koşulu = sahnedeki **bütün** tokenler → alt-küme şartı bir daha tutmuyor, çukur **fiilen unutuluyor** | giriş = gövdenin **kullandığı** tokenler |
| 2 | Çukur değeri = toplam değişim → uzun çukur bedava sanılıyor, bütçe tekrara gidiyor (cd82 seviyesini kaybetti) | değer = **eylem başına** değişim (verim) |
| 3 | Gövde işe yaramasa da sonuna kadar oynanıyor | ilk 1/3'te değişim yoksa **erken çıkış** |
| 4 | Birleştirme tavanı 16 | tavan 8 + **verim düşürüyorsa birleşme yok** |
| 5 | Eylem sözlüğü hiç çıkarılmıyor | bütçenin %15'i **sistematik eylem taraması** (Adem'in m0r0 notu) |
| 6 | Eylem-tarama fazında tampon boşaltılmıyor → 121 adımlık tek çukur | pencere kontrolü o dalda da |

### Sonuç — 25 oyun, 800 eylem, 2 tohum
| | seviye |
|---|---|
| rastgele | 2 |
| **çukur (düzeltilmiş)** | **6** |

| oyun | seviye | çukur | doğum | birleşme | ilk sv@ |
|---|---|---|---|---|---|
| **lp85** | **2** | 19 | 11 | 8 | 34 |
| r11l | 1 | 59 | 92 | 6 | 70 |
| sp80 | 1 | 19 | 17 | 2 | 16 |
| tn36 | 1 | 17 | 16 | 1 | 25 |
| vc33 | 1 | 13 | 8 | 5 | 36 |

> **lp85'te SEVİYE 2** — hiçbir önceki sürüm (yenilik, nesne-alfabe, planner)
> hiçbir oyunda seviye 2'ye ulaşmamıştı. `DEVIR.md` §3'e göre mevcut ajan da
> sadece vc33'te seviye 2 görüyor.
> lp85'te 11 doğum / 8 birleşme → **çukurlar gerçekten birleşip işe yaradı.**

### Sürümlerin karşılaştırması (aynı koşullar)
| sürüm | toplam seviye |
|---|---|
| rastgele | 2 |
| nesne-alfabe | 4-5 |
| etki-uzayı planner | 5 |
| çukur (kaba giriş) | 5 |
| **çukur (düzeltilmiş)** | **6** |

⚠ Hâlâ 2 tohum. Gürültü ±1 olduğu için "6 > 5" tek başına kesin değil;
ama lp85'in seviye 2'si nitel olarak yeni.

### Süreç notu (kayda geçsin)
Arka plan koşuları `nohup ... &` ile başlatılınca, onları bekleyen tool
çağrısı iptal edilince **süreç grubuyla birlikte ölüyor**. `setsid` ile
başlatmak gerekiyor. İki koşu bu yüzden yarıda kaldı.

---

## 12. HEDEF HİPOTEZİ — üçüncü yöntem

`CODE/hedef.py`. `DEVIR.md` §3'teki Adem'in kendi gözleminden:
> "Doğru hedef hipotezi **ilk frame'de, hiç eylem yapmadan, saf geometriyle**
> oluşuyor. Ajan bunu henüz taklit etmiyor."

Oyun notları da bunu doğruluyor:
- m0r0: *"bu mavi onları siyah 5 yolunu kullanarak taşıyıp **birleştirecek**"*
- ft09: *"ortadaki kare etraftaki karelerin **şablonunu** temsil ediyor"*

İkisi de **ilk bakışta, eylem yapmadan** kurulmuş.

**Fark:** yenilik (`kesif.py`) ve çukur (`cukur.py`) EYLEMDEN SONRA öğrenir.
Hedef hipotezi EYLEMDEN ÖNCE kurulur.

Hipotez = bir **mesafe fonksiyonu** (0 = sağlandı). Ödül yok — mesafe dış
dünyadan değil, sahnenin geometrisinden. Hipotez tutmuyorsa `N` tükenir,
sıra diğerine geçer: kenar fiziği hipotez seviyesinde.

Üretilen hipotezler (hepsi saf geometri): `birleştir(T)`, `hizala(T)`,
`temizle(T)`, `çoğalt(T)`, `eşitle(T,U)`.

**İlk deneme (3 oyun):** 3/3 seviye — bp35 (@225), vc33 (@15), lp85 (@707).
**bp35 hiçbir önceki sürümde açılmamıştı**, ve orada bir hipotez gerçekten
tuttu (`q = 0.90`). vc33 @15 = şimdiye kadarki en hızlı.

### Bulunan hatalar
1. Hipotez isimleri `token[:2]` ile üretiliyordu → farklı tokenler aynı ismi
   alıyor, hipotezler karışıyordu. → tam token hash'i.
2. Hipotez kümesi yenilenince `h` hâlâ eski hipotezi gösteriyordu → `KeyError`.

---

## 13. ⚠ BİRLEŞİK (çukur + hedef) — DAHA KÖTÜ

`CODE/birlesik.py`. Fikir: hipotez YÖN verir, çukur ARAÇ olur; çukurun değeri
ham değişim değil, **hipotezin mesafesini azaltması**.

**Sonuç (aynı 4 oyun):**
| yöntem | seviye |
|---|---|
| hedef tek başına | **3/3** |
| birleşik | **2/4** (bp35 kayboldu) |

Ve **birleşme = 0** her oyunda: çukurlar oluşuyor (12, 6, 21) ama hiç
birleşmiyorlar.

> **Teşhis:** hipotez sık değişiyor; A hipotezi için kurulan çukur B'ye
> yaramıyor ve her hipotez/seviye değişiminde havuz sıfırlanıyor. Çukurun
> biriktirme avantajı, hedefin yön değiştirmesiyle yok oluyor.
>
> İki mekanizmanın **zaman ölçekleri uyuşmuyor**: çukur yavaş birikim ister,
> hipotez hızlı yön değiştirir. Birleştirmek için hipotezlerin daha kararlı
> olması ya da çukurların hipotezden bağımsız saklanması gerek.

---

## 14. ⭐ ANA BULGU: yöntemler TAMAMLAYICI, rakip değil

25 oyun, 800 eylem, 2 tohum — aynı koşullar:

| oyun | rastgele | çukur | hedef | en iyi |
|---|---|---|---|---|
| bp35 | 0 | — | **1** | 1 |
| lp85 | 0 | **2** | 1 | **2** |
| r11l | 1 | 1 (@70) | 1 (**@6**) | 1 |
| sp80 | 1 | 1 (**@16**) | 1 (@38) | 1 |
| tn36 | 0 | 1 (**@25**) | 1 (@29) | 1 |
| vc33 | 0 | 1 (@36) | 1 (**@15**) | 1 |
| **TOPLAM** | **2** | **6** | **6** | **7** |

**Aynı sayı, farklı oyunlar.** Çukur `lp85`'te seviye 2 yapıyor; hedef
`bp35`'i açıyor ve genelde çok daha hızlı (r11l @6 vs @70, vc33 @15 vs @36).

### Bu, §13'teki birleşik başarısızlığını açıklıyor
İkisini **tek ajanda eritmek** yanlış — zaman ölçekleri uyuşmuyor.
Doğrusu, ve bu zaten mimarinin kendi mantığı:

> **Yöntemin kendisi bir KENAR olmalı.**
> ```
> φ = oyunun ilk karesi (hangi yöntem buraya uygun)
> ψ = "şu yöntemi kullan"
> q = bu oyunda tuttu mu
> N = bütçesi; tükenirse sıra ötekine geçer
> ```
> Böylece ajan hangi yöntemi kullanacağını **aynı fizikle** seçer.
> Yöntem seçimi için ayrı bir mekanizma yazmaya gerek yok.

### Yöntemlerin özeti
| yöntem | ne yapar | ne zaman kazanır |
|---|---|---|
| yenilik (`kesif.py`) | görülmemiş etki arar | keşif gerektiren, ödülsüz |
| nesne-alfabe (`nesne.py`) | eylem uzayını nesne token'ına indirger | her yerde temel |
| planner (`nesne.py`) | etki uzayında zincir hedefler | m0r0 |
| çukur (`cukur.py`) | işleyen eylem dizisini saklar, birleştirir | lp85 (sv 2), derinlik |
| **hedef** (`hedef.py`) | ilk kareden geometrik hipotez, mesafe küçültür | bp35, hız |
| birleşik (`birlesik.py`) | ikisini tek ajanda erittir | ⚠ **hiçbiri** — daha kötü |

---

## 15. KADEME TESTLERİ — `CODE/test_kademe.py`

Adem: *"testleri parça parça yapmak lazım; her adımı full olduktan sonra
baştan uca test etmek gerek."* Haklı — §8-14 hep uçtan uca (25 oyun) ölçümdü,
gürültülü ve hangi parçanın çalıştığını söylemiyor.

Sentetik, deterministik, gerçek oyun yok, rastgelelik yok. **25/25 GEÇTİ.**

| kademe | ne sınandı | sonuç |
|---|---|---|
| **K5** nesne token'ı | aynı şekil+renk farklı konum → aynı token; farklı renk/şekil → farklı; ilişki atomları | 5/5 |
| **K6** çukur | doğum (değişim varsa/yoksa), giriş = gövdenin tokenleri, verim cezası (10.0 vs 2.5), kanıtsız/kanıtlı birleşme, verim düşüren birleşme reddi, N azalır/dolar, ölüm, budama tavanı | 14/14 |
| **K7** hipotez | birleştir 8→3, hizala 4→0, temizle nesne bitince tanımsız, ilk kareden üretim, isim çakışması yok | 6/6 |

> **SONUÇ: mekanizmalar bozuk değil.**
> Her parça tek başına doğru çalışıyor. Sorun mekanizmalarda değil,
> **nasıl kullanıldıklarında**: bütçe dağıtımı, hangi anda hangisine geçildiği,
> hipotezin ne kadar sabit tutulduğu.

### Yeni bulunan hata (2. aşama testinden)
Çukurdaki eylem-sözlüğü fazı `bütçe × %15` yazılmıştı. Bütçe 800→3000 olunca
tarama 120→450 adıma çıktı ve **seviye daha GEÇ geldi** (vc33 @36 → @286).
Sözlük taraması **sabit sayıda adım** olmalı, bütçenin oranı değil.

---

## 16. UZAY — vektör temsili (`CODE/vektor.py`, `test_vektor.py`)

### Adem'in tasarımı
> "Bir uzay oluşturmamız gerek, nöronlar gibi; girdiğinde uzay içine girip
> sonra çıkacak. Anlamlı uzayları birleştirince ANLAM çıkacak. Ve uzay en iyi
> vektörler/matrisler ile temsil edilir."

### Neden gerekli — ölçülmüş sorun
Token eşleşmesi **tam eşitlik**ti. İki nesne tek alanda bile farklıysa tamamen
ilgisiz sayılıyordu. Alfabe inceliğinin bu kadar kritik olmasının sebebi buydu
(§8: 107 token → 0 seviye, 28 token → seviye geliyor).

### İşlemler (VSA / bipolar MAP, 2048 boyut)
```
bind(a,b)  = a*b        BAĞLA  ("rol = değer")  — benzerliği YOK EDER, kendi tersi
bundle(..) = sign(sum)  TOPLA  ("hepsi bir arada") — benzerliği KORUR
kaydır(v,i)             SIRA kodlar
```
Anlam bu ikisinin birleşiminden çıkıyor: `bind` yeni sembol üretir, `bundle`
üyelik saklar.

### Ölçülen davranış — 20/20 GEÇTİ
| sınama | sonuç |
|---|---|
| aynı token | **1.00** |
| 1 alan farklı | **0.74** ← tam eşitlikte ilgisiz sayılırdı |
| 2 alan farklı | 0.64 |
| hepsi farklı | 0.00 |
| sıralı mı (aynı > 1fark > 2fark > hepsi) | ✓ |
| sorgu "rengi ne?" / "alanı ne?" / "kare mi?" | ✓ ← **uzaya girip çıkma** |
| `[A,B]` vs `[B,A]` | 0.29 ← sıra kodlanıyor |
| sahnedeki **benzer** nesne bulunuyor | ✓ ← tam eşitlikte kaçırılırdı |

Bağlantı: `DEVIR.md` §4 "popülasyon geometrisi — aynı nesnenin farklı
görünümleri bir **manifold** oluşturur (Chung & Abbott 2104.07059)".
Bu dosya onun somut hali.

⚠ Henüz **oyuna bağlanmadı** — kademe testi geçti, uçtan uca ölçüm yapılmadı.

---

## 17. 2. AŞAMA: bütçe değil, MEKANİZMA eksiği

Soru: seviye 1'i geçtikten sonra devam edebiliyor muyuz?
Test: bütçe 800 → 3000 (3.75×), seviye 1'e ulaşabilen oyunlarda.

| oyun | bütçe 800 | bütçe 3000 |
|---|---|---|
| vc33 | 1 (@36) | 1 (@286) |
| tn36 | 1 | 1 |
| r11l | 1 | 1 |
| sp80 | 1 | 1 |
| **lp85** | **2** | **1** ← bütçe artınca KÖTÜLEŞTİ |

vc33 seviye 1'i @286'da geçip **2700 eylem daha** kullandı, ikinciye ulaşamadı.

> **2. aşama bütçe sorunu DEĞİL.** 3.75 kat bütçe hiçbir şey değiştirmedi.
> Eksik olan bir mekanizma var.

### Bulunan hata
Çukurdaki eylem-sözlüğü fazı `bütçe × %15` yazılmıştı → bütçe 3000'de tarama
450 adım oldu, keşif geç başladı, **lp85 seviye 2'sini kaybetti**.
Sözlük çıkarma sabit iştir, bütçeyle ölçeklenmemeli. **SOZLUK_ADIM = 120** sabitlendi.

---

## 18. UZAY BAĞLANDI — kontrollü A/B, en iyi sonuç

`CODE/uzaysal.py` + `CODE/hedef3.py`.

**Tek değişiklik:** kredi `(tür, token, eylem)` ile tam eşitlikte tutuluyordu.
Artık `UzaysalKredi` devrede — hiç denenmemiş bir token, **benzerlerinin
kredisini devralıyor**.

```
kredi[k] = kendi kaydı  +  Σ benzerlik(k,k') × kredi[k']    (benzerlik ≥ 0.55)
```

### Kademe testleri K9-K12 — 19/19 GEÇTİ
| sınama | sonuç |
|---|---|
| öğrenilen token A | 0.93 |
| **hiç denenmemiş A' (1 alan fark)** | **0.86** ← tam eşitlikte 0.50'de kalırdı |
| hiç denenmemiş A'' (2 alan fark) | 0.86 |
| ilgisiz token B | 0.50 ← sızıntı yok |
| başka eylem / başka hipotez türü | 0.50 ← sızıntı yok |
| kötü deneyim de transfer oluyor | 0.13 ← benzer token boşuna denenmiyor |
| çukur girişi benzerlikle (tam alt küme değil) | ✓ |
| sahne benzerliği sıralı (1.00 > 0.89 > 0.48) | ✓ |

### Uçtan uca — KONTROLLÜ A/B (aynı kod yolu, aynı tohumlar, tek değişken)
| | toplam seviye |
|---|---|
| rastgele | 2 |
| hedef2 (tam eşitlik) | 6 |
| **hedef3 (benzerlik)** | **7** |

Kazanılan oyun: **lp85 @60**.
Seviye 1 geçenler: bp35, cd82, lp85, r11l, sp80, tn36, vc33 — **7/25**.

> Bu, şimdiye kadarki **en iyi tek-yöntem sonucu** (önceki en iyi 6).
> Ve diğer karşılaştırmalardan daha güvenilir: yöntemler arası değil,
> **aynı yöntemin tek parçası** değiştirildi.

⚠ Hâlâ 2 tohum. Ama A/B kontrollü olduğu için gürültü büyük ölçüde ortak.

### Kademe testi durumu
| kademe | konu | test |
|---|---|---|
| K1-K4 | kenar, nöron, uzay/bisim, doğum/kayıt/bileşim | 25 |
| K5 | nesne token'ı | 5 |
| K6 | çukur mekaniği | 14 |
| K7 | hipotez mesafesi | 6 |
| K8 | uzay / vektör | 20 |
| K9-K12 | kredi transferi, çukur girişi, sahne benzerliği | 19 |
| **TOPLAM** | | **89** |

---

## 19. DÜNYA MODELİ — tek gözlem, çok tahmin (`CODE/model.py`, `hedef4.py`)

### Adem'in tasarımı
> "Bir eylem dahi yaparsa bunu **sonucuyla** öğrenmeli ve kaydetmeli. Ve
> bunları kullanarak **diğer eylemleri tahmin** etmeli."

§18'de uzay sadece *kredi* içindi ("bu iyi miydi?"). Burada **tahmin** için:
```
denendi   : (token A , eylem 3) → etki E1
soruluyor : (token A', eylem 3) → ?      A' HİÇ denenmedi
cevap     : E1     çünkü A ≈ A'
```

İki yönlü genelleme:
1. **Nesne benzerliği** — aynı eylem, benzer token
2. **Eylem benzerliği** — eylemlerin ne olduğu söylenmiyor, o yüzden eylem
   vektörü **etkilerinden** öğreniliyor: aynı tokenlarda aynı etkiyi üreten
   iki eylem benzerdir. (= eylem uzayında bisimulation, vektör halinde)

### Kademe testleri K13-K16 — 15/15 GEÇTİ
| sınama | sonuç |
|---|---|
| tek gözlem → benzer token için tahmin | ✓ kaynak=`nesne` |
| ilgisiz token → **tahmin YOK** (uydurmuyor) | ✓ |
| çelişkide çoğunluk, güven 1.00 değil | 0.53 |
| `benz(eylem1, eylem2)` aynı etki üretenler | **1.00** |
| `benz(eylem1, eylem5)` farklı etki | **-0.04** |
| **1 gözlem → 3/20 çift açılıyor** | ✓ |
| **4 gözlem → 12/20 çift açılıyor** | ✓ 3× genelleme |

### Uçtan uca A/B — ⚠ DERİNLİK ARTTI, GENİŞLİK DÜŞTÜ
| | toplam seviye | oyun sayısı | en yüksek seviye |
|---|---|---|---|
| hedef3 | 6 | 6 | 1 |
| **hedef4** | **7** | 5 | **3 (lp85)** |

**lp85 = SEVİYE 3.** Hiçbir sürüm 1'i geçememişti (çukur 2 yapmıştı).
Ve sadece **17 model kaydıyla**, ilk seviye @15.

Ama bp35 ve cd82 kayboldu.

> **Ölü hamle elemesi oyunu TANIDIKTAN sonra işe yarıyor, TANIMADAN önce
> zarar veriyor.** `tahminli%` 82-98 çıktı — model neredeyse her çifti
> tahmin ediyor, zayıf kanıtla "burada bir şey olmaz" deyip canlı hamleyi
> de eliyor.
>
> **Düzeltme yönü:** ölü-hamle cezası model kapsaması/güveni yüksek
> olduğunda açılmalı, baştan değil. Bu tam olarak Adem'in iki aşaması:
> genişlik (aşama 1) ve derinlik (aşama 2) farklı ayar istiyor.

### Adım kaydı ve video — `VIDEO/`
`CODE/kayit.py` her adımı kaydedip video üretiyor: solda oyun karesi,
sağda ajanın o anki düşüncesi (aktif hipotez + mesafesi, seçilen
(token,eylem), seçim nedeni [merak/ölü tahmin/tahmin var], model tahmini vs
gerçek sonuç). Seviye atlayınca yeşil çerçeve.
Ayrıca `VIDEO/<oyun>_adimlar.txt` — adım adım metin kaydı.

### Kademe testi durumu
| kademe | test |
|---|---|
| K1-K12 | 89 |
| **K13-K16** (dünya modeli) | **15** |
| **TOPLAM** | **104** |

---

## 20. HAFIZA + ISRAR + REÇETE — ⚠ KÖTÜLEŞTİRDİ

`CODE/hafiza.py`, `CODE/hedef5.py`. Adem'in üç talebi:
1. **Israr** — *"insan eylemi sona kadar götürür; bizimki sağa gidip sola gidiyor"*
2. **Hafıza** — her eylem yazılsın, işe yarayanlar ayrı dosyaya, her oyun ayrı
3. **Reçete** — seviye geçince son hale bak, sonraki seviyede aynısını dene

### Kademe testleri K17-K19 — 20/20 GEÇTİ
Hafıza yazma/okuma/diskte kalıcılık, oyun ayrımı, reçete çıkarma,
ısrar başlat/sürdür/tüken/bırak — hepsi doğru çalışıyor.

### Uçtan uca — ⚠ DÜŞTÜ
| | toplam seviye |
|---|---|
| hedef4 | **7** |
| hedef5 | **4** |

Kayıplar: lp85 (2→1), r11l (1→0), vc33 (1→0).
Tek kazanç: **bp35 @55** (önceki en iyi @225 — 4× hızlı).
Reçete mekanizması ateşlendi (bp35'te 5, sp80'de 6, tn36'da 3 adım).

### Suçlu: ISRAR
| deneme | ısrar adımı / 800 | sonuç |
|---|---|---|
| ilk hali (`değişim > 0`) | **520-776** | 3 seviye kaybı |
| düzeltilmiş (`Δmesafe < 0`) | 4-644 | hâlâ kötü |

**Teşhis:** bu oyunlarda neredeyse **her eylem bir şeyi değiştiriyor**
(vc33'te ölçülmüştü: her tıklama kareyi değiştiriyor). Yani "değişim var"
bir sinyal değil. Yararlılığa bağladıktan sonra da benzer sorun: hipotez
mesafesi sürekli azaldığı için "yararlı" hep doğru çıkıyor.

> **Fikir doğru, tetikleyici yanlış.** İnsan gerçekten eylemi sona kadar
> götürür — ama "işe yarıyor" derken *alternatiflerden daha iyi* demek
> istiyor, "bir şey oldu" demek değil.
>
> **Düzeltme yönü:** ısrar mutlak değil **göreli** olmalı — bu eylem
> alternatiflerden daha çok mu kazandırıyor? Ya da: değişim *artıyor* mu?
> Sabit bir "yararlı" eşiği bu oyunlarda ayırt edici değil.

### Yöntem karşılaştırması (25 oyun, 800 eylem, 2 tohum)
| sürüm | toplam | en yüksek sv | not |
|---|---|---|---|
| rastgele | 2 | 1 | |
| çukur | 6 | 2 (lp85) | |
| hedef3 (uzay) | 6-7 | 1 | en geniş |
| **hedef4 (dünya modeli)** | **7** | **3 (lp85)** | **en iyi** |
| hedef5 (hafıza+ısrar) | 4 | 1 | ⚠ ısrar bozdu |

---

## 21. BAĞLAM — "bu nesne ne?" cevabı kendinde değil, etrafında

### Adem'in tespiti
> "Arada bir beyin mantık yok, yani **bağlam** yok. Bağlam kurmalı,
> etraftaki nesneler ile ne olduğunu anlamalı."

Haklı. Token nesneyi **tek başına** anlatıyordu. Ama oyun notlarının tamamı bağlam:
- ft09: *"**ortadaki** kare **etraftaki** karelerin şablonunu temsil ediyor"*
- m0r0: *"mavi 10'lar **siyah 5 yolunu kullanarak** taşınacak"*

Aynı kare başka yerde başka şey demek.

### `CODE/baglam.py` — iki tür bağlam

**1. GEOMETRİK — ilk kareden, eylem gerekmez**
```
baglam  = bundle_k [ bind(token(k), YÖN_k, UZAKLIK_k) ]
kimlik  = bind(kendi_token, baglam)
```
Komşu kendi **yönüne ve uzaklığına** bağlanıyor — yoksa "solumda duvar" ile
"sağımda duvar" aynı çıkardı.

**2. NEDENSEL — eylemden öğrenilir**
```
A'ya dokununca B değişiyorsa  →  A ile B bağlı
```
Geometrik yakınlıktan **bağımsız**: uzaktaki sayaç, kapı-anahtar gibi bağları
yakalar. Tek gözlemle karar vermiyor (en az 2).

### Kademe testleri K20-K22 — 22/22 GEÇTİ
| sınama | sonuç |
|---|---|
| aynı nesne + aynı çevre → aynı kimlik | ✓ |
| aynı nesne + **yönü değişmiş** çevre → farklı kimlik | ✓ |
| aynı komşu, farklı **uzaklık** → farklı bağlam | ✓ |
| **gerçek ızgarada:** iki özdeş nesne, biri çevrili biri yalnız | token aynı, **bağlamlı kimlik 0.15** ← ayırt ediliyor |
| A→B nedensel bağ | 1.00 |
| **uzaktan** bağ tespiti (geometrik komşu değil) | ✓ |
| tek gözlemle karar vermiyor | ✓ |

### Bu sırada bulunan gerçek hata: BUNDLE YOZLAŞMASI
`bundle` sonucu `sign()` ile ikilileştiriliyordu. İki vektör toplanırken
çelişen konumlarda toplam 0 oluyor ve oralara ne konursa konsun **farklı
bundle'lar aynı deseni paylaşıyor**.

Sebep: `a=B·y0, b=C·y4, c=C·y0, d=B·y4` için `a·b == c·d` — yani çelişki
**konumları** aynı, beraberlik çözümü ne olursa olsun ortak çıkıyor.
Ölçülen sonuç: ilgisiz iki bağlam **0.55** benzerlik (0 olmalıydı).

**Düzeltme:** bundle artık ikilileştirmiyor, gerçek değerli normalize toplam
tutuyor. Kosinüs zaten doğru çalışıyor, yozlaşma ortadan kalktı.
Bu düzeltme bütün vektör katmanını (uzay, kredi, model, bağlam) etkiliyor.

Ayrıca `icinde_mi` eşiği ölçümle 0.15 → 0.35 yapıldı
(üyeler 0.49-0.87, üye olmayan 0.26).

⚠ **Bağlam henüz ajana bağlanmadı** — kademe testi geçti, uçtan uca ölçüm yok.

### Kademe testi toplamı
| kademe | konu | test |
|---|---|---|
| K1-K4 | kenar, nöron, uzay/bisim, doğum/kayıt/bileşim | 25 |
| K5-K7 | nesne token'ı, çukur, hipotez mesafesi | 25 |
| K8 | uzay / vektör | 20 |
| K9-K12 | kredi transferi, çukur girişi, sahne benzerliği | 19 |
| K13-K16 | dünya modeli (tek gözlem → çok tahmin) | 15 |
| K17-K19 | hafıza, reçete, ısrar | 20 |
| **K20-K22** | **bağlam (geometrik + nedensel)** | **22** |
| **TOPLAM** | | **146** |

---

## 22. ÇİFT YÖNLÜ ÇIKARIM — "o öyleyse bu, bu öyleyse o"

### Adem'in sorusu
> "O öyleyse bu böyledir, bu böyleyse o öyledir — bu gibi bağlamları bizim
> nöron gibi yapımız üretmiyor mu? Bu bu varsa bu olabilir."

### Üretiyor
Kenarın kendisi zaten bir eğer-ise: `φ → ψ`. Üstüne:
- doğum `φ`'yi daraltıyor → *"bu VE bu varsa"*
- bileşim atomu `("noron", ad, değer)` → *"X şunu diyorsa"*
- nedensel bağlam → *"A'ya dokununca B değişir"*

### Üretmiyordu — `CODE/cikarim.py` ekledi
| eksik | ne demek | örnek |
|---|---|---|
| **ters çıkarım** | `ψ → φ` | "şu etkiyi gördüm, sebebi ne olabilir?" |
| **değilleme** | negatif kural | "duvar varsa hareket OLAMAZ" |
| **ayrık** | tek kural yerine sınırlı belirsizlik | "ya kayar ya döner" |
| **zincir** | A→B, B→C ⟹ A→C | uzak sonucu çıkarma |

Kenarlarımız tek yönlüydü. Ama Adem'in ft09 notu **çift yönlü bir eşleme**:
> *"beyaz 0'ın olduğu taraf turuncu 8 olacak, gri 2'nin olduğu taraf mavi 9"*

Tek yönlü kenarla bunun yarısı öğrenilir.

### Kademe testleri K24-K26 — 19/19 GEÇTİ
| sınama | sonuç |
|---|---|
| ileri: koşul → sonuç | ✓ güven 1.00 |
| **ters: sonuç → sebep** | ✓ `turuncu8` → `beyaz0_yanı` |
| aynı sonucun iki sebebi listeleniyor | ✓ her biri 0.50 |
| **hiç görülmeyen sonuç = OLAMAZ** (negatif kural) | ✓ |
| az gözlemde değilleme yapılmıyor | ✓ |
| baskın sonuç yoksa tek kural vermiyor, **ayrık küme** veriyor | ✓ |
| zincir A→B→C→D | ✓ |
| döngü sonsuza gitmiyor | ✓ |

**Ters çıkarım planlamanın temeli:** "istediğim sonuca hangi koşul götürür"
sorusu, artık ayrı bir planner algoritması olmadan kural deposundan cevaplanıyor.

⚠ Henüz ajana bağlanmadı.

### Kademe testi toplamı: **171**
K1-K4 (25) · K5-K7 (25) · K8 (20) · K9-K12 (19) · K13-K16 (15) ·
K17-K19 (20) · K20-K23 (28) · **K24-K26 (19)**
