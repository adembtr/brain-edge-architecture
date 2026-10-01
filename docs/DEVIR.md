# DEVİR DOKÜMANI — Kenar Mimarisi

> Tasarım devir dokümanı: mimari gerekçe, nörobilim arka planı, kaynaklar ve açık sorular.
> _(Public copy: personal notes and session-handover instructions were removed; section numbers are kept because the code cites them.)_
> Yanında `edge.py` var. İkisi birlikte okunmalı.
> Tarih: 27 Ağustos 2026

---

## 0. Bir paragrafta ne oluyor

Adem, ARC-AGI-3 (ARC Prize 2026, Kaggle) için LLM'siz, veri setsiz bir ajan
kuruyor. Mevcut ajanı çalışıyor ama planner'ı yok. Paralel olarak
"beyinde bilgi nerede saklanır" sorusunu araştırdı ve bu araştırmadan
**yeni bir temel birim** çıktı: *kendi kullanım geçmişini taşıyan kenar*.
`edge.py` bunun ilk çalışan implementasyonu. Testler geçti ve `N`
değişkeninin keşif ürettiği izole ölçümle doğrulandı. Sıradaki iş: bu
kenarı ağa çıkarmak ve vc33'te ölçmek.

---

## 1. (removed in the public copy — personal notes)

---

## 2. Yarışma bağlamı (sabitler)

| | |
|---|---|
| Yarışma | ARC Prize 2026 — ARC-AGI-3, Kaggle |
| Ortam | Etkileşimli oyunlar (ARC-AGI-2'nin statik ızgaralarından farklı) |
| Girdi | Frame'ler, 64×64'e kadar, değerler 0–15 |
| Eylem | En fazla 7; ne yaptıkları söylenmiyor |
| Kazanma koşulu | Söylenmiyor |
| Skor | `min(insan_eylem / ajan_eylem, 1.0)²` |
| Kısıtlar | 1 GPU, 9 saat, offline, internet yok |
| Takvim | Kasım 2026'ya kadar |

**Skorun sonucu:** her boşa eylem karesel ceza. Verimlilik merkezi.

**Bilinen manzara:**
- Frontier sistemler Mart 2026'da %1'in altında
- Kaggle offline en iyi ~%1.2 (Tufa Labs, Duck harness, Milestone 1)
- StochasticGoose (RL + küçük ağ), Blind Squirrel (sembolik BFS)
- **25 açık oyunun hepsi zeka olmadan çözülebiliyor** (arc_agi v0.9.8'deki
  null-koordinat hatası dahil). Açık leaderboard yanıltıcı; asıl sınav
  özel set genellemesi.

---

## 3. Ajanın ölçülmüş mevcut durumu

| Modül | Durum |
|---|---|
| Seviye 1 geçen oyun | **4/25** (vc33 seviye 2'ye ulaşıyor) |
| Yanlış-eleme sezgisi | Seviye geçiren **tek** yöntem |
| SMT kural öğrenme (Z3) | 0.84–0.98 doğruluk, <0.2 sn — FAZ 1 geçti |
| Hedef hipotezi | 4/4 oyunda doğru, **frame sıfırdan, eylemsiz** |
| Meta-nesne tespiti | sayaç/tehlike/bağlı nesne — 4/4 geçti |
| Bisimulation tipleme | Eylem uzayını %63–83 kısaltıyor, **ana ajana bağlı değil** |
| **Planner** | **YOK — tek kritik eksik parça** |

**Önemli düzeltme (Adem yaptı, kayda geçsin):** CEGIS FAZ 2'de
başarısız olmadı. Seviye 1 geçilmeden, yani WIN-kuralı için hiç pozitif
örnek yokken test edildi — yapısal olarak imkânsız bir pencere. Bu bir
spec hatasıydı, algoritma hatası değil.

**Anahtar gözlem (Adem'in kendi oyun notlarından):** doğru hedef
hipotezi **ilk frame'de, hiç eylem yapmadan, saf geometriyle** oluşuyor.
Ajan bunu henüz taklit etmiyor.

**Temsil felsefesi:** her şey sayısal, sadece geometrik ilişkiler.
İnsan-okunabilir etiket yok ("elma", "duvar", "kargo" yok). Matematiksel
olarak sağlam olduğu doğrulandı, kısmen uygulandı.

---

## 4. Nörobilim izi — ne soruldu, ne bulundu

### Adem'in sorusu (el yazısı notlarından, kırmızıyla)

> "Ateşleme her yerde aynıysa, her nöron aynı şekilde patlıyorsa ve bu
> bozulmadan beynin öbür ucuna gidiyorsa — bilgi nerede?"

Notlarındaki iki kritik satır:
- Adrian çizimi (10 kg / 50 kg): darbe boyu aynı, sadece sıklık artıyor
- "Duyunun niteliğini uyaran değil, uyarılan yol belirler"
- "Bir desen ancak canlının dünyayla ilişkisini değiştirebiliyorsa bir
  şey hakkında olur"

### Varılan cevap

**Uyarılırken bilgi dört yerde birden oluşuyor:**
1. **Kimlik/adres** — hangi hattan geldiği. Anlam sinyalin içeriğinde
   değil, geometrik adresinde.
2. **Zamanlama** — frekans + spike'lar arası kesin zamanlama
3. **Popülasyon geometrisi** — N nöronun aktivite vektörü; aynı nesnenin
   farklı görünümleri bir manifold oluşturur (Chung & Abbott)
4. **Akış alanı** — bilgi noktada değil, noktanın etrafındaki yerel akış
   alanında (MARBLE)

**Uyarılmadığında:** spike'larda hiçbir yerde değil. Spike bilgiyi
taşır, saklamaz. Bilgi, akış alanını *üreten* şeyde — sinaptik ağırlıkta.

> **Beyin bilgiyi bir cevap olarak değil, bir kural olarak saklar.**

**Kâse metaforu:** kâse = ağırlık matrisinin state uzayında tanımladığı
vektör alanı. Depo değil, kural. Çukurlar (attractor) = akışın kendine
döndüğü yerler.

### Adem'in itirazları ve kabul edilen düzeltmeler

1. **"Kâse sabit olsaydı öğrenme olmazdı"** — HAKLI. LLM'de eğitim biter,
   ağırlık donar. Beyinde çıkarım ve öğrenme aynı fiziksel süreç.
   Train/test ayrımı yok.
2. **"Kâse tek değil"** — doğru. Girdi kâsenin şeklini anlık değiştirir
   (koşullu kâse).
3. **"Beyin sebepsiz başka bir şeyi tercih edebilir"** —
   itiraz geçerli. Bilim bir kısmını cevaplıyor: stokastik sinaps +
   sürekli değişen iç durum + neredeyse eşit derinlikteki çukurlarda
   simetri kırılması. "Gerçek irade mi" sorusu fizikle kapanmıyor.
4. **Adem'in küp modeli düzeltildi:** uzay anatomik olarak bölünmüş
   değil. Modaliteler *bölge* değil **yön/alt-uzay** işgal eder. Bu
   yüzden üst üste binebilirler (mixed selectivity).

### Önceki iddiaların düzeltmeleri (dürüstlük kaydı)

- "Kortekste hata taşıyan ayrı hücre popülasyonları var" — **fazla kesin
  söylendi.** Predictive coding bir *teori*; hata nöronu anatomisi
  doğrudan kanıtlanmış değil. Ororbia derlemesinin varlık sebebi bu:
  beyinde credit assignment açık problem.
- "Bilgi ağırlık matrisinde durur" — **fazla dar.** Ağırlık dışı depolar
  var: intrinsik uyarılabilirlik, vezikül havuzu (saniyeler), moleküler
  iz (saatler).
- "Bağlantı zaten var, sadece ağırlık değişir" — kısmen doğru; yapısal
  plastisite (spine turnover) gerçek.
- "Rate kodu" — tek kod değil. Rate ~80 Hz üstünde çöküyor. Tartışma
  kapanmadı.

### Nöronda "o sayı" ne — asıl bulgu

LLM'de bir bağlantı = bir float.
**Beyinde bir bağlantı = küçük bir dinamik sistem.** En az dört bileşen:

| Bileşen | Ne | Kaynak |
|---|---|---|
| `q` kuantal boyut | Bir vezikülün yanıt genliği | — |
| `p` salım olasılığı | **0.1–0.4** tipik; in vivo %10'a kadar | arxiv q-bio/0309030 |
| `N` hazır vezikül | Tükenir, rastgele yenilenir — saniyeler ölçeğinde bellek | — |
| Reseptör bileşimi | Toplama lineer değil | Beniaguev 2021 |

**Beniaguev, Segev & London (Neuron 2021):** NMDA'lı gerçekçi bir
piramidal hücreyi ms çözünürlükte taklit etmek için **5–8 katmanlı**
temporal konvolüsyonel ağ gerekiyor. NMDA çıkarılınca tek gizli katman
yetiyor. Dendritik dalda olan şey **uzay-zamansal şablon eşleştirme**.

**Marder 2012 (Neuron):** nöromodülatörler etkin sinaptik gücü ve içsel
ateşleme özelliklerini değiştirerek devreyi yeniden yapılandırıyor.
Anatomik bağlantı haritası **minimum yapıyı** verir; işlevsel devreyi
nöromodülatör ortam belirler.

**Sonuç cümlesi:** nöronda "o sayı" frekans da değil, tek skaler de
değil. Her kenar `(q, p, N, reseptör dinamiği)` durumlu, stokastik, kendi
zaman sabitleri olan bir kapı. Frekans o kapıdan geçen *sinyal*, ağırlık
kapının *durumu*.

### arXiv kaynak listesi (Adem'e verildi)

**Kodlama şeması**
- `physics/9908027` — Panzeri & Schultz. Temporal/korelasyonel/rate'i tek
  bilgi-teorik çerçevede birleştiriyor. **En net matematiksel başlangıç.**

**Popülasyon geometrisi**
- `2104.07059` — Chung & Abbott, *Neural Population Geometry*
- `2304.03376` — MARBLE (manifold geometrisi / yerel akış alanları)

**Prediktif kodlama**
- `2107.12979` — Millidge, Seth & Buckley
- `2207.12316` — aynı ekip, çıkarım+öğrenme teorisi
  ("prospective configuration" buradan)

**Kredi ataması**
- `2312.09257` — Ororbia, kapsamlı tarama
- `2403.18929` — kısa versiyon (Ororbia, Millidge, Salvatori)

**Seçiciliğin doğuşu**
- `q-bio/0505011` — V1 alıcı alan oluşumu, Hebbian + inhibisyon
- `2011.03535` — enerji-tabanlı topografik modeller
- `2308.09431` — uçtan uca topografik ağlar

**arXiv'de olmayan ama gerekenler:** Rigotti 2013 (Nature, mixed
selectivity), Fusi 2016, Olshausen & Field 1996 (sparse coding).

**Okuma sırası önerisi:** `physics/9908027` → `2104.07059` → `2107.12979`
(dil → geometri → mekanizma)

---

## 5. KENAR MİMARİSİ — tam spesifikasyon

### 5.1 Temel karar

**En küçük parça nöron değil, KENAR (sinaps).**

Sebep: biyolojide durum tutan şey sinaps; nöron nonlineer bir
birleştirici. Ve Adem'in kendi cümlesi: "onlar arasındaki bağlantı anlamı
oluşturuyor."

| Nesne | Tanım |
|---|---|
| Nokta | Durum. Frame'in geometrik/sayısal kodu. Etiket yok. |
| Kenar | O noktadaki ok. "Bu koşuldaysan, şu olur." |
| Nöron | Aynı hedef değişkeni tahmin eden kenarların toplayıcısı. **Ayrıca tanımlanmaz, ortaya çıkar.** |
| Kâse | Tüm kenarların birlikte tanımladığı akış alanı |

**Nöron kurmak = bir hedef değişken seçmek.** Ona bakan bütün kenarlar
otomatik olarak onun girdisi olur.

- Nöronun girdisi: o an `φ`'si eşleşen kenarlar (**seyrek**)
- Nöronun çıktısı: tek tahmin + güven
- Nonlineerlik: `g` kapısı (NMDA analogu) — koşullu toplama, düz toplama
  değil
- Hiyerarşi: bir nöronun çıktısı başka bir nöronun `φ`'sinde geçerse
  katman oluşur. **Katman elle tasarlanmaz.**

### 5.2 Matematik

```
Kenar:      e = (φ, ψ, q, N)          [p ve g henüz YOK]
Aktif mi:   φ(s, a) ∈ {0,1}
Etki:       q_eff = q · N/Nmax
Hata:       err = ‖gözlenen − ψ(s,a)‖  ∈ [0,1]

q ← q + α(1 − 2·err)          clip [0,1]
N ← N − 1                      (SADECE eyleme gerekçe olduysa)
N ← N + (Nmax − N)/τ           (her tik)
N ← N + β·err                  (sürpriz bilgi getirdi → bütçe iadesi)

ölüm:  q < q_min
doğum: φ'yi daralt (MDL: hatayı en az bilgiyle açıkla)
```

### 5.3 `N` — kritik ayrım

| | Soru | Hız |
|---|---|---|
| `q` | Ne kadar güçlü iddia ediyor? | Yavaş |
| `p` | Geçmişte ne kadar tuttu? | Orta |
| `N` | Şu an kullanılabilir mi? | **Hızlı** |

`q` ve `p` kuralın **dünya hakkındaki** bilgisi.
`N` kuralın **kendi geçmişi hakkındaki** bilgisi. Farklı iki şey.

**Önemli incelik (biyolojiden sapma):** `N` tahmin ederken tükenmez,
**sadece eyleme gerekçe olurken** tükenir. Yoksa doğru kuralı susturmak
saçma olurdu.

- Kenar bir sonucu öngörüyorsa → bedava
- Kenar "bu eylemi yap" diyorsa → `N − 1`

Anlamı: **bir fikre harcanan eylem bütçesi.** "Bu fikri denedim, beni bir
yere götürmedi, başkasını deneyeyim, sonra geri dönerim."

**Sonuç:** `N` politikayı kasıtlı olarak Markov olmaktan çıkarıyor. Aynı
duruma ikinci kez gelen ajan farklı davranıyor. **Keşif buradan doğuyor —
ayrı keşif kodu yazmadan.** Yanlış-eleme sezgisinin genellemesi budur.

### 5.4 Neden `p` ve `g` henüz yok

Disiplin: **ölçülmüş bir başarısızlık talep etmeden ekleme.**
Muhtemelen `(q, N)` ikilisi tek başına yeni davranış üretiyor.

**Ve `p` konusunda uyarı:** gerçek rastgelelikle kullanma. Skor
`(insan/ajan)²` — her boşa eylem karesel ceza. `p` olasılık olarak değil,
**deney seçme bilgisi** olarak kullanılmalı.

### 5.5 `φ` neyin üzerinde tanımlı — karar verildi

**Bisimulation tipleri.**

Bisimulation: iki şey, davranışları ayırt edilemiyorsa aynı tiptir.
`s₁ ~ s₂ ⟺ ∀a: a(s₁) ~ a(s₂)`. Partition refinement ile hesaplanıyor.

Neden: ayırt edilemez olanları birleştirdiği için kenar sayısını minimumda
tutar. Ve **etiketsiz nesne kimliği** üretir — "duvar" demeden duvarı
bulur.

**Ana risk buradan geliyor:** `φ` yüklem uzayı kombinatoryal patlarsa
kenar sayısı kontrolden çıkar ve sistem çalışmaz. → İlk günden **kenar
sayısını logla.**

### 5.6 Adres uzayı — boyut kararı

**2B bir ilke değil, sadece verinin şekliydi.**

- **Yanlış 3B:** 2B veriyi boş bir 3. eksene gömmek. Yarıçap-1 komşuluk
  2B'de 8, 3B'de **26** hücre. Boş eksen en pahalı şey.
- **Doğru 3B:** üçüncü eksen **zaman.** `(x, y, t)`

`(x,y,t)`'de hareket **yerel** bir özellik olur — eğik çizgi. Hafıza
gerekmez. Hız = eğim. Hızlanma = eğrilik. Üç kavram, tek geometrik
nicelik.

Bu, Minsky–Papert dersinin aynısı: **bir temsilde yerel-olmayan şey,
doğru temsilde yerel olur.**

Pratik: tüm tarihi tutma. `t ∈ {0,−1,−2}` yeter.

**KOD KARARI (tek satır, her şeyi açar):** adres uzayını `(x,y)` diye
sabitleme, **boyut listesi** olarak tut. Bugün `[x,y]`, yarın `[x,y,t]`,
sonra `[bant]`. Kod aynı kalır.

**Ölçüm:** `t` eklendiğinde kenar sayısı **düşerse** (tek kenar üç kuralın
işini yapıyor) doğru yoldasın. Artarsa `t` derinliğini 2'ye indir.

### 5.7 Çoklu duyu (SONRAKİ İŞ, şimdi değil)

ARC-AGI-3'te ses/dokunma **yok**. Bu bölüm mimarinin genel hali için.

**Ortak para birimi frekans değil, OLAY:** `olay = (adres, zaman, Δ)`
Adres kimliği taşır, `Δ` şiddeti taşır.

| Duyu | Adres uzayı | Olay ne zaman |
|---|---|---|
| Görme | 2B ızgara (x,y) | Piksel/nesne değişince |
| Ses | 1B bant (tonotopik) | Bant enerjisi değişince |
| Dokunma | 2B beden haritası | Temas başlayınca/bitince |

**Adem'in frekans sezgisi burada kurtuluyor:** seste frekans *kod* değil,
**adres**. Koklea fiziksel bir Fourier dönüşümü yapıyor. Frekans önemli —
ama kimlik olarak, sinyal olarak değil.

Ajan hangi duyunun hangisi olduğunu **bilmez.** Sadece farklı geometrili
adres uzayları görür.

**Çapraz-modal bağ ayrı modül değil** — `φ`'si iki uzaya birden bakan bir
kenar:
```
φ: dokunma-adresi T ateşledi
ψ: görme-adresi V 2 tik sonra değişecek
```
Bu kenar tuttukça `q` yükselir. Ajan **isim koymadan** T ile V'nin aynı
nesne olduğunu öğrenir.

**Duyu ilkesi:** mutlak değer değil **değişim** kodlanır. Retina
parlaklığı değil kontrastı gönderir. ARC'de karşılığı: frame'in kendisi
değil, **frame farkı** temel sinyal.

---

## 6. `edge.py` — ne yapıyor, ne kanıtlandı

### Sınıf

`Edge(phi, psi, name, q=0.5, Nmax=4.0, alpha=0.30, tau=3.0, beta=1.0)`

Metodlar: `active()`, `q_eff()`, `predict()`, `spend()`, `tick()`,
`learn(err)`, `dead()`, `specialize(extra_phi)`

Python, tek dosya, ~100 satır, NumPy yok (seyrek çalışacak;
vektörleştirme ölçümden sonra).

### TEST 1 — "engel" kavramının doğuşu — GEÇTİ

1B koridor, x=7'de duvar. Kenar: "sağ → +1".

```
t=0..3  err=0   q: 0.5 → 1.00
t=4     err=1   q=0.70   >> YENİ KENAR: "sağ->+1 & hedef_boş"
t=5     err=1   q=0.40
t=6     err=1   q=0.10
t=7     err=1   q=0.00   (öldü)
        çocuk:  q=0.70 ayakta
```

**"Duvar" kelimesi hiçbir yerde geçmiyor.** Sadece `(s+a) != WALL`
yüklemi. Saf geometri.

### TEST 2 — ilk hali YANILTICIYDI (dürüstlük kaydı)

İlk kurulumda A yanlış / B doğruydu. B kazandı ama bu **`q`'nun işiydi,
`N`'in değil.** Klasik bir güncelleme de aynısını yapardı.

### TEST 2b — `N` İZOLE EDİLDİ — ASIL KANIT

İki kenar da **hep doğru** (err=0 hep). Yani `q` hiç düşmüyor. Tek fark
yaratabilecek şey `N`.

```
N AÇIK  : A A A A A A B B A B A B
N KAPALI: A A A A A A A A A A A A
```

`N` kapalıyken sistem B'yi **hiç denemiyor.** Açıkken A tükeniyor, B
deneniyor, A doluyor, geri dönülüyor.

**İstenen şey buydu: ayrı bir keşif algoritması yazılmadan, kuralın kendi
fiziğinden çıkan keşif.**

### Parametreler ve anlamları

- `alpha = 0.30` — ne kadar çabuk ikna oluyor
- `tau = 3.0` — susan fikir kaç tikte geri gelir. **En kritik olan bu.**
  Çok küçük → takıntılı ajan. Çok büyük → dağınık ajan.
- `beta = 1.0` — sürprizin bütçe iadesi

`tau` vc33'te ölçülecek.

---

## 7. Dünyadaki en yakın işler

**AXIOM** (VERSES AI 2025, `arxiv 2505.24784` — Heins, Tschantz, Friston,
Buckley). **En yakını, çok yakın.** Sahneyi nesne bileşimleri olarak
temsil ediyor, dinamikleri parçalı doğrusal yörüngelerle modelliyor,
üretici modeli tek olaylardan mixture bileşeni büyüterek çevrimiçi
genişletiyor, periyodik Bayesian model reduction ile sadeleştiriyor.
10.000 adımda, gradyan optimizasyonu olmadan.

Çeviri: onların "mixture bileşeni doğurma"sı = bizim **kenar doğumu**;
"Bayesian model reduction"ı = bizim **budama**.

**Schema Networks** (Vicarious 2017, `arxiv 1706.04317`) — nesne yönelimli
üretici fizik simülatörü, olayların çoklu nedenlerini ayrıştırıp
nedenlerden geriye akıl yürütüyor. Breakout varyasyonlarında zero-shot
transfer.

**ARC-AGI-3 özelinde yeni makaleler:**
- `2605.05138` — Executable World Models for ARC-AGI-3
- `2512.24156` — Graph-Based Exploration for ARC-AGI-3
- `2605.25931` — Explore Before You Solve: Speed–Depth Trade-off
- `2603.24621` — ARC-AGI-3 resmi teknik rapor

**Özgün olabilecek kısım:** hiçbirinde `N` yok — kullanım bütçesi taşıyan
kural. En yakın akrabası count-based exploration, ama orada sayaç ajanın
*dışında* bir bonus; burada **kuralın kendi iç durumu**. Literatür tam
tarandı iddia edilemez, ama bu haliyle rastlanmadı.

---

## 8. Dürüst değerlendirme

**ARC-AGI-3'te LLM'leri geçer mi:** büyük ihtimalle evet. Ama bu düşük
bir bar — frontier %1'in altında, LLM'ler bu benchmarkta zaten iyi değil.

**Genel olarak "insandan iyi düşünen sistem":** hayır. Bu mimari dar,
ayrık, neredeyse tam gözlemlenebilir alanlarda çok verimli. Dilde ve
geniş dünya bilgisinde LLM'lerin yanına yaklaşmaz. Eksiklik değil, farklı
bir alet.

### Üç risk

1. **`φ` patlaması.** En büyük risk. → İlk günden kenar sayısını logla.
   Grafik yukarı fırlıyorsa mimari değil, `φ` dili sorunlu.
2. **Küçültmek büyütmekten zor.** AXIOM Bayesian model reduction'ı boşuna
   koymamış. `q < q_min` budaması muhtemelen yetmez; periyodik MDL tabanlı
   kenar birleştirme lazım olacak. Şimdiden planla.
3. **Bu planner'ı çözmüyor.** Model öğrenmeyi çözüyor. Planlama hâlâ ayrı
   bir iş — ve zaten eksik olan parça oydu. Kenar mimarisi planner'a iyi
   bir zemin verir, yerini almaz.

---

## 9. AÇIK SORULAR

1. **Nöron seviyesinde birleştirme kuralı ne?** Testlerde `max(q_eff)`
   kullanıldı — muhtemelen fazla basit. Yerini alacak şeyi **ölçüm**
   göstersin, tahmin değil.
2. `φ` yüklem gramerinin sınırı tam olarak ne? (bisimulation tipleri
   seçildi ama gramer belirlenmedi)
3. `ε`'nin metriği: frame farkı üzerinden mi, hedef değişken uzayında mı?
4. `Nmax`, `τ`, `q_min` değerleri — ölçümle belirlenecek
5. Kenar doğum eşiği
6. **Kâsenin ARC karşılığı ne?** Sinaptik ağırlığın bu mimarideki tam
   matematiksel karşılığı — planner tasarımını doğrudan belirliyor.
7. **Prospective configuration:** ağırlığı güncellemeden önce aktiviteyi
   oturtma fazı. "Hipotezi değiştirmeden önce yorumu değiştir" demek.
   ARC-AGI-3'te yanlış-eleme sezgisinin neden çalıştığını açıklıyor
   olabilir. → Planner için en ilginç ipucu.

### Daha önce belirlenmiş açık matematik soruları (hâlâ geçerli)

- **Ödül sinyali olmadan ödül fonksiyonu çıkarımı** — özgün matematik
  için en umut verici yön
- **M4: eylem uzayı üzerinde cebirsel yapı öğrenme** — en az keşfedilmiş,
  en yüksek içgörü/risk oranı

---

## 10. SIRADAKİ ADIMLAR — öncelik sırasıyla

### Hemen (bu oturum)

**Tam mimariyi kurma.** Sadece:
- `(q, N)` — `p` ve `g` yok
- Tek oyun: **vc33**
- İki log: **kenar sayısı** + **ortalama ε**

Bunlar iki saatte mimarinin yaşayıp yaşamayacağını söyler.

**Başarı kriteri:** `N` gerçekten kendiliğinden keşif üretiyorsa — yani
ayrı keşif kodu yazmadan ajan tıkandığı yerden çıkıyorsa — elde gerçek
bir şey var. **O anı ölç.** Asıl iddia orada.

### Sonra (önceden anlaşılmış sıra, hâlâ geçerli)

1. Çok-seed gerçek skor ölçümü (5+ seed × 25 oyun) — güvenilir baseline
2. Bisimulation'ın ana ajana entegrasyonu
3. Planner inşası — **vc33'te derinlik**, 25 oyunda genişlik değil

### Sonraya bırakılan

- Çoklu duyu (Bölüm 5.7). Kasım'daki iş görme-tek. Yarışma bitince ikinci
  bir adres uzayı eklemek yeterli olacak.
- **Test önerisi (yarışma sonrası):** küçük ızgara dünyası — dar görüş
  alanı + 4 bitlik temas + görüş dışı nesne için tek bantlık ses.
  Soru: sistem temas olayı ile görme olayının aynı nesneye ait olduğunu
  öğrenir mi? Öğrenirse çapraz-modal bağ mimariden bedava çıkıyor.
  Öğrenmezse `φ` dili yetersiz.

---

## 11. İlkeler (kayda geçsin)

- **Perceptron duvarı ARC-AGI-3'te hâlâ duruyor.** Minsky & Papert 1969:
  connectedness ve parity, yerel özelliklerden sonlu mertebeli
  perceptronla erişilemez. Chollet aynı topolojik yüklemleri
  ARC-AGI-3'ün Core Knowledge gereksinimlerine gömdü. → **M1 algı katmanı
  sembolik olmalı, öğrenilmiş değil.**
- **No Free Lunch bir tasarım ilkesi.** Yapısal prior'lar (MDL, komşuluk,
  bisimulation) kaçınılmaz ve dünya-bilgisi prior'larına tercih edilir.
  Tam sayısal, geometri-önce temsili haklı çıkaran şey bu.
- **Chollet'in zeka tanımı:** zeka = beceri değil, **beceri edinme
  verimliliği.** ARC özellikle dağılım-dışı genellemeyi ölçüyor.
- **LLM-seyrek hibrit** tek uygulanabilir LLM mimarisi (çağrı başına 3–5
  sn, Kaggle kısıtı altında). Ama bu proje LLM'siz gidiyor.
- **Açık leaderboard yanıltıcı.** Asıl sınav özel set.

---

## 12. Dosyalar

| Dosya | Nerede | Ne |
|---|---|---|
| `edge.py` | bu devirle birlikte | Tek kenar + 2 test |
| `DEVIR.md` | bu dosya | — |
| `kenar_mimarisi.md` | önceki çıktı | Bölüm 5'in daha kısa hali |
| `plan.md` | `AGI/` ([arc-agi3-agent](https://github.com/adembtr/arc-agi3-agent)) | Yaşayan proje planı |
| `solver_gorev.md` | proje dizini | SMT/CEGIS/SAT-planning spec |
| `hedef_gorev.md` | proje dizini | Hedef hipotezi, meta-nesne, şema transferi |
| `player/notes/*.txt` | proje dizini | Adem'in elle oynadığı oyun notları — **yer gerçeği** |

---

## 13. (removed in the public copy — session-handover instructions)

Kalan tek metodoloji ilkesi: **ölçmeden iddia etme** — bir mekanizmanın işe
yaradığını göstermek için onu izole etmek gerekiyor (bkz. §6, Test 2 / 2b).
