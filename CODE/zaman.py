"""
zaman.py — ADRES UZAYINA ZAMAN EKSENI. DEVIR.md 5.6'nin olcumu.

Iddia: "(x,y,t)'de hareket YEREL bir ozellik olur -- egik cizgi.
Hafiza gerekmez. Tek kenar, uc kuralin isini yapar."

Olcut (Adem'in koydugu): t eklendiginde KENAR SAYISI DUSERSE dogru yol.

Test dunyasi: kendi kendine hareket eden bir nesne (deger 7).
YONU KAREDEN OKUNAMAZ -- koridorun ortasinda sagdaki de soldaki de bos.
Yon sadece ZAMANDAN okunur. Bu yuzden ayirt edici bir test.
"""
import random
from collections import namedtuple
import dunya
from terim import Terim, Tahmin, BAGLAM
from kase import Kase, Kenar

GEZGIN = 7
HARITA_G = [
    "1111111111111111",
    "1000000000000001",
    "1700000000000001",
    "1000000000000001",
    "1111111111111111",
]
KORIDOR = 14          # ic genislik: x = 1..14


class Iz:
    """
    NOKTA, (x,y,t) uzayinda. Son K kareyi tasir.
    DEVIR.md: "tum tarihi tutma, t in {0,-1,-2} yeter."
    """
    __slots__ = ("kareler", "odaklar")

    def __init__(self, kareler, odaklar):
        self.kareler = kareler      # [simdi, -1, -2, ...]
        self.odaklar = odaklar

    def kare(self, dt):
        return self.kareler[dt] if dt < len(self.kareler) else None

    def odak(self, dt):
        return self.odaklar[dt] if dt < len(self.odaklar) else (None, None)


def gezgin_bul(grid):
    for y, r in enumerate(grid):
        for x, v in enumerate(r):
            if v == GEZGIN:
                return x, y
    return None, None


def dunya_adim(grid, yon):
    """Gezgin yonunde ilerler, duvara carpinca YON DEGISTIRIR."""
    x, y = gezgin_bul(grid)
    nx = x + yon
    g = [list(r) for r in grid]
    if dunya.deger_kare(grid, nx, y) == dunya.DUVAR:
        yon = -yon
        nx = x + yon
    g[y][x] = dunya.BOS
    g[y][nx] = GEZGIN
    return tuple(tuple(r) for r in g), yon, (nx - x, 0)


def alfabe_uret(t_derinlik, dx_menzil=2, konum=True):
    """
    (x,y,t) adres uzayindaki atomlar.  t_derinlik=0 -> ZAMAN EKSENI YOK.

    konum=True: MUTLAK konum atomlari da eklenir. Bunlar olmadan gorev
    t'siz COZULEMEZ (yon kareden okunamaz). Eklenince t'siz cozum de
    mumkun olur -- ama EZBERLEYEREK, koridorun her hucresi icin ayri
    kural. Iste SIKISTIRMA tam burada olculur.
    """
    A = []
    for dt in range(t_derinlik + 1):
        for dx in range(-dx_menzil, dx_menzil + 1):
            for v in (dunya.BOS, dunya.DUVAR, GEZGIN):
                A.append(("nokta", dx, 0, dt, v))
    if konum:
        for x in range(1, KORIDOR + 1):
            A.append(("konum", x))
    return A


def kosu(t_derinlik, T=12000, tohum=0, dogum_araligi=25, pencere=1500,
         konum=True):
    BAGLAM.dunya = dunya
    rnd = random.Random(tohum)
    k = Kase()
    k.ek_alfabe = alfabe_uret(t_derinlik, konum=konum)
    n = k.noron("gezgin_yer_degisimi")
    n.bagla(Kenar(Terim([]), Tahmin((1, 0))))       # tek kaba kural

    grid = tuple(tuple(int(c) for c in r) for r in HARITA_G)
    yon = 1
    kareler = [grid] * (t_derinlik + 1)
    odaklar = [gezgin_bul(grid)] * (t_derinlik + 1)
    isabet = []
    for t in range(T):
        k.tik = t
        iz = Iz(list(kareler), list(odaklar))
        tah, _, _ = n.predict(iz, 0)
        grid2, yon, gercek = dunya_adim(grid, yon)
        isabet.append(1 if tah == gercek else 0)
        n.learn(iz, 0, gercek)
        n.tick()
        if t % dogum_araligi == dogum_araligi - 1:
            for e in list(n.kenarlar):
                (k.revize(e) or k.dogur(n, e))
            k.buda()
        grid = grid2
        kareler = [grid] + kareler[:t_derinlik]
        odaklar = [gezgin_bul(grid)] + odaklar[:t_derinlik]
    return sum(isabet[-pencere:]) / pencere, len(n.kenarlar), k, n


print("=" * 80)
print("A — ADRES UZAYINA ZAMAN EKLEME.  DEVIR.md 5.6'nin olcumu")
print("Gorev: kendi kendine hareket eden nesne bir sonraki tikte nereye gidecek?")
print(f"Koridor genisligi {KORIDOR}. Yon SU ANKI KAREDEN okunamaz.")
print("=" * 80)

print("\nBOLUM 1 — YETENEK: mutlak konum atomu YOK (ezber imkansiz)")
print(f"  {'EKSENLER':<16}{'alfabe':>9}{'dogruluk':>11}{'CANLI KENAR':>14}")
for D in (0, 1):
    eksen = "[x,y]" if D == 0 else "[x,y,t]"
    dog, kn, _, _ = kosu(D, konum=False)
    print(f"  {eksen:<16}{len(alfabe_uret(D, konum=False)):>9}{dog:>11.3f}{kn:>14}")
print("  >> t olmadan gorev COZULEMEZ. Zaman ekseni YETENEK katiyor.")

print("\nBOLUM 2 — SIKISTIRMA: mutlak konum atomu VAR (ezber mumkun)")
print(f"  {'EKSENLER':<16}{'alfabe':>9}{'dogruluk':>11}{'CANLI KENAR':>14}{'dogum':>8}")
kayit = {}
for D in (0, 1, 2):
    eksen = "[x,y]" if D == 0 else ("[x,y,t]" if D == 1 else "[x,y,t,t-1]")
    dog, kn, k, n = kosu(D, konum=True)
    kayit[D] = (dog, kn, n)
    print(f"  {eksen:<16}{len(alfabe_uret(D)):>9}{dog:>11.3f}{kn:>14}{k.dogum_sayisi:>8}")

d0, k0, n0 = kayit[0]; d1, k1, n1 = kayit[1]
print(f"\n  t eklenince dogruluk: {d0:.3f} -> {d1:.3f}   ({d1-d0:+.3f})")
print(f"  t eklenince KENAR   : {k0} -> {k1}   ({k1-k0:+d})")
print(f"  >> OLCUT (DEVIR.md 5.6): kenar sayisi DUSTU mu?  "
      f"{'EVET — dogru yol' if k1 < k0 else 'HAYIR — t derinligini dusur'}")

print("\n  [x,y] ile ogrenilenler (ezber — konuma ozel):")
for e in sorted(n0.kenarlar, key=lambda e: -(e.p*e.q))[:5]:
    print(f"     {e}")
print("\n  [x,y,t] ile ogrenilenler (kural — konumdan bagimsiz):")
for e in sorted(n1.kenarlar, key=lambda e: -(e.p*e.q))[:5]:
    print(f"     {e}")
