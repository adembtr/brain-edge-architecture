# DURUM — nerede kaldık (28 Ağustos 2026)

> `DEVIR.md` ve `kenar_mimarisi.md` **tasarım**; `BULGULAR.md` **bütün ölçümler**;
> bu dosya **yarın nereden devam edileceği**.

---

## 1. Tek cümle

Mimari çalışıyor ve gerçek ARC oyunlarında **7 seviye** geçiyor (rastgele 2),
`lp85`'te **seviye 3**. Ama son eklediğim üç şey (hafıza+ısrar, bağlam, bağlamlı
kimlik) **kötüleştirdi** — hepsi aynı sebepten: anahtar uzayı patlıyor.

---

## 2. En iyi sürüm: `CODE/hedef4.py`

```
rastgele        2 seviye
çukur           6      (lp85'te sv 2)
hedef3 (uzay)   6-7    (en geniş)
HEDEF4          7      (lp85'te sv 3)   ← TEMEL AL
hedef5 (ısrar)  4      ⚠ kötüleşti
hedef6 (bağlam) lp85'te 1  ⚠ kötüleşti
```

Seviye 1 geçenler: bp35, cd82, lp85, r11l, sp80, tn36, vc33.
Hız: r11l @6, vc33 @15, sp80 @38, tn36 @41, lp85 @60, cd82 @137, bp35 @55.
(Kıyas: `AGI/SONUC.md`'de mevcut ajan vc33'te sv1 için ort **150** aksiyon.)

---

## 3. ⭐ Günün tek sistematik bulgusu

**Her temsil zenginleştirmesi anahtar uzayını patlatıyor ve genellemeyi öldürüyor.**

| seviye | önce | sonra | sonuç |
|---|---|---|---|
| φ atomları | eşik 0.55 | eşik 0.20 | cn04'te **1145 kenar**, doğruluk taban altı |
| token | 28 | 107 | **0 seviye** |
| bağlam | 17 kimlik | 255 kimlik | lp85 **sv2 → sv1** |

Bütçe çözmüyor: 800 → 3000 (3.75×) hiçbir şey değiştirmedi.

**Önerilen çözüm (yarının işi):** alfabeyi elle tasarlama, **öğren**.
```
1. EN KABA token ile başla (sadece renk, ~6 kimlik)
2. Hata nerede yoğunlaşıyor ölç
3. SADECE orada bir alan aç (boyut / şekil / komşu / bağlam)
4. Ölçülebilir kazanç yoksa GERİ AL
5. Tekrarla
```
Bu, `kenar_mimarisi §3`'teki doğum kuralının **alfabeye** uygulanması.
Kenarlara uyguladık, alfabeye hiç uygulamadık.

---

## 4. Kurulu ama BAĞLANMAMIŞ (hepsi test geçti, kullanılmayı bekliyor)

| dosya | ne yapar | test |
|---|---|---|
| `baglam.py` | geometrik + nedensel bağlam | K20-K22, 22/22 |
| `kimlik.py` | bağlamlı kimlik anahtar olarak | K23, 6/6 |
| `cikarim.py` | **ters çıkarım**, değilleme, ayrık, zincir | K24-K26, 19/19 |
| `hafiza.py` | oyuna özel kalıcı hafıza + reçete | K17-K19, 20/20 |

`cikarim.py` özellikle önemli: "istediğim sonuca hangi koşul götürür"
sorusunu ayrı planner algoritması olmadan cevaplıyor.

---

## 5. Kademe testleri: **171**, hepsi geçiyor

K1-K4 kenar/nöron/uzay/doğum · K5-K7 token/çukur/hipotez · K8 vektör ·
K9-K12 kredi transferi · K13-K16 dünya modeli · K17-K19 hafıza/ısrar ·
K20-K23 bağlam · K24-K26 çift yönlü çıkarım

Çalıştırma:
```bash
cd CODE
V=python   # arc_agi kurulu ortam (ARC-AGI-3-Agents venv'i); AGI_DIR = arc-agi3-agent klonu
for t in edge test_kademe test_vektor test_uzaysal test_model test_hafiza test_baglam test_cikarim; do $V $t.py; done
```

**Bu testlerin söylediği:** mekanizmalar tek tek doğru. Sorun onlarda değil,
birleştirilmelerinde ve ayarlarında.

---

## 6. Yarın için sıra

1. **Adaptif alfabe** (§3) — günün tek sistematik hatasına doğrudan saldırıyor
2. **Konsolidasyon** — `hedef4`'ü temel al, üstüne **tek seferde tek şey** ekle,
   kurulu A/B düzeneğiyle ölç, kazanmayanı geri al
3. Sonra: `cikarim.py`'yi bağla (ters çıkarım planlamanın temeli)

**Yapmayalım:** daha fazla temsil eklemek (hepsi kurulu, sorun bu değil),
bütçe artırmak (ölçtük, işe yaramıyor).

---

## 7. Pratik notlar

- **Arka plan koşusu `setsid` ile başlatılmalı.** `nohup ... &` yetmiyor;
  bekleyen tool çağrısı iptal edilince süreç grubuyla ölüyor. İki koşu böyle kayboldu.
- `pkill -f <ad>` kendi kabuğunu öldürüyor (exit 144). PID ile öldür, ayrı çağrıda.
- Python: ARC-AGI-3-Agents venv'i (`arc_agi` kurulu)
- Oyunlar: `AGI/environment_files/` (25 oyun, offline, arc_agi 0.9.8)
- Videolar: `BRAIN/VIDEO/` (8 oyun, mp4 + adım adım metin)
- Hafıza: `BRAIN/HAFIZA/<oyun>.txt` / `_ise_yarayan.txt` / `_recete.txt`
- **LLM yok.** Hepsi geometri, benzerlik ve kenar fiziği.

---

## 8. Makale

`MAKALE/makale.pdf` hazır (5 sayfa, derlendi), **yayınlanmadı**.
_(Taslak bu açık depoya dahil edilmedi; `MAKALE/` altında sadece deney kodları ve sonuç JSON'ları var.)_
`N`'in faz geçişi: `τ* = Nmax(1−r)+1`, 12/12 ayarda doğrulandı.
Dürüstlük notu: varsayılan `Nmax=4, τ=3` tam kritik noktada.
