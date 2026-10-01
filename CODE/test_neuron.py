"""
test_neuron.py — Noron katmani olcumleri.

Disiplin (DEVIR.md B.13): olcmeden iddia etme, mekanizmayi IZOLE et.
Her testte tek degisken oynatilir, gerisi sabit tutulur.
"""

import random
import dunya
from neuron import Neuron, EdgeP, kenar_havuzu, yuklem_havuzu, KURALLAR


# ---------------------------------------------------------------------
def kosu(noron, adim_sayisi=1200, tohum=0, bolum=150, pencere=300,
         hedef_fn=None, adim_carpani=1):
    """
    Rastgele politika ile dunyada gezer, noron her tikte tahmin eder ve
    ogrenir. Train/test ayrimi YOK (mimarinin gereg-i) -> dogruluk son
    `pencere` adimin kayan ortalamasi olarak raporlanir.
    """
    rnd = random.Random(tohum)
    hedef_fn = hedef_fn or (lambda s, a, s2: dunya.yer_degisimi(s, s2))
    s = dunya.kur()
    isabetler = []
    for t in range(adim_sayisi):
        if t % bolum == 0:
            s = dunya.kur()
        a = rnd.choice(dunya.EYLEMLER)

        tahmin, guven, _ = noron.predict(s, a)

        s2 = s
        for _ in range(adim_carpani):
            s2 = dunya.adim(s2, a)
        gercek = hedef_fn(s, a, s2)

        isabetler.append(1 if tahmin == gercek else 0)
        noron.learn(s, a, gercek)
        noron.tick()
        if t % 50 == 49:
            noron.buda()
        s = dunya.adim(s, a)
    son = isabetler[-pencere:]
    return sum(son) / len(son), len(noron.kenarlar)


def yeni_noron(kural, derinlik=2):
    n = Neuron("ajan_yer_degisimi", kurall=kural)
    for e in kenar_havuzu(derinlik):
        n.bagla(e)
    return n


# =====================================================================
print("=" * 74)
print("TEST N1 — TEK KENAR vs NORON")
print("Iddia: noron (kenar demeti) tek kenardan iyi olmali.")
print("=" * 74)

tek = Neuron("ajan_yer_degisimi", kurall="max_qeff")
tek.bagla(EdgeP(lambda s, a: True,
                lambda s, a: dunya.DELTA[a],
                "her_zaman -> eylem yonu", ozgulluk=0))
d1, _ = kosu(tek)
print(f"  tek kenar ('hep eylem yonune git')   : dogruluk {d1:.3f}")

n = yeni_noron("max_qeff", derinlik=2)
d2, k2 = kosu(n)
print(f"  noron (395 kenar, max_qeff)          : dogruluk {d2:.3f}  "
      f"(budama sonrasi {k2} kenar)")
print(f"  >> NORON KAZANDI" if d2 > d1 else "  >> NORON KAZANMADI")


# =====================================================================
print()
print("=" * 74)
print("TEST N2 — BIRLESTIRME KURALI YARISI  (DEVIR.md acik soru 1)")
print("Ayni dunya, ayni tohum, ayni kenar havuzu. TEK fark: kural.")
print("=" * 74)
print(f"  {'kural':<15}{'dogruluk':>10}{'canli kenar':>14}")
sonuc = {}
for ad in KURALLAR:
    n = yeni_noron(ad, derinlik=2)
    d, k = kosu(n)
    sonuc[ad] = d
    isaret = "  <-- mevcut" if ad == "max_qeff" else ""
    print(f"  {ad:<15}{d:>10.3f}{k:>14}{isaret}")
kazanan = max(sonuc, key=sonuc.get)
print(f"\n  KAZANAN: {kazanan}  ({sonuc[kazanan]:.3f})")
print(f"  mevcut kurala gore fark: {sonuc[kazanan] - sonuc['max_qeff']:+.3f}")


# =====================================================================
print()
print("=" * 74)
print("TEST N3 — COK TOHUM (yukaridaki fark gurultu mu?)")
print("=" * 74)
print(f"  {'kural':<15}" + "".join(f"{'t'+str(t):>8}" for t in range(5)) + f"{'ort':>9}")
ort = {}
for ad in KURALLAR:
    ds = []
    for t in range(5):
        n = yeni_noron(ad, derinlik=2)
        d, _ = kosu(n, tohum=t)
        ds.append(d)
    ort[ad] = sum(ds) / len(ds)
    print(f"  {ad:<15}" + "".join(f"{d:>8.3f}" for d in ds) + f"{ort[ad]:>9.3f}")
kz = max(ort, key=ort.get)
print(f"\n  5 tohum ortalamasinda KAZANAN: {kz} ({ort[kz]:.3f}) | "
      f"max_qeff ({ort['max_qeff']:.3f}) | fark {ort[kz]-ort['max_qeff']:+.3f}")


# =====================================================================
print()
print("=" * 74)
print("TEST N4 — phi PATLAMASI  (DEVIR.md risk 1: 'ilk gunden kenar sayisini logla')")
print("=" * 74)
print(f"  {'derinlik':>9}{'baslangic kenar':>17}{'budama sonrasi':>16}{'dogruluk':>10}")
for d in (1, 2, 3):
    n = yeni_noron(kz, derinlik=d)
    bas = len(n.kenarlar)
    dog, kal = kosu(n)
    print(f"  {d:>9}{bas:>17}{kal:>16}{dog:>10.3f}")
yh = len(yuklem_havuzu())
print(f"\n  yuklem havuzu = {yh}.  derinlik k'da phi sayisi ~ C({yh},k) x 5 psi")
print(f"  k=4 icin tahmin: ~{__import__('math').comb(yh,4)*5} kenar (calistirilmadi)")


# =====================================================================
print()
print("=" * 74)
print("TEST N5 — BILESIM BOSLUGU: 2 tik ilerisi")
print("Ayni eylem 2 kez. Duz kenar bunu ancak DAHA DERIN phi ile yapabilir.")
print("=" * 74)
print(f"  {'derinlik':>9}{'kenar':>9}{'1-tik':>9}{'2-tik':>9}{'kayip':>9}")
for d in (1, 2, 3):
    n1 = yeni_noron(kz, derinlik=d)
    a1, _ = kosu(n1)
    n2 = Neuron("2tik_yer_degisimi", kurall=kz)
    for e in kenar_havuzu(d):
        n2.bagla(e)
    a2, _ = kosu(n2, hedef_fn=lambda s, a, s2: (s2.ax - s.ax, s2.ay - s.ay),
                 adim_carpani=2)
    print(f"  {d:>9}{len(kenar_havuzu(d)):>9}{a1:>9.3f}{a2:>9.3f}{a1-a2:>+9.3f}")
print("\n  NOT: 2-tik hedefinin psi kumesi 5 degil 9 deger iceriyor")
print("       ((0,0),(+-1,0),(+-2,0),(0,+-1),(0,+-2)) -> havuzda karsiligi YOK.")
print("       Duz kenar bunu ifade EDEMEZ. Bilesim tam olarak burada gerekiyor.")


# =====================================================================
print()
print("=" * 74)
print("TEST N6 — HIPOTEZ URETIMI BOSLUGU: gerekli yuklem havuzda yoksa?")
print("Kutu itme 'otesi_deger=0' yuklemini GEREKTIRIYOR. Onu havuzdan cikar.")
print("=" * 74)


def kenar_havuzu_eksik(derinlik=2, yasak="otesi_deger=0"):
    import neuron as M
    orj = M.yuklem_havuzu
    M.yuklem_havuzu = lambda: [(n, f) for (n, f) in orj() if n != yasak]
    try:
        return M.kenar_havuzu(derinlik)
    finally:
        M.yuklem_havuzu = orj


for etiket, havuz in (("TAM havuz", kenar_havuzu(2)),
                      ("EKSIK havuz (otesi_deger=0 yok)", kenar_havuzu_eksik(2))):
    n = Neuron("ajan_yer_degisimi", kurall=kz)
    for e in havuz:
        n.bagla(e)
    d, k = kosu(n)
    print(f"  {etiket:<34} dogruluk {d:.3f}  ({len(havuz)} kenar)")
print("\n  Fark ne kadar buyukse, DOGRU YUKLEMI URETEBILMEK o kadar belirleyici.")
print("  q, N, p, budama, dogum -- hicbiri bu farki kapatamaz.")
print("  Bu bosluk mimaride degil, phi'nin GELDIGI YERDE.")

print()
print("=" * 74)
print("TUM OLCUMLER TAMAM")
print("=" * 74)
