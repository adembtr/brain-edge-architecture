"""
neuron.py — Noron katmani.

DEVIR.md 5.1: "Noron kurmak = bir hedef degisken secmek. Ona bakan butun
kenarlar otomatik olarak onun girdisi olur. Noron ayrica tanimlanmaz,
ORTAYA CIKAR."

DEVIR.md acik soru 1: "Noron seviyesinde birlestirme kurali ne? Testlerde
max(q_eff) kullanildi -- muhtemelen fazla basit. Yerini alacak seyi OLCUM
gostersin, tahmin degil."

Bu dosya o olcumu mumkun kilar: 5 birlestirme kurali, ayni veri, ayni kenar
havuzu, tek fark kural. Kazanani sayilar soyler.

edge.py'ye DOKUNULMADI. EdgeP onu miras alir, p'yi EKLER.
"""

from edge import Edge, _clip
import dunya


# =====================================================================
# EdgeP — Edge + p (guvenilirlik) + ozgulluk
# =====================================================================
class EdgeP(Edge):
    """
    p neden eklendi (gerekce KAYDA GECSIN):

    OLCUM 3 (bu oturumda yapildi): q tavana vuruyor. 5 basari da 5000 basari
    da q=1.00 veriyor; tek hatadan sonra ikisi de q=0.70'e dusuyor. Yani
    sistemin bir kuralin NE KADAR KOKLU oldugu hakkinda hicbir bilgisi yok.

    Literatur ayni yeri gosteriyor: Wilson 1995 (XCS). Holland'in klasor
    sistemlerinde uygunluk GUCTEN (=q) geliyordu ve 20 yil asiri-genelleme
    ile coktu. Wilson uygunlugu TAHMININ ISABETINDEN (=p) alinca calisti.

    Yani "olculmus bir basarisizlik talep etmeden ekleme" disiplinine
    uygun: basarisizlik olculdu, p artik istege bagli degil.
    """

    __slots__ = ("p", "eta", "ozgulluk")

    def __init__(self, phi, psi, name="", q=0.5, Nmax=4.0, alpha=0.30,
                 tau=3.0, beta=1.0, p=0.5, eta=0.15, ozgulluk=1):
        super().__init__(phi, psi, name, q, Nmax, alpha, tau, beta)
        self.p = p                  # gecmiste tutma orani   ORTA hiz
        self.eta = eta              # p ogrenme hizi
        self.ozgulluk = ozgulluk    # phi'deki yuklem sayisi (MDL maliyeti)

    def learn(self, err):
        super().learn(err)
        isabet = 1.0 if err < 0.5 else 0.0
        self.p = _clip(self.p + self.eta * (isabet - self.p), 0.0, 1.0)

    def specialize(self, extra_phi, name="", ozgulluk_artis=1):
        old = self.phi
        return EdgeP(lambda s, a: old(s, a) and extra_phi(s, a),
                     self.psi, name or (self.name + "+"), q=self.q,
                     Nmax=self.Nmax, alpha=self.alpha, tau=self.tau,
                     beta=self.beta, p=self.p, eta=self.eta,
                     ozgulluk=self.ozgulluk + ozgulluk_artis)

    def __repr__(self):
        return (f"<{self.name} q={self.q:.2f} p={self.p:.2f} "
                f"N={self.N:.2f} oz={self.ozgulluk} {self.hits}/{self.uses}>")


# =====================================================================
# Birlestirme kurallari — noronun nonlineerligi
# =====================================================================
def _oy_topla(aktifler, agirlik):
    """Ayni degeri tahmin eden kenarlar oylarini birlestirir."""
    kutu = {}
    for e in aktifler:
        v = e.psi(None, None) if e.phi.__code__.co_argcount == 0 else None
        kutu[v] = kutu.get(v, 0.0) + agirlik(e)
    return kutu


def kural_max_qeff(aktifler, s, a):
    """MEVCUT KURAL. Kazanan hepsini alir. q_eff en yuksek olan konusur."""
    w = max(aktifler, key=lambda e: e.q_eff())
    return w.predict(s, a), w.q_eff(), [w]


def kural_agirlikli_oy(aktifler, s, a):
    """Ayni tahmini yapanlar q_eff'lerini toplar. Demokrasi."""
    kutu, kaynak = {}, {}
    for e in aktifler:
        v = e.predict(s, a)
        kutu[v] = kutu.get(v, 0.0) + e.q_eff()
        kaynak.setdefault(v, []).append(e)
    v = max(kutu, key=kutu.get)
    toplam = sum(kutu.values()) or 1.0
    return v, kutu[v] / toplam, kaynak[v]


def kural_isabet_oy(aktifler, s, a):
    """XCS. Agirlik q_eff degil, q_eff*p. Guc degil ISABET oy verir."""
    kutu, kaynak = {}, {}
    for e in aktifler:
        v = e.predict(s, a)
        w = e.q_eff() * getattr(e, "p", 1.0)
        kutu[v] = kutu.get(v, 0.0) + w
        kaynak.setdefault(v, []).append(e)
    v = max(kutu, key=kutu.get)
    toplam = sum(kutu.values()) or 1.0
    return v, kutu[v] / toplam, kaynak[v]


def kural_en_ozel(aktifler, s, a):
    """
    MDL / uretim sistemi sirasi: en OZEL eslesen kural konusur.
    "Kus ucar" ile "penguen ucmaz" carpisirsa penguen kazanir.
    Esitlikte q_eff.
    """
    w = max(aktifler, key=lambda e: (e.ozgulluk, e.q_eff()))
    return w.predict(s, a), w.q_eff(), [w]


def kural_ozel_isabet(aktifler, s, a):
    """En ozel + isabetli. Ozgulluk once, sonra q_eff*p."""
    w = max(aktifler, key=lambda e: (e.ozgulluk,
                                     e.q_eff() * getattr(e, "p", 1.0)))
    return w.predict(s, a), w.q_eff() * getattr(w, "p", 1.0), [w]


KURALLAR = {
    "max_qeff":      kural_max_qeff,      # DEVIR.md'nin mevcut kurali
    "agirlikli_oy":  kural_agirlikli_oy,
    "isabet_oy":     kural_isabet_oy,     # XCS
    "en_ozel":       kural_en_ozel,       # MDL
    "ozel_isabet":   kural_ozel_isabet,
}


# =====================================================================
# Noron
# =====================================================================
class Neuron:
    """
    Bir hedef degisken. Kenarlar ONA BAKTIGI icin girdisi olur.
    Noron kenarlari "icermez", sadece ayni hedefi tahmin edenleri toplar.
    """

    def __init__(self, hedef_adi, kurall="max_qeff", q_min=0.05):
        self.hedef = hedef_adi
        self.kural_adi = kurall
        self.kural = KURALLAR[kurall]
        self.kenarlar = []
        self.q_min = q_min
        self.gecmis_kenar_sayisi = []

    def bagla(self, e):
        self.kenarlar.append(e)

    def aktifler(self, s, a):
        return [e for e in self.kenarlar if e.active(s, a)]

    def predict(self, s, a):
        """-> (tahmin, guven, kaynak_kenarlar). Aktif kenar yoksa (None,0,[])."""
        akt = self.aktifler(s, a)
        if not akt:
            return None, 0.0, []
        return self.kural(akt, s, a)

    def learn(self, s, a, gozlenen):
        """LOKAL. Sadece phi'si eslesenler ogrenir. Backprop yok."""
        for e in self.aktifler(s, a):
            err = 0.0 if e.predict(s, a) == gozlenen else 1.0
            e.learn(err)

    def tick(self):
        for e in self.kenarlar:
            e.tick()

    def buda(self):
        onceki = len(self.kenarlar)
        self.kenarlar = [e for e in self.kenarlar if not e.dead(self.q_min)]
        self.gecmis_kenar_sayisi.append(len(self.kenarlar))
        return onceki - len(self.kenarlar)


# =====================================================================
# Yuklem havuzu — phi'nin kelime dagarcigi
# =====================================================================
# ONEMLI: bunlar ELLE verilmis yuklemlerdir. Sistem bunlari URETMIYOR.
# Uretim problemi (hipotez uretimi) kasitli olarak BURADA COZULMEDI.
# Bu havuz, Adem'in AGI/predicates.py'sindeki 192 yuklemin minik hali.
# Hicbirinde "duvar"/"kutu" ANLAMI yok; sadece geometri ve sayi esitligi.

def yuklem_havuzu():
    y = []
    for k in dunya.EYLEMLER:
        y.append((f"eylem={k}", (lambda k: lambda s, a: a == k)(k)))

    def hedef_deger(s, a):
        dx, dy = dunya.DELTA[a]
        return dunya.deger(s, s.ax + dx, s.ay + dy)

    def otesi_deger(s, a):
        dx, dy = dunya.DELTA[a]
        return dunya.deger(s, s.ax + 2 * dx, s.ay + 2 * dy)

    for v in range(4):
        y.append((f"hedef_deger={v}", (lambda v: lambda s, a: hedef_deger(s, a) == v)(v)))
    for v in range(4):
        y.append((f"otesi_deger={v}", (lambda v: lambda s, a: otesi_deger(s, a) == v)(v)))
    return y


def kenar_havuzu(derinlik=2, Nmax=4.0, tau=3.0, alpha=0.30):
    """
    phi = havuzdan <=derinlik yuklemin VE'si.  psi = 5 yer degisiminden biri.
    Kenar sayisi = |phi uzayi| x |psi uzayi|.  <-- phi patlamasinin olculdugu yer
    """
    yuk = yuklem_havuzu()
    phis = [("her_zaman", lambda s, a: True, 0)]
    for i, (n1, f1) in enumerate(yuk):
        phis.append((n1, f1, 1))
    if derinlik >= 2:
        for i in range(len(yuk)):
            for j in range(i + 1, len(yuk)):
                n1, f1 = yuk[i]
                n2, f2 = yuk[j]
                phis.append((f"{n1}&{n2}",
                             (lambda f1, f2: lambda s, a: f1(s, a) and f2(s, a))(f1, f2),
                             2))
    if derinlik >= 3:
        for i in range(len(yuk)):
            for j in range(i + 1, len(yuk)):
                for k in range(j + 1, len(yuk)):
                    n1, f1 = yuk[i]; n2, f2 = yuk[j]; n3, f3 = yuk[k]
                    phis.append((f"{n1}&{n2}&{n3}",
                                 (lambda f1, f2, f3: lambda s, a:
                                  f1(s, a) and f2(s, a) and f3(s, a))(f1, f2, f3),
                                 3))

    kenarlar = []
    for (pn, pf, oz) in phis:
        for d in dunya.YER_DEGISIMLERI:
            kenarlar.append(EdgeP(pf, (lambda d: lambda s, a: d)(d),
                                  name=f"{pn} -> {d}", Nmax=Nmax, tau=tau,
                                  alpha=alpha, ozgulluk=oz))
    return kenarlar
