"""
baglam.py — BAGLAM. "Bu nesne NE?" sorusunun cevabi kendinde degil, ETRAFINDA.

Adem: "arada bir beyin mantik yok, yani BAGLAM yok. Bagam kurmali,
etraftaki nesneler ile ne oldugunu anlamali."

Hakli. Su ana kadar token nesneyi TEK BASINA anlatiyordu (renk, boyut,
sekil, simetri) + 4 kaba iliski. Ama Adem'in oyun notlarinin tamami baglam:
    ft09: "ORTADAKI kare ETRAFTAKI karelerin SABLONUNU temsil ediyor"
    m0r0: "mavi 10'lar SIYAH 5 YOLUNU KULLANARAK tasinacak"
Ortadaki karenin anlami kendinden degil, cevresiyle iliskisinden geliyor.
Ayni kare baska yerde baska sey demek.

IKI TUR BAGLAM:

  1. GEOMETRIK  — kim etrafimda, hangi yonde, ne kadar uzakta.
                  Ilk kareden okunur, EYLEM GEREKMEZ.
                  baglam = bundle_k [ bind(token_vek(k), YON_k, UZAKLIK_k) ]
                  kimlik  = bind(kendi_token, baglam)
                  -> Ayni sekil + farkli cevre = FARKLI kimlik.

  2. NEDENSEL   — neye dokununca ne degisiyor. EYLEMDEN ogrenilir.
                  A'ya basinca B degisiyorsa A ile B nedensel bagli.
                  Bu, geometrik yakinliktan BAGIMSIZ bag kurar
                  (uzaktaki sayac, kapi-anahtar, vs.)

Ikisi birlikte "bu nesne ne" sorusunu cevaplar.
"""
import math
from collections import defaultdict, Counter
from vektor import hv, bind, bundle, benzerlik, token_vek


# =====================================================================
# 1. GEOMETRIK BAGLAM
# =====================================================================
def _yon(dx, dy, dilim=8):
    """Bagil yonu `dilim` parcaya bol. Yon bir SEMBOL olur."""
    if dx == 0 and dy == 0:
        return "ayni"
    a = math.atan2(dy, dx)
    k = int(round(a / (2 * math.pi / dilim))) % dilim
    return f"y{k}"


def _uzak(d, kesim=(3, 8, 20, 50)):
    for i, k in enumerate(kesim):
        if d <= k:
            return i
    return len(kesim)


def komsular(merkez, hepsi, en_fazla=6):
    """En yakin `en_fazla` nesne, (token, yon, uzaklik) olarak."""
    mx, my = merkez[1]
    out = []
    for (tk, (x, y)) in hepsi:
        if (x, y) == (mx, my):
            continue
        d = math.hypot(x - mx, y - my)
        out.append((d, tk, _yon(x - mx, y - my), _uzak(d)))
    out.sort(key=lambda z: z[0])
    return [(tk, yn, uz) for (_, tk, yn, uz) in out[:en_fazla]]


def baglam_vek(kms):
    """
    Cevrenin vektoru. Her komsu KENDI YONUNE ve UZAKLIGINA baglanir,
    yoksa "solumda duvar" ile "sagimda duvar" ayni cikardi.
    """
    if not kms:
        return hv(("BAGLAM", "bos"))
    return bundle([bind(token_vek(tk), hv(("YON", yn)), hv(("UZAK", uz)))
                   for (tk, yn, uz) in kms])


def baglamli_kimlik(tk, kms):
    """
    NESNENIN BAGLAMLI KIMLIGI = kendi_token BAGLANMIS cevre.
    Ayni sekil + ayni renk ama FARKLI cevre -> FARKLI kimlik.
    """
    return bind(token_vek(tk), baglam_vek(kms))


def sahne_nesneleri(obs, token_fn):
    """[(token, (cx,cy)), ...]"""
    out = []
    for ob in obs:
        cy, cx = ob.centroid
        out.append((token_fn(ob), (float(cx), float(cy))))
    return out


def baglamli_kimlikler(obs, token_fn, en_fazla=6):
    """Her nesne icin (token, baglamli_kimlik_vektoru)."""
    nes = sahne_nesneleri(obs, token_fn)
    out = []
    for i, (tk, xy) in enumerate(nes):
        kms = komsular((tk, xy), nes, en_fazla)
        out.append((tk, baglamli_kimlik(tk, kms), kms))
    return out


# =====================================================================
# 2. NEDENSEL BAGLAM
# =====================================================================
class NedenselBaglam:
    """
    "A'ya dokununca B degisiyor" -> A ile B BAGLI.
    Geometrik yakinliktan BAGIMSIZ: uzaktaki sayac, kapi-anahtar, vs.
    """

    def __init__(self):
        self.bag = defaultdict(Counter)     # etkilenen_token -> degisen_token sayaci
        self.toplam = Counter()

    def gozle(self, etkilenen_tk, degisen_tokenlar):
        self.toplam[etkilenen_tk] += 1
        for d in degisen_tokenlar:
            self.bag[etkilenen_tk][d] += 1

    def guc(self, a_tk, b_tk):
        """A'ya dokununca B'nin degisme orani."""
        n = self.toplam.get(a_tk, 0)
        return (self.bag[a_tk][b_tk] / n) if n else 0.0

    def etkiledikleri(self, a_tk, esik=0.5, en_az=2):
        n = self.toplam.get(a_tk, 0)
        if n < en_az:
            return []
        return [b for b, c in self.bag[a_tk].items() if c / n >= esik]

    def uzaktan_mi(self, a_tk, b_tk, kms):
        """A ile B nedensel bagli ama GEOMETRIK komsu degil mi?"""
        if self.guc(a_tk, b_tk) < 0.5:
            return False
        return b_tk not in {tk for (tk, _, _) in kms}

    def nedensel_vek(self, a_tk):
        """A'nin nedensel imzasi: neleri etkiliyor."""
        et = self.etkiledikleri(a_tk)
        if not et:
            return hv(("NEDEN", "bos"))
        return bundle([token_vek(b) for b in et])
