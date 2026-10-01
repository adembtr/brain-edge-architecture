"""
model.py — UZAYSAL DUNYA MODELI. Tek gozlem, bircok tahmin.

Adem: "bir eylem dahi yaparsa bunu SONUCUYLA ogrenmeli ve kaydetmeli.
Ve bunlari kullanarak DIGER EYLEMLERI TAHMIN etmeli."

Onceki adimda (uzaysal.py) uzayi sadece KREDI icin kullandim:
"bu iyi miydi?". Adem'in istedigi daha guclu: TAHMIN.
    denendi   : (token A , eylem 3) -> etki E1
    soruluyor : (token A', eylem 3) -> ?      A' HIC denenmedi
    cevap     : E1     cunku A ~ A'

Iki yonlu genelleme:
  1. NESNE benzerligi : ayni eylem, benzer token -> ayni etki beklenir
                        (token'in yapisi var: renk/boyut/sekil/iliski)
  2. EYLEM benzerligi : ayni token, benzer eylem -> ayni etki beklenir
                        Eylemlerin yapisi YOK (1..7, ne olduklari soylenmiyor),
                        o yuzden eylem vektoru ETKILERINDEN ogrenilir:
                        ayni tokenlarda ayni etkiyi ureten iki eylem benzerdir.
                        (= eylem uzayinda bisimulation, vektor halinde)

Bu, planner'i dogrudan besler: planner artik SADECE denenmis ciftleri
degil, TAHMIN EDILEN ciftleri de kullanabilir.
"""
from collections import Counter, defaultdict
import numpy as np
from vektor import hv, bind, bundle, benzerlik, token_vek


class UzaysalModel:
    """(token, eylem) -> etki.  Denenmemis cift icin BENZERLIKTEN tahmin."""

    def __init__(self, esik_nesne=0.55, esik_eylem=0.30, min_gozlem=1,
                 vek_fn=None):
        self.vek_fn = vek_fn or token_vek
        self.kayit = defaultdict(Counter)      # (tk, a) -> etki sayaci
        self.esik_n, self.esik_e = esik_nesne, esik_eylem
        self.min_gozlem = min_gozlem
        self._tv = {}                          # token vektor onbellek
        self._ev = {}                          # eylem vektor onbellek (bayat olabilir)
        self._bayat = True
        self.tokenlar = []
        self.eylemler = []

    # ---------- kayit ----------
    def gozle(self, tk, eylem, etki):
        """TEK GOZLEM. Bir eylem bile yapilsa sonucuyla kaydedilir."""
        self.kayit[(tk, eylem)][etki] += 1
        if tk not in self._tv:
            self._tv[tk] = self.vek_fn(tk); self.tokenlar.append(tk)
        if eylem not in self.eylemler:
            self.eylemler.append(eylem)
        self._bayat = True

    def tv(self, tk):
        if tk not in self._tv:
            self._tv[tk] = self.vek_fn(tk)
        return self._tv[tk]

    # ---------- eylem vektoru: ETKILERINDEN ogrenilir ----------
    def _eylem_vektorleri(self):
        """
        Eylemin ne oldugu SOYLENMIYOR. O yuzden eylemi ne YAPTIGI tanimlar:
            v(a) = bundle over tk [ bind(token_vek(tk), hv(etki)) ]
        Ayni tokenlarda ayni etkiyi ureten iki eylem -> benzer vektor.
        """
        if not self._bayat:
            return self._ev
        self._ev = {}
        for a in self.eylemler:
            parcalar = []
            for (tk, a2), c in self.kayit.items():
                if a2 != a or not c:
                    continue
                e = c.most_common(1)[0][0]
                parcalar.append(bind(self.tv(tk), hv(("ETKI", e))))
            self._ev[a] = bundle(parcalar) if parcalar else np.zeros_like(self.tv(self.tokenlar[0])) if self.tokenlar else None
        self._bayat = False
        return self._ev

    def eylem_benzerligi(self, a1, a2):
        ev = self._eylem_vektorleri()
        if ev.get(a1) is None or ev.get(a2) is None:
            return 0.0
        return benzerlik(ev[a1], ev[a2])

    # ---------- tahmin ----------
    def tahmin(self, tk, eylem):
        """
        -> (etki, guven, kaynak)
        kaynak: 'kendi' | 'nesne' | 'eylem' | None
        """
        c = self.kayit.get((tk, eylem))
        if c and sum(c.values()) >= self.min_gozlem:
            e, n = c.most_common(1)[0]
            return e, n / sum(c.values()), "kendi"

        # 1) NESNE benzerligi: ayni eylem, benzer token
        oy = Counter(); agirlik = 0.0
        v = self.tv(tk)
        for (tk2, a2), c2 in self.kayit.items():
            if a2 != eylem or tk2 == tk or not c2:
                continue
            b = benzerlik(v, self.tv(tk2))
            if b >= self.esik_n:
                e2 = c2.most_common(1)[0][0]
                oy[e2] += b; agirlik += b
        if oy:
            e, w = oy.most_common(1)[0]
            return e, w / agirlik, "nesne"

        # 2) EYLEM benzerligi: ayni token, benzer eylem
        oy2 = Counter(); ag2 = 0.0
        for (tk2, a2), c2 in self.kayit.items():
            if tk2 != tk or a2 == eylem or not c2:
                continue
            be = self.eylem_benzerligi(eylem, a2)
            if be >= self.esik_e:
                e2 = c2.most_common(1)[0][0]
                oy2[e2] += be; ag2 += be
        if oy2:
            e, w = oy2.most_common(1)[0]
            return e, w / ag2, "eylem"

        return None, 0.0, None

    def kapsama(self, tokenlar, eylemler):
        """Kac (token,eylem) cifti TAHMIN EDILEBILIR? (denenmis + genellenen)"""
        toplam = denenmis = tahmin = 0
        for tk in tokenlar:
            for a in eylemler:
                toplam += 1
                if (tk, a) in self.kayit:
                    denenmis += 1
                elif self.tahmin(tk, a)[0] is not None:
                    tahmin += 1
        return toplam, denenmis, tahmin
