# Kenar Mimarisi — Temel Birim Spesifikasyonu

## 0. Tek cümle

Sistemin en küçük parçası nöron değil **kenar**tir. Kenar = kendi kullanım
geçmişini taşıyan küçük bir tahminci. Nöron, aynı hedefi tahmin eden
kenarların demeti olarak *ortaya çıkar*, ayrıca tanımlanmaz.

---

## 1. Uzayın nesneleri

| Nesne | Tanım |
|---|---|
| Nokta | Durum. Frame'in geometrik/sayısal kodu. Etiket yok. |
| Kenar | O noktadaki ok. "Bu koşuldaysan, şu olur." |
| Nöron | Aynı hedef değişkeni tahmin eden kenarların toplayıcısı. |
| Kâse | Tüm kenarların birlikte tanımladığı akış alanı. |

Kâse bir depo değil, bir kuraldır. Bilgi kenarların şeklinde durur.

---

## 2. Kenarın yapısı

```
e = (φ, ψ, q, p, N, g)
```

| Alan | Anlam | Zaman sabiti |
|---|---|---|
| `φ` | Önkoşul. Geometrik yüklem + (opsiyonel) eylem. | — |
| `ψ` | Tahmin. Bir sonraki tikte hedef değişken ne olacak. | — |
| `q` | Büyüklük. İddianın gücü. | Yavaş |
| `p` | Güvenilirlik. Geçmişte tutma oranı. | Orta |
| `N` | Bütçe. Kullanıldıkça tükenir, zamanla dolar. | Hızlı |
| `g` | Kapı. Hangi kenar aktifse bu geçer. | — |

`φ`'nin tanım kümesi: **bisimulation tipleri.** Ayırt edilemez olanlar
birleştirildiği için kenar sayısı minimumda kalır.

---

## 3. Güncelleme kuralları

```
ε   = gözlenen − ψ

q  ← q + α·ε                     (yavaş)
p  ← p + η·(isabet − p)          (orta)
N  ← N − 1                       (kullanımda)
N  ← N + (Nmax − N)/τ            (her tik, pasif dolum)
```

Hepsi lokal. Global etiket yok, backprop yok, ödül sinyali yok.
Tek girdi `ε`.

### Yapısal plastisite

- `p < p_min` → kenar ölür (budama)
- Bir bağlamda `ε` ısrarla yüksek → yeni kenar doğar

### Hata anında üç yarışan hamle

1. `ψ`'yi revize et
2. `q`'yu düşür
3. **`φ`'yi daralt, yeni kenar doğur** ← MDL'e göre genellikle bu kazanır

3. seçenek, isim koymadan kavram üretir (bkz. Bölüm 5 örneği).

---

## 4. Nöron

Nöron kurmak = **bir hedef değişken seçmek.**

- **Girdi:** o an `φ`'si eşleşen kenarlar (seyrek)
- **Çıktı:** tek tahmin + güven
- **Nonlineerlik:** `g` kapısı. Eşi aktif değilse kenar hiç sayılmaz.
  Toplama değil, koşullu toplama. (NMDA analogu.)

Örnek nöronlar: "A'nın sütunu", "sayaç değeri", "seviye biter mi".

**Hiyerarşi:** bir nöronun çıktısı başka bir nöronun `φ`'sinde geçerse
katman oluşur. Katman elle tasarlanmaz, kullanımdan doğar.

---

## 5. Çalışma örneği — "engel" kavramının doğuşu

Tip-A ve tip-B nesne (bisimulation'dan, isimsiz).

**Kenar₁**
- `φ`: A ile B aynı satırda, mesafe > 0, eylem = a2
- `ψ`: A'nın sütunu +1
- `q=0.8, p=0.9, N=5/5`

**Tik 1.** a2 → A gerçekten +1 gider.
`ε = 0` → `p` ↑, `N` = 4, `q` sabit.

**Tik 2.** A artık B'ye bitişik. a2 → A kımıldamaz.
`ε` büyük → `φ` daralır: `mesafe > 1`.

Sonuç: sistem "engel" kavramını **hiç isim koymadan** üretti.

---

## 6. LLM'den üç farkı

**1. Seyreklik.** LLM'de her nöron her adımda tam vektör alır ve tüm
ağırlıklar çarpılır. Burada sadece eşleşen kenarlar uyanır.

**2. Train/test ayrımı yok.** LLM'de eğitim biter, ağırlık donar. Burada
her tahmin kendisini üreten kuralı da değiştirir.

**3. Aynı girdi farklı çıktı verebilir.** `N` tükendiği için sistem ikinci
seferde başka kenarı dener. LLM'de karşılığı yok.

→ (3) en önemlisi: **keşif, ayrı bir keşif algoritması yazmadan sistemin
fiziğinden çıkıyor.** Yanlış-eleme sezgisinin genellemesi budur.

---

## 7. Uygulama disiplini

- **Önce `(q, N)` ikilisiyle başla.** Muhtemelen tek başına yeni davranış
  üretir.
- `p` ve `g`'yi ancak **ölçülmüş** bir başarısızlık talep ettiğinde ekle.
- `p`'yi gerçek rastgelelikle kullanma. Skor `(insan/ajan)²` — her boşa
  eylem karesel ceza. `p` olasılık değil, **deney seçme bilgisi** olarak
  kullanılmalı.
- Depth-before-breadth: önce vc33, sonra 25 oyun.

---

## 8. Biyolojik dayanak (doğrulanmış)

- **Sinaps tek sayı değil:** merkezi sinapslarda salım olasılığı p tipik
  0.1–0.4; in vivo %10'a kadar düşebiliyor. → `p`
- **Vezikül havuzu tükenir/yenilenir:** saniyeler ölçeğinde bellek. → `N`
- **Toplama lineer değil:** NMDA'lı piramidal hücreyi taklit için 5–8
  katmanlı TCN gerekiyor (Beniaguev, Segev & London 2021); dendritik dal
  uzay-zamansal şablon eşleştirme yapıyor. → `g`
- **Ağırlık bağlamla anlık çarpılır:** nöromodülatörler etkin sinaptik
  gücü değiştirip devreyi yeniden yapılandırıyor; anatomi minimum yapıyı
  verir, işlevsel devreyi bağlam belirler (Marder 2012). → `g`
- **İç içe zaman ölçekleri:** kalsiyum tabanlı plastisite + synaptic
  tagging-and-capture; hızlı nöron dinamiğini yavaş ağırlık dinamiğine
  kalsiyum bağlıyor. → `q`/`p`/`N` ayrımı

### Analog karşılıklar
- `N` → kondansatör (kullanımda boşalır, τ ile dolar)
- `q` → memristif yavaş bellek
- `g` → koşullu geçit

---

## 9. Açık kalan noktalar

- `φ` yüklem dili tam olarak ne? (bisimulation tipleri seçildi, ama
  yüklem gramerinin sınırı belirlenmedi)
- `ε`'nin metriği: frame farkı üzerinden mi, hedef değişken uzayında mı?
- Kenar doğum eşiği ve `Nmax`, `τ` değerleri — ölçümle belirlenecek
- Duyu ilkesi: mutlak değer değil **değişim** kodlanmalı. Frame'in
  kendisi değil, frame farkı temel sinyal. (Frekans fikrinin kurtarılan
  hali — frekans şiddeti taşır, kimliği taşımaz; kimliği adres taşır.)
