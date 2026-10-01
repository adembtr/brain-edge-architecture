"""
zaman_halka.py — SIKISTIRMA olcumu (DEVIR.md 5.6 olcutu).

Onceki test t'nin YETENEK kattigini gosterdi (0.000 -> 1.000).
Ama Adem'in olcutu farkli: "t eklendiginde KENAR SAYISI DUSERSE dogru
yoldasin." Bunun icin gorev IKI YOLLA DA cozulebilir olmali.

Bu dunyada gezgin bir HALKA uzerinde tek yonde donuyor. Konum yonu
BELIRLIYOR -> ezber MUMKUN. Yani:
    [x,y]   -> her bolge icin ayri kural  (ezber)
    [x,y,t] -> "geldigin yone devam et"   (kural)
Kenar sayisi farki = sikistirma.
"""
import random
import dunya
from terim import Terim, Tahmin, BAGLAM
from kase import Kase, Kenar
from zaman import Iz, GEZGIN, gezgin_bul

W, H = 8, 6                      # ic halka: x=1..6, y=1..4
HARITA_H = ["1"*W] + ["1" + "0"*(W-2) + "1" for _ in range(H-2)] + ["1"*W]


def halka_yolu():
    """Saat yonunde cevre halkasi."""
    yol = []
    for x in range(1, W-1):  yol.append((x, 1))
    for y in range(2, H-1):  yol.append((W-2, y))
    for x in range(W-3, 0, -1): yol.append((x, H-2))
    for y in range(H-3, 1, -1): yol.append((1, y))
    return yol


YOL = halka_yolu()


def alfabe(t_derinlik, dx_menzil=1):
    A = []
    for dt in range(t_derinlik+1):
        for dx in range(-dx_menzil, dx_menzil+1):
            for dy in range(-dx_menzil, dx_menzil+1):
                for v in (dunya.BOS, dunya.DUVAR, GEZGIN):
                    A.append(("nokta", dx, dy, dt, v))
    for x in range(1, W-1):  A.append(("konum", x))
    for y in range(1, H-1):  A.append(("konum_y", y))
    return A


def kosu(t_derinlik, T=15000, dogum_araligi=25, pencere=2000):
    BAGLAM.dunya = dunya
    k = Kase(); k.ek_alfabe = alfabe(t_derinlik)
    n = k.noron("gezgin"); n.bagla(Kenar(Terim([]), Tahmin((1,0))))
    bos = tuple(tuple(int(c) for c in r) for r in HARITA_H)

    def kare_at(i):
        g = [list(r) for r in bos]
        x, y = YOL[i % len(YOL)]
        g[y][x] = GEZGIN
        return tuple(tuple(r) for r in g)

    i = 0
    kareler = [kare_at(i)]*(t_derinlik+1)
    odaklar = [YOL[0]]*(t_derinlik+1)
    isabet = []
    for t in range(T):
        k.tik = t
        iz = Iz(list(kareler), list(odaklar))
        tah,_,_ = n.predict(iz, 0)
        x0,y0 = YOL[i % len(YOL)]; x1,y1 = YOL[(i+1) % len(YOL)]
        gercek = (x1-x0, y1-y0)
        isabet.append(1 if tah == gercek else 0)
        n.learn(iz, 0, gercek); n.tick()
        if t % dogum_araligi == dogum_araligi-1:
            for e in list(n.kenarlar): (k.revize(e) or k.dogur(n, e))
            k.buda()
        i += 1
        kareler = [kare_at(i)] + kareler[:t_derinlik]
        odaklar = [YOL[i % len(YOL)]] + odaklar[:t_derinlik]
    return sum(isabet[-pencere:])/pencere, len(n.kenarlar), n


print("="*80)
print("BOLUM 3 — SIKISTIRMA. Halka uzerinde tek yonde donen nesne.")
print(f"Halka {len(YOL)} hucre. Konum yonu BELIRLIYOR -> ezber de mumkun.")
print("="*80)
print(f"  {'EKSENLER':<16}{'alfabe':>9}{'dogruluk':>11}{'CANLI KENAR':>14}")
kayit={}
for D in (0,1):
    ad = "[x,y]" if D==0 else "[x,y,t]"
    d,kn,n = kosu(D); kayit[D]=(d,kn,n)
    print(f"  {ad:<16}{len(alfabe(D)):>9}{d:>11.3f}{kn:>14}")
d0,k0,n0 = kayit[0]; d1,k1,n1 = kayit[1]
print(f"\n  dogruluk: {d0:.3f} -> {d1:.3f}")
print(f"  KENAR   : {k0} -> {k1}  ({k1-k0:+d})")
print(f"  >> DEVIR.md 5.6 OLCUTU: "
      f"{'GECTI — t sikistiriyor' if k1 < k0 and d1 >= d0-0.02 else 'GECMEDI'}")
print("\n  [x,y] (ezber):")
for e in sorted(n0.kenarlar, key=lambda e:-(e.p*e.q))[:5]: print(f"     {e}")
print("\n  [x,y,t] (kural):")
for e in sorted(n1.kenarlar, key=lambda e:-(e.p*e.q))[:5]: print(f"     {e}")
