"""
vektor.py — UZAY. Nesneler, eylemler ve diziler VEKTOR olur.

Adem: "bir uzay olusturmamiz gerek, noronlar gibi; girdiginde uzay icine
girip sonra cikacak. Anlamli uzaylari birlestirince ANLAM cikacak.
Ve uzay en iyi vektorler/matrisler ile temsil edilir."

NEDEN GEREKLI (olculmus sorun):
Su an token eslesmesi TAM ESITLIK. Iki nesne tek alanda bile farkliysa
TAMAMEN ilgisiz sayiliyor. Bu yuzden alfabe inceligi kritik oldu:
    107 token -> 0 seviye     28 token -> seviye geliyor   (BULGULAR §8)
Vektorde benzerlik DERECELI: 7 alandan 5'i tutan iki token yakin kalir.

BAGLANTI (DEVIR.md §4): "populasyon geometrisi -- N noronun aktivite
vektoru; ayni nesnenin farkli gorunumleri bir MANIFOLD olusturur
(Chung & Abbott 2104.07059)". Bu dosya onun somut hali.

ISLEMLER (VSA / bipolar MAP):
    bind(a,b)   = a * b        BAGLA   ("rol = deger")   kendi tersi
    bundle(...)  = sign(sum)    TOPLA   ("hepsi bir arada")
    benzerlik    = cosine
Bind benzerligi YOK EDER (yeni sey uretir), bundle benzerligi KORUR
(uyelik saklar). Anlam bu ikisinin birlesiminden cikiyor.
"""
import numpy as np

BOYUT = 2048
_RNG = np.random.default_rng(12345)
_SOZLUK = {}


def hv(anahtar):
    """Bir sembolun hipervektoru. Ayni anahtar -> ayni vektor (kalici)."""
    if anahtar not in _SOZLUK:
        _SOZLUK[anahtar] = _RNG.choice(np.array([-1.0, 1.0]), size=BOYUT)
    return _SOZLUK[anahtar]


def bind(*vs):
    """BAGLA. Sonuc girdilerin HICBIRINE benzemez -> yeni sembol uretir."""
    out = vs[0].copy()
    for v in vs[1:]:
        out = out * v
    return out


def bundle(vs):
    """
    TOPLA. Sonuc her uyeye BENZER -> kume/uyelik saklar.

    OLCULEN HATA (K20): sonuc sign() ile ikililestiriliyordu. Iki vektor
    toplanirken celisen konumlarda toplam 0 oluyor; oralara ne konursa
    konsun FARKLI bundle'lar ayni deseni paylasiyor. Sonuc: ilgisiz iki
    baglam 0.55 benzerlik gosterdi (0 olmasi gerekirken).
    Sebep: a=B*y0, b=C*y4, c=C*y0, d=B*y4 icin a*b == c*d, yani
    celiski KONUMLARI ayni -> beraberlik cozumu ne olursa olsun ortak.

    Cozum: IKILILESTIRME. Gercek degerli toplam tut; kosinus zaten
    dogru calisiyor ve beraberlik yozlasmasi ortadan kalkiyor.
    """
    if not len(vs):
        return np.zeros(BOYUT)
    s = np.sum(np.asarray(vs, dtype=float), axis=0)
    n = np.linalg.norm(s)
    return s / n if n > 0 else s


def benzerlik(a, b):
    na, nb = np.linalg.norm(a), np.linalg.norm(b)
    if na == 0 or nb == 0:
        return 0.0
    return float(np.dot(a, b) / (na * nb))


def kaydir(v, n=1):
    """Permutasyon: SIRA kodlar. Dizide 1. mi 2. mi oldugunu ayirir."""
    return np.roll(v, n)


# =====================================================================
# TOKEN -> VEKTOR   (nesnenin uzaydaki yeri)
# =====================================================================
ALANLAR = ("renk", "genislik", "uzunluk", "alan", "kare", "sekil", "simetri",
           "icinde", "degiyor", "esi_var", "yalniz")


def token_vek(tk):
    """
    Nesne token'i (tuple) -> hipervektor.
      v = bundle_i [ bind(ROL_i, DEGER_i) ]
    Ayni alan-deger cifti -> ayni katki. 5/7 alan tutuyorsa vektorler yakin.
    "Ayni parcalar farkli nesnelerde kullanilir" -- bu, o.
    """
    parcalar = []
    for i, deger in enumerate(tk):
        alan = ALANLAR[i] if i < len(ALANLAR) else f"alan{i}"
        parcalar.append(bind(hv(("ROL", alan)), hv(("DEG", alan, deger))))
    return bundle(parcalar)


def sorgula(v, alan, adaylar):
    """
    UZAYA GIRIP CIKMA. "Bu vektorde `alan` ne?" diye sorar.
    unbind: v * ROL  ->  DEGER'e yakin cikar. Adaylar arasindan en yakini.
    """
    tahmin = bind(v, hv(("ROL", alan)))
    return max(adaylar, key=lambda d: benzerlik(tahmin, hv(("DEG", alan, d))))


# =====================================================================
# EYLEM ve DIZI -> VEKTOR   (cukurun uzaydaki hali)
# =====================================================================
def adim_vek(tk, eylem):
    """Tek adim = (nesne, eylem) baglanmis."""
    return bind(token_vek(tk), hv(("EYLEM", eylem)))


def dizi_vek(adimlar):
    """
    Eylem dizisi (= cukur govdesi) tek vektore. Sira permutasyonla kodlanir,
    yoksa [A,B] ile [B,A] ayni cikardi.
    """
    return bundle([kaydir(adim_vek(tk, a), i) for i, (tk, a) in enumerate(adimlar)])


def sahne_vek(tokenlar):
    """Sahne = icindeki nesnelerin toplami. Uyelik sorgulanabilir."""
    return bundle([token_vek(t) for t in tokenlar])


def icinde_mi(sahne_v, tk, esik=0.35):
    """
    Bu nesne sahnede var mi? TAM ESITLIK degil, BENZERLIK.

    Esik OLCUMLE belirlendi (3 uyeli sahne):
        uyeler        0.49 - 0.87
        uye olmayan   0.26   (o da alan paylastigi icin, tamamen ilgisiz degil)
    Eski esik 0.15 fazla gevsekti; 0.35 temiz ayiriyor.
    """
    return benzerlik(sahne_v, token_vek(tk)) > esik
