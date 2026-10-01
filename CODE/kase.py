"""
kase.py — KASE. Adem'in 4. nesnesi, ve ".pt karsiligi ne?" sorusunun cevabi.

kenar_mimarisi.md §1:  "Kase = tum kenarlarin birlikte tanimladigi akis alani.
                        Kase bir DEPO degil, bir KURAL'dir."
DEVIR.md acik soru 6:  "Kasenin ARC karsiligi ne?"

CEVAP: kase = beynin agirlik dosyasi. LLM'de .pt, bizde .kase

    LLM              BIZ
    ---              ---
    agirlik = sayi   agirlik = KURAL (terim)
    tensor           terim listesi
    .pt (binary)     .kase (JSON - ACILIP OKUNABILIR)
    egitim biter     egitim bitmez, dosya yasar

Bu dosya sunlari yapar:
    KAYIT   kaydet()/yukle()  -> beyin diske yazilir, aynen devam eder
    DOGUM   dogur()           -> YENI KURAL URETIR (lambda ile imkansizdi)
    BUDAMA  buda()            -> olum + KOPYA BIRLESTIRME + KAPSAMA (MDL)
    BILESIM ("noron",...) atomu -> noron ciktisi YENI KELIME olur
"""

import json
from collections import deque
from terim import Terim, Tahmin, BAGLAM


def _clip(x, lo, hi):
    return lo if x < lo else (hi if x > hi else x)


# =====================================================================
class Kenar:
    """edge.py'nin terim-tabanli hali. Ayni fizik, ama phi/psi VERI."""

    __slots__ = ("phi", "psi", "q", "p", "N", "Nmax", "alpha", "tau",
                 "beta", "eta", "uses", "hits", "isabetler", "hatalar",
                 "dogdu", "dogum_denemesi", "gorulme")

    def __init__(self, phi, psi, q=0.5, p=0.5, Nmax=4.0, alpha=0.30,
                 tau=3.0, beta=1.0, eta=0.15, dogdu=0):
        self.phi, self.psi = phi, psi
        self.q, self.p, self.N, self.Nmax = q, p, Nmax, Nmax
        self.alpha, self.tau, self.beta, self.eta = alpha, tau, beta, eta
        self.uses = self.hits = 0
        self.dogum_denemesi = 0
        self.gorulme = 0          # kac kez AKTIF oldu (spend'den bagimsiz)
        # Isabet sik, hata NADIR ve BILGILENDIRICI. Ayni tamponda tutmak
        # nadir baglamlari (kutu itme ~%3) bogar -> dogum hic tetiklenmez.
        # Surpriz daha uzun hatirlanir. (Ayni sezgi: N += beta*err)
        self.isabetler = deque(maxlen=40)
        self.hatalar = deque(maxlen=120)
        self.dogdu = dogdu

    def active(self, s, a):  return self.phi(s, a)
    def q_eff(self):         return self.q * (self.N / self.Nmax)
    def predict(self, s, a): return self.psi(s, a)
    def ozgulluk(self):      return self.phi.uzunluk()

    def spend(self):
        self.N = max(0.0, self.N - 1.0); self.uses += 1

    def tick(self):
        self.N += (self.Nmax - self.N) / self.tau

    def learn(self, s, a, err, gozlenen=None):
        self.q = _clip(self.q + self.alpha * (1.0 - 2.0 * err), 0.0, 1.0)
        self.N = min(self.Nmax, self.N + self.beta * err)
        self.gorulme += 1
        isabet = err < 0.5
        self.p = _clip(self.p + self.eta * ((1.0 if isabet else 0.0) - self.p), 0, 1)
        if isabet:
            self.hits += 1
            self.isabetler.append((s, a, gozlenen))
        else:
            self.hatalar.append((s, a, gozlenen))

    def dead(self, q_min=0.05, min_deneme=3):
        """Kenar, DARALMA sansini kullanmadan olemez (kenar_mimarisi §3)."""
        return self.q < q_min and self.dogum_denemesi >= min_deneme

    def json(self):
        return {"phi": self.phi.json(), "psi": self.psi.json(),
                "q": round(self.q, 4), "p": round(self.p, 4),
                "N": round(self.N, 4), "Nmax": self.Nmax,
                "uses": self.uses, "hits": self.hits,
                "gorulme": self.gorulme, "dogdu": self.dogdu}

    @staticmethod
    def yukle(d):
        e = Kenar(Terim.yukle(d["phi"]), Tahmin.yukle(d["psi"]),
                  q=d["q"], p=d["p"], Nmax=d["Nmax"], dogdu=d.get("dogdu", 0))
        e.N = d["N"]; e.uses = d["uses"]; e.hits = d["hits"]
        e.gorulme = d.get("gorulme", 0)
        return e

    def __repr__(self):
        return f"[{self.phi} -> {self.psi} | q={self.q:.2f} p={self.p:.2f} oz={self.ozgulluk()}]"


# =====================================================================
# Ozgullugun HAK EDILMESI gereken esik.
# OLCULEN HATA: "en ozel kazanir" kurali SABIT havuzda en iyiydi (0.999).
# Ama DOGUM varken yeni dogan kenar (q=0.5, p=0.5) sirf ozgul oldugu icin
# 5000 kez dogrulanmis kenari susturuyor -> dogruluk 0.62'den 0.43'e dustu.
# Duzeltme: ozgulluk ancak GUVENILIRLIK kazanildiysa sayilir.
P_ESIK = 0.70


def kural_ozel_isabet(aktifler, s, a):
    """test_neuron.py TEST N3'un kazanani + dogum kapisi."""
    w = max(aktifler, key=lambda e: (e.ozgulluk() if e.p >= P_ESIK else 0,
                                     e.q_eff() * e.p))
    return w.predict(s, a), w.q_eff() * w.p, w


class Noron:
    """
    KATMAN (bilesim kisiti):
      Bir noron SADECE kendinden KUCUK katmandaki noronlari kelime olarak
      kullanabilir. Yoksa noron kendi kendini sorar -> sonsuz dongu.
      (Bu hata gercekten olustu ve mimariyi duzeltti.)

    DEVIR.md 5.1: "bir noronun ciktisi baska bir noronun phi'sinde gecerse
    KATMAN olusur. Katman elle tasarlanmaz." -- katman sayisi elle
    verilmiyor; sadece SIRA veriliyor, hangi kelimenin kullanilacagini
    dogum seciyor.
    """

    def __init__(self, hedef, katman=0):
        self.hedef, self.kenarlar, self.katman = hedef, [], katman

    def bagla(self, e): self.kenarlar.append(e)

    def aktifler(self, s, a):
        return [e for e in self.kenarlar if e.active(s, a)]

    def predict(self, s, a):
        akt = self.aktifler(s, a)
        if not akt: return None, 0.0, None
        return kural_ozel_isabet(akt, s, a)

    def learn(self, s, a, gozlenen):
        for e in self.aktifler(s, a):
            e.learn(s, a, 0.0 if e.predict(s, a) == gozlenen else 1.0, gozlenen)

    def tick(self):
        for e in self.kenarlar: e.tick()


# =====================================================================
class Kase:
    """Beynin kendisi. Tum noronlar + tum kenarlar + uzayin dili."""

    def __init__(self, tipleyici=None, eksenler=("x", "y")):
        self.noronlar = {}
        self.tipleyici = tipleyici
        self.eksenler = list(eksenler)
        self.ek_alfabe = []          # (x,y,t) atomlari buradan girer
        self.dogum_sayisi = self.budama_sayisi = self.birlesme_sayisi = 0
        self.kapsama_sayisi = 0
        self.revizyon_sayisi = 0
        self.tik = 0

    def noron(self, hedef, katman=0):
        if hedef not in self.noronlar:
            self.noronlar[hedef] = Noron(hedef, katman)
            BAGLAM.noronlar[hedef] = self.noronlar[hedef]
        return self.noronlar[hedef]

    def kenar_sayisi(self):
        return sum(len(n.kenarlar) for n in self.noronlar.values())

    # ---------------- ALFABE: dogumda denenecek atomlar ----------------
    def alfabe(self, eylemler=(0, 1, 2, 3), katman_ust=0):
        if self.ek_alfabe:
            return list(self.ek_alfabe)
        A = [("eylem", k) for k in eylemler]
        if self.tipleyici:
            for t in range(self.tipleyici.tip_sayisi()):
                A += [("hedef_tip", t), ("otesi_tip", t)]
            parcalar = sorted({p for v in self.tipleyici.imza
                               for p in self.tipleyici.imza[v]},
                              key=str)
            for p in parcalar:
                A += [("hedef_parca",) + tuple(p), ("otesi_parca",) + tuple(p)]
        # BILESIM: SADECE alt katmandaki noronlarin ciktisi kelime olur.
        for ad, n in self.noronlar.items():
            if n.katman >= katman_ust:
                continue                      # <- dongu kapisi
            for d in {e.psi.delta for e in n.kenarlar}:
                A.append(("noron", ad) + tuple(d))
        return A

    # ---------------- DOGUM ----------------
    def dogur(self, noron, kenar, min_ornek=4, min_ayirma=0.55):
        """
        HIPOTEZ URETIMI. Kenar hem tutmus (H) hem tutmamis (M).
        IKI kural birden dogar:

          COCUK  : phi & alfa  -> ayni psi     "yasadigim yere cekiliyorum"
          KARDES : phi & beta  -> YENI psi     "orada baska bir sey oluyor"

        alfa: H'de dogru, M'de yanlis olan atom   (h - m buyuk)
        beta: M'de dogru, H'de yanlis olan atom   (m - h buyuk)

        Kardes olmadan sistem sadece KUCULUR (olculdu: OLCUM 9'da 20 kenarin
        hepsi 40 adimda oldu ve sistem sessizlesti). Kardes DOGUM yoludur.

        DURUSTLUK: bu, ALFABE ICINDEN secim (predicate selection).
        Alfabenin kendisini uretmiyor. Ama alfabede ("noron",...) atomu var
        -> sistemin KENDI urettigi kelimeler de aday. Icat oradan basliyor.
        """
        from terim import atom_degerlendir
        from collections import Counter

        H = [(s, a) for (s, a, g) in kenar.isabetler]
        M = list(kenar.hatalar)
        if len(H) < min_ornek or len(M) < min_ornek:
            kenar.dogum_denemesi += 1
            return None

        alfabe = self.alfabe(katman_ust=noron.katman)
        en_a, sk_a, en_b, sk_b = None, 0.0, None, 0.0
        for atom in alfabe:
            if kenar.phi.icerir(atom):
                continue
            try:
                h = sum(1 for (s, a) in H if atom_degerlendir(atom, s, a)) / len(H)
                m = sum(1 for (s, a, _) in M if atom_degerlendir(atom, s, a)) / len(M)
            except Exception:
                continue
            if h - m > sk_a: en_a, sk_a = atom, h - m
            if m - h > sk_b: en_b, sk_b = atom, m - h

        kenar.dogum_denemesi += 1
        dogan = []
        if en_a is not None and sk_a >= min_ayirma:
            dogan.append(Kenar(kenar.phi.daralt(en_a), kenar.psi,
                               q=kenar.q, p=kenar.p, Nmax=kenar.Nmax,
                               dogdu=self.tik))
        if en_b is not None and sk_b >= min_ayirma:
            # DUZELTME: psi, SADECE beta'nin tuttugu hata durumlarindan
            # secilmeli. Tum M'den secmek farkli baglamlari karistiriyordu.
            sik = Counter(g for (s, a, g) in M
                          if g is not None and atom_degerlendir(en_b, s, a))
            if sik:
                yeni_psi = Tahmin(sik.most_common(1)[0][0])
                dogan.append(Kenar(kenar.phi.daralt(en_b), yeni_psi,
                                   q=0.5, p=0.5, Nmax=kenar.Nmax,
                                   dogdu=self.tik))
        for c in dogan:
            noron.bagla(c)
            self.dogum_sayisi += 1
        if dogan:
            kenar.dogum_denemesi = 0        # basarili dogum -> kredi yenilenir
        kenar.isabetler.clear(); kenar.hatalar.clear()
        return dogan or None

    # ---------------- PSI REVIZYONU (hamle 1) ----------------
    def revize(self, kenar, min_ornek=6):
        """
        kenar_mimarisi.md §3: hata aninda UC yarisan hamle var
            1. psi'yi REVIZE ET     <- BU EKSIKTI
            2. q'yu dusur
            3. phi'yi daralt (dogum)

        Kodda sadece 2 ve 3 vardi. Sonuc (gercek ARC oyunlarinda olculdu):
        HIC DOGRU OLMAYAN bir kural dogum yapamiyor -- cunku dogum hem
        ISABET hem HATA kumesi ister, isabet kumesi bos. Kural sadece
        oluyor ve yerine bir sey gelmiyor. Dogruluk 0.000'de kaliyordu.

        Cozum: isabet yoksa ama hata bolsa, phi'yi daraltmadan once
        TAHMINI duzelt. "Ne dedigimi degil, NE GORDUGUMU soyle."
        """
        from collections import Counter
        if len(kenar.isabetler) >= min_ornek or len(kenar.hatalar) < min_ornek:
            return False
        sik = Counter(g for (_, _, g) in kenar.hatalar if g is not None)
        if not sik:
            return False
        yeni, adet = sik.most_common(1)[0]
        if adet / len(kenar.hatalar) < 0.5:      # net bir cogunluk yoksa dokunma
            return False
        if Tahmin(yeni) == kenar.psi:
            return False
        kenar.psi = Tahmin(yeni)
        kenar.q = max(kenar.q, 0.5)              # yeni iddiaya sifirdan sans
        kenar.p = 0.5
        kenar.dogum_denemesi = 0
        kenar.isabetler.clear(); kenar.hatalar.clear()
        self.revizyon_sayisi += 1
        return True

    # ---------------- BUDAMA (guclendirilmis) ----------------
    def buda(self, q_min=0.05):
        """
        DEVIR.md risk 2: "kucultmek buyutmekten zor. q<q_min budamasi
        muhtemelen yetmez; MDL tabanli kenar BIRLESTIRME lazim olacak."

        Uc asama:
          1. OLUM      q cok dusuk
          2. BIRLESME  ayni (phi, psi) -> tek kenar     (terim VERI oldugu icin mumkun)
          3. KAPSAMA   ozel kenar, genel ebeveyniyle AYNI seyi soyluyorsa sil (MDL)
        """
        for n in self.noronlar.values():
            # 1. olum
            once = len(n.kenarlar)
            kalan = [e for e in n.kenarlar if not e.dead(q_min)]
            if not kalan and n.kenarlar:
                # OLCULMUS HATA (cd82): noron son kenarini da kaybedince
                # sessizlesiyor ve bir daha hicbir sey ogrenemiyor.
                # En az bir kenar hep ayakta kalir; psi revizyonu onu
                # tekrar ise yarar hale getirebilir.
                kalan = [max(n.kenarlar, key=lambda e: e.p)]
                kalan[0].q = 0.5; kalan[0].dogum_denemesi = 0
            n.kenarlar = kalan
            self.budama_sayisi += once - len(n.kenarlar)

            # 2. birlesme: ayni terim + ayni tahmin
            gorulen = {}
            yeni = []
            for e in n.kenarlar:
                k = (e.phi, e.psi)
                if k in gorulen:
                    o = gorulen[k]
                    o.q = max(o.q, e.q); o.p = max(o.p, e.p)
                    o.uses += e.uses; o.hits += e.hits
                    self.birlesme_sayisi += 1
                else:
                    gorulen[k] = e; yeni.append(e)
            n.kenarlar = yeni

            # 3. kapsama: ozel kenar ebeveyniyle ayni sey diyorsa gereksiz
            genel = {}
            for e in n.kenarlar:
                genel.setdefault(e.psi, []).append(e)
            silinecek = set()
            for psi, grup in genel.items():
                grup.sort(key=lambda e: e.phi.uzunluk())
                for i, ozel in enumerate(grup):
                    for gen in grup[:i]:
                        if set(gen.phi.atomlar) < set(ozel.phi.atomlar) \
                           and gen.p >= ozel.p - 0.02 and gen.p > 0.95 \
                           and gen.gorulme >= 30 and ozel.gorulme >= 30:
                            silinecek.add(id(ozel)); break
            if silinecek:
                self.kapsama_sayisi += len(silinecek)
                n.kenarlar = [e for e in n.kenarlar if id(e) not in silinecek]

            # 4. OLU YUKLEM: cok uzun sure hic ateslenmeyen kenar bilgi
            # tasimiyor, sadece yer kapliyor. (phi patlamasina karsi.)
            once = len(n.kenarlar)
            n.kenarlar = [e for e in n.kenarlar
                          if e.gorulme > 0 or (self.tik - e.dogdu) < 600]
            self.budama_sayisi += once - len(n.kenarlar)

    # ---------------- KAYIT ----------------
    def kaydet(self, yol):
        veri = {
            "surum": 1,
            "uzay": {"eksenler": self.eksenler},
            "tipler": ({str(k): v for k, v in self.tipleyici.tipler().items()}
                       if self.tipleyici else {}),
            "parcalar": ({str(v): sorted(map(list, self.tipleyici.imza[v]), key=str)
                          for v in sorted(self.tipleyici.imza)}
                         if self.tipleyici else {}),
            "istatistik": {"tik": self.tik, "dogum": self.dogum_sayisi,
                           "olum": self.budama_sayisi,
                           "birlesme": self.birlesme_sayisi,
                           "revizyon": self.revizyon_sayisi,
                           "kapsama": self.kapsama_sayisi},
            "noronlar": [{"hedef": ad,
                          "kenarlar": [e.json() for e in n.kenarlar]}
                         for ad, n in self.noronlar.items()],
        }
        with open(yol, "w") as f:
            json.dump(veri, f, indent=1)
        return yol

    @staticmethod
    def yukle(yol, tipleyici=None):
        with open(yol) as f:
            veri = json.load(f)
        k = Kase(tipleyici, veri["uzay"]["eksenler"])
        k.tik = veri["istatistik"]["tik"]
        k.dogum_sayisi = veri["istatistik"]["dogum"]
        for nd in veri["noronlar"]:
            n = k.noron(nd["hedef"])
            for ed in nd["kenarlar"]:
                n.bagla(Kenar.yukle(ed))
        return k
