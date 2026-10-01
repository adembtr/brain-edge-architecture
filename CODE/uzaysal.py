"""
uzaysal.py — UZAYI BAGLAMA katmani. Tam esitligin yerine BENZERLIK.

OLCULEN DARBOGAZ (BULGULAR §8, §16):
Kredi ve cukur girisi (tur, token, eylem) ile TAM ESITLIKTE saklaniyordu.
Bir token'da ogrenilen sey, tek alani farkli token'a HIC gecmiyordu.
Alfabe inceliginin bu kadar kritik olmasinin sebebi buydu:
    107 token -> 0 seviye     28 token -> seviye geliyor

Bu dosya arada durur: ayni arayuz, ama okuma BENZERLIK agirlikli.
    tam esitlik : kredi[(tur, tk, a)]
    uzaysal     : kredi[(tur, tk, a)]  +  SUM_k' benz(tk,k') * kredi[(tur,k',a)]

Mimariyi bozmaz: q/p/N fizigi ayni, sadece ANAHTAR ESLESMESI dereceli oldu.
"""
import numpy as np
from vektor import token_vek, benzerlik, sahne_vek, bundle


class UzaysalKredi:
    """
    Kredi deposu. Yazma tam anahtara, OKUMA benzerlik agirlikli.

    esik : bu benzerligin altindaki kayitlar hic katilmaz (gurultu olmasin)
    beta : kendi kaydina karsi komsularin agirligi
    """

    def __init__(self, varsayilan=0.5, esik=0.55, beta=0.6, vek_fn=None):
        # vek_fn: anahtari vektore ceviren fonksiyon. Varsayilan token_vek;
        # BAGLAMLI kimlik kullanilacaksa disaridan verilir.
        self.vek_fn = vek_fn or token_vek
        self.bellek = {}          # (tur, tk, eylem) -> kredi
        self.varsayilan = varsayilan
        self.esik, self.beta = esik, beta
        self._vek = {}            # tk -> vektor onbellek
        self._indeks = {}         # (tur, eylem) -> [tk, ...]

    def vek(self, tk):
        if tk not in self._vek:
            self._vek[tk] = self.vek_fn(tk)
        return self._vek[tk]

    def oku(self, tur, tk, eylem):
        anahtar = (tur, tk, eylem)
        kendi = self.bellek.get(anahtar)
        komsular = []
        for k2 in self._indeks.get((tur, eylem), ()):
            if k2 == tk:
                continue
            b = benzerlik(self.vek(tk), self.vek(k2))
            if b >= self.esik:
                komsular.append((b, self.bellek[(tur, k2, eylem)]))
        if kendi is None and not komsular:
            return self.varsayilan
        if not komsular:
            return kendi
        agirlik = sum(b for b, _ in komsular)
        komsu_ort = sum(b * v for b, v in komsular) / agirlik
        if kendi is None:
            # HIC DENENMEMIS token: benzerlerinden TAHMIN et  <-- asil kazanc
            return komsu_ort
        return (1 - self.beta) * kendi + self.beta * komsu_ort

    def yaz(self, tur, tk, eylem, iyi, hiz=0.25, ceza=0.15):
        anahtar = (tur, tk, eylem)
        v = self.bellek.get(anahtar, self.varsayilan)
        v = min(1.0, max(0.0, v + hiz * (1.0 if iyi else -ceza)))
        self.bellek[anahtar] = v
        self._indeks.setdefault((tur, eylem), [])
        if tk not in self._indeks[(tur, eylem)]:
            self._indeks[(tur, eylem)].append(tk)

    def __len__(self):
        return len(self.bellek)


def sahne_benzerligi(tokenlar_a, tokenlar_b):
    """Iki sahne ne kadar benzer. Cukur girisi icin."""
    if not tokenlar_a or not tokenlar_b:
        return 0.0
    return benzerlik(sahne_vek(list(tokenlar_a)), sahne_vek(list(tokenlar_b)))


def giris_uygun(giris_tokenlar, sahne_tokenlar, esik=0.35):
    """
    Cukur girisi: TAM ALT KUME degil, her giris token'inin sahnede
    yeterince BENZER bir karsiligi olmasi yeter.
    """
    if not giris_tokenlar:
        return True
    if not sahne_tokenlar:
        return False
    sv = [token_vek(t) for t in sahne_tokenlar]
    for g in giris_tokenlar:
        gv = token_vek(g)
        if max(benzerlik(gv, s) for s in sv) < esik:
            return False
    return True
