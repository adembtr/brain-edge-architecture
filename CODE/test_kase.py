"""test_kase.py — Dogum, budama, kayit, bilesim ve N'in derin olcumu."""
import random, json, os
import dunya, uzay, terim
from terim import Terim, Tahmin, BAGLAM
from kase import Kase, Kenar

BAGLAM.dunya = dunya


def kur_beyin(tipleyici):
    """SIFIRDAN. Havuz YOK. Sadece 4 kaba kural:
       'eylem k yaparsan k yonune gidersin'. Gerisi DOGACAK."""
    BAGLAM.tipleyici = tipleyici
    k = Kase(tipleyici)
    n = k.noron("yer_degisimi")
    for a in dunya.EYLEMLER:
        n.bagla(Kenar(Terim([("eylem", a)]), Tahmin(dunya.DELTA[a])))
    return k


def kosu(k, kur_fn, adim=4000, tohum=0, bolum=150, dogum_araligi=25,
         pencere=500, izle=False):
    rnd = random.Random(tohum)
    n = k.noronlar["yer_degisimi"]
    s = kur_fn(); isabet = []; iz = []
    for t in range(adim):
        k.tik = t
        if t % bolum == 0: s = kur_fn()
        a = rnd.choice(dunya.EYLEMLER)
        tahmin, _, _ = n.predict(s, a)
        s2 = dunya.adim(s, a)
        gercek = dunya.yer_degisimi(s, s2)
        isabet.append(1 if tahmin == gercek else 0)
        n.learn(s, a, gercek); n.tick()
        if t % dogum_araligi == dogum_araligi - 1:
            for e in list(n.kenarlar): (k.revize(e) or k.dogur(n, e))
            k.buda()
        if izle and t % 400 == 399:
            iz.append((t + 1, sum(isabet[-400:]) / 400, k.kenar_sayisi()))
        s = s2
    return sum(isabet[-pencere:]) / pencere, iz


# =====================================================================
print("=" * 78)
print("TEST K1 — DOGUM: havuz YOK, 4 kaba kuraldan basla, kendi kurallarini uret")
print("=" * 78)
T = uzay.tipleyici_ogren(dunya.kur3)
k = kur_beyin(T)
print(f"  baslangic: {k.kenar_sayisi()} kenar")
for e in k.noronlar["yer_degisimi"].kenarlar: print(f"     {e}")
dog, iz = kosu(k, dunya.kur3, izle=True)
print(f"\n  {'adim':>7}{'dogruluk':>11}{'kenar':>8}")
for (t, d, kk) in iz: print(f"  {t:>7}{d:>11.3f}{kk:>8}")
print(f"\n  SON dogruluk: {dog:.3f}")
print(f"  dogum={k.dogum_sayisi}  olum={k.budama_sayisi}  "
      f"birlesme={k.birlesme_sayisi}  kapsama={k.kapsama_sayisi}")
print(f"  canli kenar: {k.kenar_sayisi()}   (kiyas: elle havuz 280-530 kenardi)")
print("\n  DOGAN KURALLAR (en guvenilir 8):")
for e in sorted(k.noronlar["yer_degisimi"].kenarlar,
                key=lambda e: -(e.p * e.q))[:8]:
    print(f"     {e}  (t={e.dogdu} dogdu)")

# =====================================================================
print()
print("=" * 78)
print("TEST K2 — .kase DOSYASI: beyin diske yazilip aynen geri geliyor mu?")
print("=" * 78)
yol = os.path.join(os.path.dirname(os.path.abspath(__file__)), "beyin.kase")
k.kaydet(yol)
boyut = os.path.getsize(yol)
k2 = Kase.yukle(yol, T)
BAGLAM.noronlar["yer_degisimi"] = k2.noronlar["yer_degisimi"]
rnd = random.Random(999); s = dunya.kur3(); ayni = 0; N = 400
for t in range(N):
    if t % 150 == 0: s = dunya.kur3()
    a = rnd.choice(dunya.EYLEMLER)
    p1, _, _ = k.noronlar["yer_degisimi"].predict(s, a)
    p2, _, _ = k2.noronlar["yer_degisimi"].predict(s, a)
    ayni += (p1 == p2)
    s = dunya.adim(s, a)
print(f"  dosya      : beyin.kase  ({boyut} bayt, {k2.kenar_sayisi()} kenar)")
print(f"  {N} tahminin {ayni} tanesi AYNI  -> {'TAM AYNI' if ayni==N else 'FARK VAR'}")
print("\n  dosyanin ic-i (ilk kenar) — LLM'in .pt'si okunamaz, bu OKUNUR:")
d = json.load(open(yol))
print("   ", json.dumps(d["noronlar"][0]["kenarlar"][0], ensure_ascii=False))
print("    tipler   :", d["tipler"])
print("    istatistik:", d["istatistik"])
BAGLAM.noronlar["yer_degisimi"] = k.noronlar["yer_degisimi"]

# =====================================================================
print()
print("=" * 78)
print("TEST K3 — N'IN DERIN OLCUMU  (Adem: 'neden azaliyor? artmasi gerekmez mi?')")
print("=" * 78)
from edge import Edge

def kesif_kosusu(mod, adim=16, kenar_sayisi=4):
    """4 kural, HEPSI DOGRU. Tek fark N'in davranisi."""
    es = [Edge(lambda s,a: True, (lambda i: lambda s,a: i)(i), f"K{i}",
               q=0.60 - 0.01*i) for i in range(kenar_sayisi)]
    dizi = []
    for t in range(adim):
        w = max(es, key=lambda e: e.q_eff())
        dizi.append(w.name)
        if mod == "azalir":   w.N = max(0.0, w.N - 1.0)
        elif mod == "artar":  w.N = min(w.Nmax, w.N + 1.0)
        elif mod == "sabit":  pass
        w.learn(0.0)
        if mod != "sabit":
            for e in es: e.tick()
    return dizi, len(set(dizi))

print("  4 kural, hepsi DOGRU, hicbiri hata yapmiyor. q ayirt edemiyor.")
for mod, aciklama in (("azalir", "N kullanimda AZALIR  (mevcut)"),
                      ("artar",  "N kullanimda ARTAR   (Adem'in onerisi)"),
                      ("sabit",  "N yok                (klasik)")):
    dizi, farkli = kesif_kosusu(mod)
    print(f"  {aciklama:<34} {' '.join(dizi)}   -> {farkli}/4 kural denendi")
print("""
  OKUMA:
    AZALIR -> sistem 4 kuralin hepsini gezer, sonra doner. KESIF.
    ARTAR  -> ilk kural surekli guclenir, digerleri HIC denenmez. TAKINTI.
    SABIT  -> ayni sey. Klasik guncelleme.

  Adem hakli ki kullanim GUCLENDIRMELI -- ama o isi q yapiyor (YAVAS).
  N farkli bir soruyu cevapliyor: 'su an bunu tekrar denemeli miyim?'
  Ikisi ayni anda calisir: kullan -> q ARTAR (ogrenme), N AZALIR (sira baskasinda).
  Biyolojide de boyle: LTP guclendirir (dakika-saat), vezikul tukenir (saniye).""")

# =====================================================================
print()
print("=" * 78)
print("TEST K4 — BILESIM: bir noronun ciktisi baska bir noronun KELIMESI olur")
print("=" * 78)
n_say = k.noron("sayac_degisimi", katman=1)   # ust katman: alt noronu kelime olarak kullanabilir
n_say.bagla(Kenar(Terim([]), Tahmin((0,))))
n_say.bagla(Kenar(Terim([("noron", "yer_degisimi", 0, 0)]), Tahmin((0,))))
rnd = random.Random(7); s = dunya.kur3()
isabet = []
for t in range(3000):
    k.tik = t
    if t % 150 == 0: s = dunya.kur3()
    a = rnd.choice(dunya.EYLEMLER)
    tah, _, _ = n_say.predict(s, a)
    s2 = dunya.adim(s, a)
    ger = (s2.sayac - s.sayac,)
    isabet.append(1 if tah == ger else 0)
    n_say.learn(s, a, ger); n_say.tick()
    if t % 25 == 24:
        for e in list(n_say.kenarlar): (k.revize(e) or k.dogur(n_say, e))
        k.buda()
    s = s2
print(f"  'sayac degisecek mi' noronu: dogruluk {sum(isabet[-500:])/500:.3f}, "
      f"{len(n_say.kenarlar)} kenar")
bilesik = [e for e in n_say.kenarlar
           if any(at[0] == "noron" for at in e.phi.atomlar)]
print(f"  BASKA NORONU kelime olarak kullanan kenar: {len(bilesik)}")
for e in bilesik[:4]: print(f"     {e}")
print("\n  >> 'noron=yer_degisimi(0,0)' artik bir YUKLEM. Sistemin kendi urettigi kelime.")

print()
print("=" * 78); print("TUM KASE OLCUMLERI TAMAM"); print("=" * 78)

# =====================================================================
print()
print("=" * 78)
print("TANI — kalan hata NEREDE? (hedef hucrenin TIPINE gore katmanli)")
print("=" * 78)
n = k.noronlar["yer_degisimi"]
rnd = random.Random(123); s = dunya.kur3()
kat = {}
for t in range(3000):
    if t % 150 == 0: s = dunya.kur3()
    a = rnd.choice(dunya.EYLEMLER)
    dx, dy = dunya.DELTA[a]
    hv = dunya.deger(s, s.ax+dx, s.ay+dy)
    ti = T.tip_of(hv)
    tah, _, kaz = n.predict(s, a)
    s2 = dunya.adim(s, a)
    ok = 1 if tah == dunya.yer_degisimi(s, s2) else 0
    kat.setdefault(f"T{ti} (ham {hv})", []).append(ok)
    n.learn(s, a, dunya.yer_degisimi(s, s2)); n.tick()
    if t % 25 == 24:
        for e in list(n.kenarlar): (k.revize(e) or k.dogur(n, e))
        k.buda()
    s = s2
print(f"  {'hedef tipi':<18}{'ornek':>8}{'dogruluk':>11}")
for ad in sorted(kat):
    v = kat[ad]
    print(f"  {ad:<18}{len(v):>8}{sum(v)/len(v):>11.3f}")
print(f"\n  toplam kenar: {len(n.kenarlar)}   dogum: {k.dogum_sayisi}")
print("  TUM KENARLAR:")
for e in sorted(n.kenarlar, key=lambda e: str(e.phi)):
    print(f"     {e}")
