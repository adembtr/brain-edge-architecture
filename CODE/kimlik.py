"""
kimlik.py — BAGLAMLI KIMLIK anahtar olarak.

Su ana kadar aday anahtari = (token, eylem). Token nesneyi TEK BASINA
anlatiyordu. Adem: "baglam kurmali, etraftaki nesneler ile ne oldugunu
anlamali."

Artik anahtar = (token, BAGLAM_KODU, eylem).
    baglam_kodu : en yakin K komsunun (renk, yon, uzaklik) ozeti  -- hashlenebilir
    kimlik_vek  : bind(token_vek, baglam_vek)                     -- benzerlik icin

Boylece:
  - ayni sekil + farkli cevre  -> FARKLI aday (dogru ayrim)
  - benzer cevre               -> kredi/tahmin TRANSFER olur (uzay sayesinde)
"""
import math
from vektor import bind, token_vek, hv
from baglam import komsular, baglam_vek, _yon, _uzak


def _kaba_yon(yn, dilim=8, hedef=4):
    """8 yonu 4'e indir: baglam kodu cok ince olmasin."""
    if yn == "ayni":
        return yn
    return f"k{int(yn[1:]) * hedef // dilim}"


def baglam_kodu(merkez_tk, merkez_xy, hepsi, K=1, kaba=True):
    """
    Hashlenebilir baglam ozeti.

    OLCULEN HATA: K=3 komsu + 8 yon + uzaklik ile lp85'te 255 farkli KIMLIK
    olustu (duz token ~17 idi). 15 kat buyume -> 800 adimda hicbiri
    doldurulamadi, genelleme olmadi, seviye 2 -> 1 dustu.
    Bu, BULGULAR §8'deki dersin ayni-si, bir ust seviyede:
    ALFABE FAZLA INCE OLURSA HICBIR KURAL GENELLEMEZ.

    Kabalastirma: 1 komsu, 4 yon, uzaklik YOK.
    """
    kms = komsular((merkez_tk, merkez_xy), hepsi, K)
    if kaba:
        return tuple((tk[0], _kaba_yon(yn)) for (tk, yn, uz) in kms)
    return tuple((tk[0], yn, uz) for (tk, yn, uz) in kms)


def kimlik_vek(anahtar):
    """
    anahtar = (token, baglam_kodu)
    kimlik  = bind(token_vek, baglam_vek)
    Ayni token + farkli baglam -> farkli vektor; benzer baglam -> yakin.
    """
    tk, bk = anahtar
    if not bk:
        return bind(token_vek(tk), hv(("BAGLAM", "bos")))
    from vektor import bundle
    bv = bundle([bind(hv(("RENK", p[0])), hv(("YON", p[1])))
                 for p in bk])
    return bind(token_vek(tk), bv)
