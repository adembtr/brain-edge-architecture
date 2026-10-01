"""
kesif.py — "DOGRU" diye bir sey yok. Sadece ETKI var.

Adem'in itirazi (kayda gecsin):
    "Bir seyin dogru oldugunu nereden biliyorsun? ARC-AGI'de dogru olani
     kimse bilmiyor. Sistem kendi mantigini kurmali. Eylem yapmali, eylem
     seviye geciriyorsa 'bu iyi' demeli. BIR BLOGU HAREKET ETTIRMEK ILE
     SEVIYE GECMEK AYNI SEY OLMALI. Amaci hep yeni eylemler kesfetmek."

Bu dosya tam olarak bunu yapar. Onceki olcumlerden farki:

  ONCE (yanlis amac)          SIMDI (Adem'in amaci)
  --------------------        ---------------------
  amac: tahmin dogrulugu      amac: YENI ETKI kesfetmek
  odul: yok (ama dogruluk     odul: yok, ve GEREKMIYOR --
        gizli bir amac gibi         degerin kaynagi YENILIK
        davraniyordu)
  seviye = ozel durum         seviye = SADECE BASKA BIR ETKI
                                      (ozel kod YOK)

Tek para birimi: ETKI IMZASI. Blok kaymasi da seviye atlamasi da ayni
turden olay; ikincisi sadece daha nadir ve daha buyuk. Hicbir yerde
"seviye" degiskenine ayricalik taninmiyor.

q artik "tahminim dogru mu" degil: "BURAYA BASMAK YENI BIR SEY GETIRIYOR MU".
N hala ayni isi yapiyor: bir fikri tuketince sirayi baskasina ver.
"""
import os, sys, random, json
from collections import Counter, defaultdict

AGI = os.environ.get("AGI_DIR", os.path.abspath(os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "..", "arc-agi3-agent")))
os.environ.setdefault("OPERATION_MODE", "offline")
os.environ.setdefault("ENVIRONMENTS_DIR", f"{AGI}/environment_files")
os.environ.setdefault("MPLBACKEND", "agg")
sys.path.insert(0, f"{AGI}/denme"); sys.path.insert(0, f"{AGI}/denme/infra")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from uzay import BisimTipleyici       # noqa: E402


# =====================================================================
def etki_imzasi(onceki, sonraki, tipleyici):
    """
    Iki kare arasindaki farkin OYUN-NOTR imzasi.
    Etiket yok, "seviye" yok, "kazanma" yok. Sadece geometri + tip.
    """
    deg = [(y, x) for y in range(len(onceki)) for x in range(len(onceki[0]))
           if onceki[y][x] != sonraki[y][x]]
    if not deg:
        return ("yok",)
    n = len(deg)
    kova = 1 if n <= 4 else (2 if n <= 30 else 3)
    giden = frozenset(tipleyici.tip_of(onceki[y][x]) for (y, x) in deg)
    gelen = frozenset(tipleyici.tip_of(sonraki[y][x]) for (y, x) in deg)
    ys = [y for (y, _) in deg]; xs = [x for (_, x) in deg]
    yayilim = 0 if (max(ys)-min(ys) <= 2 and max(xs)-min(xs) <= 2) else 1
    return ("deg", kova, giden, gelen, yayilim)


def baglam_imzasi(grid, cx, cy, tipleyici, r=1):
    """Tiklanan noktanin YEREL baglami. phi'nin somut hali."""
    im = []
    for dy in range(-r, r+1):
        for dx in range(-r, r+1):
            y, x = cy+dy, cx+dx
            v = grid[y][x] if (0 <= y < len(grid) and 0 <= x < len(grid[0])) else -1
            im.append(tipleyici.tip_of(v))
    return tuple(im)


# =====================================================================
class KesifAjani:
    """
    Kenar = (baglam -> beklenen etki), + q (yenilik degeri) + N (butce).
    DOGRULUK HESAPLANMIYOR. Tek olcut: yeni etki geldi mi.
    """

    def __init__(self, tipleyici, Nmax=4.0, tau=4.0, alpha=0.30):
        self.tp = tipleyici
        self.Nmax, self.tau, self.alpha = Nmax, tau, alpha
        self.q = defaultdict(lambda: 0.6)     # baglam -> yenilik degeri
        self.N = defaultdict(lambda: Nmax)    # baglam -> butce
        self.beklenti = {}                    # baglam -> gorulen etkiler
        self.gorulen_etkiler = set()          # TUM sistemde gorulen etkiler
        self.yeni_etki_anlari = []

    def q_eff(self, b):
        return self.q[b] * (self.N[b] / self.Nmax)

    def sec(self, adaylar):
        """adaylar: {baglam: [(cx,cy), ...]}  -> en yuksek q_eff'li baglam."""
        b = max(adaylar, key=self.q_eff)
        return b, random.choice(adaylar[b])

    def ogren(self, b, etki, t):
        # YENILIK: bu etki sistemde hic gorulmedi mi? bu baglamda?
        kure_yeni = etki not in self.gorulen_etkiler
        baglam_yeni = etki not in self.beklenti.setdefault(b, set())
        yenilik = 1.0 if kure_yeni else (0.5 if baglam_yeni else 0.0)
        if etki == ("yok",):
            yenilik = 0.0                     # hicbir sey olmadi
        if kure_yeni:
            self.yeni_etki_anlari.append((t, etki))
        self.gorulen_etkiler.add(etki)
        self.beklenti[b].add(etki)
        self.q[b] = min(1.0, max(0.0, self.q[b] + self.alpha*(yenilik - self.q[b])))
        return yenilik

    def harca(self, b):
        self.N[b] = max(0.0, self.N[b] - 1.0)

    def tik(self, baglamlar):
        for b in baglamlar:
            self.N[b] += (self.Nmax - self.N[b]) / self.tau


# =====================================================================
def kosu(oyun, butce=800, mod="kesif", tohum=0, aday_sayisi=160, Nmax=4.0, tau=4.0):
    from env import Env
    rnd = random.Random(tohum)
    e = Env(oyun); o = e.reset()
    H, W = len(o["grid"]), len(o["grid"][0])

    # 1) kisa isinma: tipleri kesfet (etiketsiz)
    tp = BisimTipleyici()
    for _ in range(120):
        cx, cy = rnd.randrange(W), rnd.randrange(H)
        onc = o["grid"]; renk = onc[cy][cx]
        o2 = e.step("click", 6, cx, cy)
        im = etki_imzasi(onc, o2["grid"], BisimTipleyici())
        tp.gozle(renk, "etki", im[1] if im[0] == "deg" else 0)
        o = o2
        if o["state"] not in ("NOT_FINISHED", "NOT_STARTED"):
            o = e.reset()

    aj = KesifAjani(tp, Nmax=Nmax, tau=tau)
    o = e.reset()
    en_seviye = o["level"]; seviye_anlari = []
    for t in range(butce):
        grid = o["grid"]
        hucreler = [(rnd.randrange(W), rnd.randrange(H)) for _ in range(aday_sayisi)]
        if mod == "rastgele":
            cx, cy = rnd.choice(hucreler); b = None
        else:
            adaylar = defaultdict(list)
            for (cx0, cy0) in hucreler:
                adaylar[baglam_imzasi(grid, cx0, cy0, tp)].append((cx0, cy0))
            b, (cx, cy) = aj.sec(adaylar)
            aj.harca(b)
            aj.tik(list(adaylar.keys()))
        o2 = e.step("click", 6, cx, cy)
        if mod != "rastgele":
            aj.ogren(b, etki_imzasi(grid, o2["grid"], tp), t)
        if o2["level"] > en_seviye:
            en_seviye = o2["level"]; seviye_anlari.append(t)
        o = o2
        if o["state"] not in ("NOT_FINISHED", "NOT_STARTED"):
            o = e.reset()
    return dict(seviye=en_seviye, seviye_anlari=seviye_anlari,
                etki=len(aj.gorulen_etkiler) if mod != "rastgele" else None,
                baglam=len(aj.q) if mod != "rastgele" else None)


if __name__ == "__main__":
    oyunlar = sys.argv[1:] or ["vc33", "cd82", "r11l", "tn36"]
    print("=" * 86)
    print("KESIF AJANI — 'dogru' yok, sadece ETKI var")
    print("Seviye atlamak ozel bir sey DEGIL; sadece nadir bir etki imzasi.")
    print("Butce: 800 tiklama/oyun, 2 tohum. Kiyas: rastgele tiklama.")
    print("=" * 86)
    print(f"  {'oyun':<7}{'RASTGELE sv':>13}{'KESIF sv':>11}"
          f"{'etki tipi':>11}{'baglam':>9}{'ilk seviye @':>14}")
    ozet = {}
    for oyun in oyunlar:
        try:
            rs = [kosu(oyun, mod="rastgele", tohum=s)["seviye"] for s in (0, 1)]
            ks = [kosu(oyun, mod="kesif", tohum=s) for s in (0, 1)]
        except Exception as ex:
            print(f"  {oyun:<7}  HATA: {type(ex).__name__}: {str(ex)[:45]}")
            continue
        sv = max(k["seviye"] for k in ks)
        ilk = min([k["seviye_anlari"][0] for k in ks if k["seviye_anlari"]] or [-1])
        ozet[oyun] = dict(rastgele=max(rs), kesif=sv,
                          etki=max(k["etki"] for k in ks),
                          baglam=max(k["baglam"] for k in ks), ilk=ilk)
        print(f"  {oyun:<7}{max(rs):>13}{sv:>11}"
              f"{max(k['etki'] for k in ks):>11}{max(k['baglam'] for k in ks):>9}"
              f"{(str(ilk) if ilk >= 0 else '-'):>14}")
    json.dump(ozet, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "kesif_ozet.json"), "w"), indent=1)
