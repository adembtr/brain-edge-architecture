"""
arc_kopru.py — BRAIN <-> ARC-AGI-3 koprusu.

BRAIN'in dogruladigi iki parcayi GERCEK oyunlara baglar:
  1. BISIMULATION TIPLEME  -> renkler davranislarina gore gruplanir.
     Oyun 7 renk gosteriyor olabilir ama DAVRANIS tipi 3 olabilir.
     Bu, phi'nin alfabesini kucultur (olculdu: 530->280 kenar, dogruluk arti).
  2. DOGUM                 -> "bu tiklama bir sey degistirir mi?" kurallari
     havuz verilmeden ogrenilir.

Neden bu hedef degisken: solver_gorev.md'deki "OLU-HAMLE ATLAMA" tam bu.
Skor (insan/ajan)^2 -> her bos tiklama karesel ceza. Olu hamleyi DENEMEDEN
bilmek dogrudan skor.
"""
import os, sys, random, json
from collections import Counter

AGI = os.environ.get("AGI_DIR", os.path.abspath(os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "..", "arc-agi3-agent")))
os.environ.setdefault("OPERATION_MODE", "offline")
os.environ.setdefault("ENVIRONMENTS_DIR", f"{AGI}/environment_files")
os.environ.setdefault("MPLBACKEND", "agg")
sys.path.insert(0, f"{AGI}/denme")
sys.path.insert(0, f"{AGI}/denme/infra")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from terim import Terim, Tahmin, BAGLAM        # noqa: E402
from kase import Kase, Kenar                   # noqa: E402
from uzay import BisimTipleyici                # noqa: E402


# =====================================================================
# ARC durumu -> BRAIN noktasi
# =====================================================================
class ArcNokta:
    """Bir tiklama baglami. Nokta = (grid, tiklanan koordinat)."""
    __slots__ = ("grid", "cx", "cy")

    def __init__(self, grid, cx, cy):
        self.grid, self.cx, self.cy = grid, cx, cy

    def deger(self, dx=0, dy=0):
        y, x = self.cy + dy, self.cx + dx
        if 0 <= y < len(self.grid) and 0 <= x < len(self.grid[0]):
            return self.grid[y][x]
        return -1


TIPLEYICI = BisimTipleyici()


def _tip(v):
    return TIPLEYICI.tip_of(v)


# --- atomlar (BAGLAM'a gerek yok, dogrudan noktadan okur) -------------
import terim as T                              # noqa: E402


def _at_tik_tip(s, a, t):
    return _tip(s.deger()) == t


def _at_komsu_tip(s, a, dx, dy, t):
    return _tip(s.deger(dx, dy)) == t


def _at_tik_renk(s, a, v):
    return s.deger() == v


def _at_bant_x(s, a, b, n):
    """Kareyi n dilime bol, tiklama hangi dilimde. Oyun-notr geometri."""
    return (s.cx * n) // len(s.grid[0]) == b


def _at_bant_y(s, a, b, n):
    return (s.cy * n) // len(s.grid) == b


def _at_yakinda_tip(s, a, r, t):
    """Yaricap r icinde t tipinden hucre var mi. (komsuluk prior'i)"""
    for dy in range(-r, r + 1):
        for dx in range(-r, r + 1):
            if _tip(s.deger(dx, dy)) == t:
                return True
    return False


def _at_ayni_tip_sayisi(s, a, k):
    """4-komsulukta tiklananla AYNI tipten kac hucre var (0..4)."""
    t0 = _tip(s.deger())
    return sum(1 for (dx, dy) in ((0, -1), (0, 1), (-1, 0), (1, 0))
               if _tip(s.deger(dx, dy)) == t0) == k


T.ATOM_TABLOSU["tik_tip"] = _at_tik_tip
T.ATOM_TABLOSU["komsu_tip"] = _at_komsu_tip
T.ATOM_TABLOSU["tik_renk"] = _at_tik_renk
T.ATOM_TABLOSU["bant_x"] = _at_bant_x
T.ATOM_TABLOSU["bant_y"] = _at_bant_y
T.ATOM_TABLOSU["yakinda"] = _at_yakinda_tip
T.ATOM_TABLOSU["ayni_tip_n"] = _at_ayni_tip_sayisi


def alfabe(tip_sayisi, renkler, tipli=True):
    A = []
    if tipli:
        for t in range(tip_sayisi):
            A.append(("tik_tip", t))
            for (dx, dy) in ((0, -1), (0, 1), (-1, 0), (1, 0),
                             (-2, 0), (2, 0), (0, -2), (0, 2)):
                A.append(("komsu_tip", dx, dy, t))
            A.append(("yakinda", 2, t))
            A.append(("yakinda", 4, t))
        for kk in range(5):
            A.append(("ayni_tip_n", kk))
    else:
        for v in renkler:
            A.append(("tik_renk", v))
    # GEOMETRI (her iki dilde de): oyun-notr konum bantlari
    for b in range(4):
        A.append(("bant_x", b, 4)); A.append(("bant_y", b, 4))
    return A


# =====================================================================
def kesif_topla(oyun, adim=600, tohum=0):
    """Rastgele tiklayarak (renk -> etki) gozlemi biriktir."""
    from env import Env
    rnd = random.Random(tohum)
    e = Env(oyun)
    o = e.reset()
    H, W = len(o["grid"]), len(o["grid"][0])
    kayit = []
    for t in range(adim):
        cx, cy = rnd.randrange(W), rnd.randrange(H)
        onceki = o["grid"]
        renk = onceki[cy][cx]
        o2 = e.step("click", 6, cx, cy)
        sonraki = o2["grid"]
        n_deg = sum(1 for yy in range(len(onceki))
                    for xx in range(len(onceki[0]))
                    if onceki[yy][xx] != sonraki[yy][xx])
        # KOVA: oyun-notr, olcek-serbest. 0 / kucuk / orta / buyuk
        kova = 0 if n_deg == 0 else (1 if n_deg <= 4 else
                                     (2 if n_deg <= 30 else 3))
        kayit.append((onceki, cx, cy, renk, kova,
                      o2["level"] - o["level"]))
        o = o2
        if o["state"] not in ("NOT_FINISHED", "NOT_STARTED"):
            o = e.reset()
    return kayit, H, W


def tiple(kayit):
    """BISIMULATION: renkleri DAVRANISLARINA gore grupla. Isim yok."""
    tp = BisimTipleyici()
    for (_, _, _, renk, kova, dseviye) in kayit:
        tp.gozle(renk, "tik_etki", kova)
        tp.gozle(renk, "tik_seviye", 1 if dseviye > 0 else 0)
    return tp


def ogren(kayit, tip_sayisi, renkler, tipli=True, dogum_araligi=25,
          pencere=250):
    global TIPLEYICI
    k = Kase()
    k.ek_alfabe = alfabe(tip_sayisi, renkler, tipli)
    n = k.noron("tiklama_degisim")
    n.bagla(Kenar(Terim([]), Tahmin((0,))))     # tek kaba kural: "degismez"
    isabet = []
    for t, (grid, cx, cy, renk, kova, _) in enumerate(kayit):
        k.tik = t
        s = ArcNokta(grid, cx, cy)
        tah, _, _ = n.predict(s, 0)
        isabet.append(1 if tah == (kova,) else 0)
        n.learn(s, 0, (kova,))
        n.tick()
        if t % dogum_araligi == dogum_araligi - 1:
            for e in list(n.kenarlar):
                (k.revize(e) or k.dogur(n, e))
            k.buda()
    return sum(isabet[-pencere:]) / pencere, len(n.kenarlar), k, n


# =====================================================================
if __name__ == "__main__":
    oyunlar = sys.argv[1:] or ["vc33"]
    print("=" * 84)
    print("B — BRAIN <-> ARC-AGI-3 KOPRUSU")
    print("Hedef degisken: 'bu tiklama kareyi degistirir mi?' (olu-hamle atlama)")
    print("=" * 84)
    print(f"  {'oyun':<7}{'renk':>6}{'TIP':>5}{'taban':>8}"
          f"{'ham phi':>10}{'tipli phi':>11}{'kenar':>7}{'  etki dagilimi'}")
    ozet = {}
    for oyun in oyunlar:
        try:
            kayit, H, W = kesif_topla(oyun)
        except Exception as ex:
            print(f"  {oyun:<7}  HATA: {type(ex).__name__}: {str(ex)[:40]}")
            continue
        renkler = sorted({r for (_, _, _, r, _, _) in kayit})
        tp = tiple(kayit)
        globals()["TIPLEYICI"] = tp
        say = Counter(d for (_, _, _, _, d, _) in kayit)
        taban = say.most_common(1)[0][1] / len(kayit)   # cogunluk tahmini
        d_ham, k_ham, _, _ = ogren(kayit, tp.tip_sayisi(), renkler, tipli=False)
        d_tip, k_tip, kk, nn = ogren(kayit, tp.tip_sayisi(), renkler, tipli=True)
        ozet[oyun] = dict(renk=len(renkler), tip=tp.tip_sayisi(),
                          taban=taban, ham=d_ham, tipli=d_tip, kenar=k_tip,
                          gruplar={k: v for k, v in tp.rapor().items()})
        print(f"  {oyun:<7}{len(renkler):>6}{tp.tip_sayisi():>5}{taban:>8.3f}"
              f"{d_ham:>10.3f}{d_tip:>11.3f}{k_tip:>7}  {dict(sorted(say.items()))}")
    if ozet:
        print()
        for oyun, v in ozet.items():
            print(f"  {oyun}: {v['renk']} renk -> {v['tip']} davranis tipi   {v['gruplar']}")
        json.dump(ozet, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "arc_ozet.json"), "w"),
                  indent=1)
