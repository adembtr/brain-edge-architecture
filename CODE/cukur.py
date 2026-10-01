"""
cukur.py — CUKUR (attractor).  kenar_mimarisi.md'nin 4. nesnesinin somut hali.

kenar_mimarisi §1: "Kase = tum kenarlarin birlikte tanimladigi akis alani."
DEVIR.md §4:       "Cukurlar (attractor) = akisin kendine dondugu yerler."

Adem'in tasarimi:
  "Isleyen her eylem dizisi bir CUKUR olur. Cukurun GIRISI ve SONUCU belli.
   Kosullar saglanirsa o cukura girer, sonunda cikar, yeni durum insa eder.
   Cukurlar birlesip EN BUYUK CUKURU olusturur. Seviye gecme en buyuk cukur."

  "Tek amac DEGISIM. Degisim varsa bu hedef iyidir, SAKLA ve ustune insa et.
   Seviye gecmeden daha buyuk hedef olmadigi icin hep oraya oynayacak.
   Eylem dizisinin sonunda degisim yoksa YON DEGISTIRMELI."

MIMARIYE BAGLANTI — cukur AYRI bir nesne DEGIL:
    kenar_mimarisi §2:  e = (phi, psi, q, p, N, g)
    cukur            :  phi   = giris kosulu (sahnede hangi tokenlar var)
                        govde = eylem dizisi          <- zamandaki uzunluk
                        psi   = beklenen degisim
                        q,p,N = AYNI FIZIK
    phi daraltma = UZAYDA dogum.   Cukur = ZAMANDA dogum.
    Cukur birlesmesi = §4'teki hiyerarsi (bir cukurun cikisi otekinin phi'si).

Odul YOK. "Dogru" YOK. "Seviye" kelimesi ajanin karar kodunda GECMIYOR.
Tek sayi: kac hucre degisti.
"""
import os, sys, random, json
from collections import defaultdict, Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from nesne import (nesneler, token, iliskiler, degisim, etki, Ajan,   # noqa: E402
                   AGI, P)


# =====================================================================
class Cukur:
    """Zamanda dogmus kenar. Fizik edge.py ile ayni."""
    __slots__ = ("giris", "govde", "psi", "q", "p", "N", "Nmax",
                 "alpha", "tau", "eta", "uses", "hits", "dogdu")

    def __init__(self, giris, govde, psi, Nmax=4.0, tau=4.0,
                 alpha=0.30, eta=0.15, dogdu=0):
        # OLCULEN HATA: giris, sahnedeki BUTUN tokenlar diye yaziliyordu.
        # Sahne degistigi icin "giris subset sahne" sarti bir daha neredeyse
        # hic saglanmiyor -> cukura girilmiyor -> fiilen UNUTULUYOR.
        # Oysa cukurun amaci tam tersi: eylemleri UNUTMAMAK.
        # Dogrusu: cukurun GOVDESININ KULLANDIGI tokenlar. "Bu cukuru
        # calistirmak icin su nesnelerin sahnede olmasi YETER."
        self.giris = frozenset(k[0] for k in govde) or frozenset(giris)
        self.govde = list(govde)          # eylem dizisi
        self.psi = float(psi)             # beklenen degisim
        self.q, self.p = 0.6, 0.5
        self.N = self.Nmax = Nmax
        self.alpha, self.tau, self.eta = alpha, tau, eta
        self.uses = self.hits = 0
        self.dogdu = dogdu

    def uygun(self, sahne):
        return self.giris <= sahne

    def q_eff(self):
        return self.q * (self.N / self.Nmax)

    def verim(self):
        """EYLEM BASINA degisim. Cukurun uzunlugu BEDAVA DEGIL."""
        return self.psi / max(1, len(self.govde))

    def deger(self):
        """Verim x guvenilirlik. Uzun cukur, ancak eylem basina iyiyse cekici."""
        return self.verim() * self.q_eff() * max(self.p, 0.05)

    def harca(self):
        self.N = max(0.0, self.N - 1.0); self.uses += 1

    def tik(self):
        self.N += (self.Nmax - self.N) / self.tau

    def ogren(self, gercek):
        tuttu = gercek >= 0.5 * self.psi
        self.q = min(1.0, max(0.0, self.q + self.alpha * (1 if tuttu else -1)))
        self.p += self.eta * ((1.0 if tuttu else 0.0) - self.p)
        self.psi = 0.8 * self.psi + 0.2 * gercek     # beklenti kayar
        if tuttu:
            self.hits += 1

    def olu(self, q_min=0.05):
        return self.q < q_min and self.uses >= 4

    def __repr__(self):
        return (f"<cukur |{len(self.govde)}| psi={self.psi:.0f} "
                f"q={self.q:.2f} p={self.p:.2f} {self.hits}/{self.uses}>")


# =====================================================================
class Kase:
    """Butun cukurlarin toplami = akis alani."""

    def __init__(self):
        self.cukurlar = []
        self.dogum = self.olum = self.birlesme = 0

    def uygun(self, sahne):
        return [c for c in self.cukurlar if c.uygun(sahne) and not c.olu()]

    def dogur(self, giris, govde, degisim_, tik, en_kisa=1, esik=1.0):
        """ZAMANDA DOGUM: degisim ureten dizi cukur olur."""
        if len(govde) < en_kisa or degisim_ < esik:
            return None
        for c in self.cukurlar:                 # ayni govde varsa guclendir
            if c.govde == list(govde):
                c.ogren(degisim_)
                return c
        c = Cukur(giris, govde, degisim_, dogdu=tik)
        self.cukurlar.append(c); self.dogum += 1
        return c

    def birlestir(self, a, b, tik):
        """
        CUKURLAR BIRLESIR -> DAHA BUYUK CUKUR.
        a'nin cikisi b'nin girisini sagliyorsa zincir tek cukur olur.
        (kenar_mimarisi §4: bir noronun ciktisi otekinin phi'sinde -> KATMAN)
        """
        if a is b or len(a.govde) + len(b.govde) > 8:
            return None
        # KANIT SARTI: ikisi de en az bir kez ISE YARAMIS olmali.
        # (olculdu: sartsiz birlestirme 200 dogumda 199 birlesme uretti)
        # Cok siki olursa HIC birlesme olmuyor (olculdu: 190 dogum, 0 birlesme)
        # ve "cukurlar birlesip en buyuk cukuru olusturur" hic gerceklesmiyor.
        # Denge: ONDEKI cukur en az bir kez ise yaramis olmali.
        if a.uses < 1 or a.p < 0.3:
            return None
        govde = a.govde + b.govde
        for c in self.cukurlar:
            if c.govde == govde:
                return None                     # zaten var
        # Birlesme ancak VERIMI dusurmuyorsa yapilir (MDL: uzunluk maliyet)
        yeni_verim = (a.psi + b.psi) / len(govde)
        if yeni_verim < 0.8 * max(a.verim(), b.verim()):
            return None
        yeni = Cukur(a.giris, govde, a.psi + b.psi, dogdu=tik)
        yeni.q = min(a.q, b.q); yeni.p = min(a.p, b.p)
        self.cukurlar.append(yeni); self.birlesme += 1
        return yeni

    def buda(self, ust=50):
        once = len(self.cukurlar)
        self.cukurlar = [c for c in self.cukurlar if not c.olu()]
        if len(self.cukurlar) > ust:            # MDL: en degerliler kalir
            self.cukurlar.sort(key=lambda c: -c.deger())
            self.cukurlar = self.cukurlar[:ust]
        self.olum += once - len(self.cukurlar)


# =====================================================================
def sahne_adaylari(o, aj_bos=None):
    grid = o["grid"]
    obs = nesneler(grid)
    eylemler = o["avail"] or [6]
    if obs:
        ic, dg, es = iliskiler(obs)
        kaba = Counter(token(x, 0, 0) for x in obs)
    else:
        ic = dg = es = []; kaba = None
    adaylar = defaultdict(list)
    for i, ob in enumerate(obs):
        yal = 1 if (kaba is not None and kaba[token(ob, 0, 0)] == 1) else 0
        tk = token(ob, 0, 0, (ic[i], dg[i], es[i]), yal)
        h = random.choice(sorted(ob.cells))
        for a2 in eylemler:
            adaylar[(tk, a2)].append((int(h[1]), int(h[0]), a2))
    return adaylar, frozenset(k[0] for k in adaylar)


def _adim(e, o, aj, k_zorla=None):
    adaylar, sahne = sahne_adaylari(o)
    if not adaylar:
        return o, 0.0, None, sahne
    k = k_zorla if (k_zorla in adaylar) else aj.sec(adaylar)[0]
    cx, cy, a = random.choice(adaylar[k])
    aj.harca(k); aj.tik(list(adaylar.keys()))
    grid = o["grid"]
    o2 = e.step("click", a, cx, cy) if a == 6 else e.step("act", a)
    d = float(degisim(grid, o2["grid"]))
    aj.ogren(k, etki(grid, o2["grid"]))
    return o2, d, k, sahne


def kosu(oyun, butce=800, tohum=0, pencere=4, mod="cukur"):
    """
    AKIS. Adem: "noronlarda cukurlar var... ilerledikce KOSULLAR SAGLANIRSA
    o cukura GIRER, sonunda cikar, yeni durum insa eder."

    Yani cukur bastan oynanan bir kayit degil; akis YOLDA icine duser.
    (Ilk surumde her tur sifirlanip zincir bastan oynaniyordu -> butce
     tekrara gidiyordu, seviye gelmiyordu. Olculdu, duzeltildi.)

    Dongu:
      - sahnedeki tokenlar bir cukurun GIRISINI sagliyorsa ve cukur
        degerliyse -> CUKURA GIR (govdesini uygula), cikista ogren
      - saglamiyorsa -> tek adim kesif
      - son `pencere` adimda degisim olduysa -> ZAMANDA DOGUM (yeni cukur)
      - ust uste iki cukur ise yaradiysa -> BIRLESTIR (daha buyuk cukur)
      - dizinin sonunda degisim yoksa -> YON DEGISTIR (N dusur)
    """
    from env import Env
    random.seed(tohum)
    e = Env(oyun); o = e.reset()
    aj = Ajan(); kase = Kase()
    en_sv, ilk, t, kuru, dongu = 0, None, 0, 0, 0
    tampon = []                 # son adimlar: (giris, k, degisim)
    son_cukur = None
    en_deg = 0.0

    while t < butce:
        adaylar, sahne = sahne_adaylari(o)
        if not adaylar:
            o = e.reset(); continue

        # ---- ONCE EYLEM SOZLUGU (Adem'in notlari, m0r0 sv1) ----
        # "1-2-3-4-5-6-7 tiklayarak tasima tuslarini bulacagim."
        # Her eylem en az bir kez denenmeden cukura girilmez.
        denenmemis = [k for k in adaylar if aj.kullanim[k] == 0]
        if denenmemis and t < SOZLUK_ADIM:   # SABIT, butceyle olceklenmez
            k0 = random.choice(denenmemis)
            o, d, k, giris = _adim(e, o, aj, k0)
            t += 1
            if k: tampon.append((giris, k, d))
            if o["level"] > en_sv:
                en_sv = o["level"]; ilk = ilk or t
            if o["state"] not in ("NOT_FINISHED", "NOT_STARTED"):
                o = e.reset()
            if len(tampon) >= pencere:          # pencereyi burada da bosalt
                dilim = sum(x[2] for x in tampon)
                if dilim > 0:
                    kase.dogur(tampon[0][0], [x[1] for x in tampon], dilim, t)
                    en_deg = max(en_deg, dilim)
                tampon = []
            continue

        # ---- KOSUL SAGLANDI MI? cukura gir ----
        uygunlar = [c for c in kase.uygun(sahne) if c.q_eff() > 0.25]
        girildi = None
        if uygunlar:
            c = max(uygunlar, key=lambda c: c.deger())
            # OLCULEN HATA (BULGULAR §10.3): giris sarti GORELIYDI
            # (deger >= 0.6*en_deg). en_deg firlayinca hicbir cukur esigi
            # gecemedi -> cukura hic girilmedi -> uses=0 -> birlesme=0 ->
            # cukur hic buyumedi. Sistem KENDI BASARISI yuzunden kilitlendi.
            # Duzeltme: cukur KENDI gecmisine gore degerlendirilir.
            if c.q_eff() > 0.30 and c.psi > 0 and c.govde:
                girildi = c; c.harca(); ic = 0.0
                for i_k, k in enumerate(c.govde):
                    if t >= butce: break
                    o, d, _, _ = _adim(e, o, aj, k)
                    t += 1; ic += d
                    if o["level"] > en_sv:
                        en_sv = o["level"]; ilk = ilk or t
                    if o["state"] not in ("NOT_FINISHED", "NOT_STARTED"):
                        o = e.reset(); break
                    # ERKEN CIKIS: cukur KISAYOL olmali, tekrar degil.
                    # Ilk ucte birde hic degisim yoksa gerisi bosa eylem.
                    if i_k >= max(2, len(c.govde)//3) and ic == 0:
                        break
                c.ogren(ic)                      # cikista ogren
                en_deg = max(en_deg, ic)
                if ic > 0 and son_cukur is not None and son_cukur is not c:
                    b = kase.birlestir(son_cukur, c, t)   # CUKURLAR BIRLESIR
                    if b: b.psi = son_cukur.psi + ic
                son_cukur = c if ic > 0 else None
                tampon = []
                if ic == 0: kuru += 1
                else: kuru = 0

        # ---- cukura girilmediyse: tek adim kesif ----
        if girildi is None:
            o, d, k, giris = _adim(e, o, aj)
            t += 1
            if k: tampon.append((giris, k, d))
            if o["level"] > en_sv:
                en_sv = o["level"]; ilk = ilk or t
            if o["state"] not in ("NOT_FINISHED", "NOT_STARTED"):
                o = e.reset()
            if len(tampon) >= pencere:
                dilim = sum(x[2] for x in tampon)
                if dilim > 0:                    # ---- ZAMANDA DOGUM ----
                    c = kase.dogur(tampon[0][0], [x[1] for x in tampon],
                                   dilim, t)
                    en_deg = max(en_deg, dilim)
                    if c is not None and son_cukur is not None:
                        b = kase.birlestir(son_cukur, c, t)
                        if b: b.psi = son_cukur.psi + dilim
                    son_cukur = c; kuru = 0
                else:                            # ---- YON DEGISTIR ----
                    kuru += 1
                    for kk in [x[1] for x in tampon]:
                        aj.N[kk] = max(0.0, aj.N[kk] - 1.0)
                    if kuru >= 8:
                        en_deg *= 0.7; son_cukur = None; kuru = 0
                tampon = []
        for c in kase.cukurlar:
            c.tik()
        dongu += 1
        if dongu % 40 == 0:
            kase.buda()

    return dict(sv=en_sv, ilk=ilk, cukur=len(kase.cukurlar),
                dogum=kase.dogum, birlesme=kase.birlesme,
                zincir=0, en_deg=int(en_deg),
                uzun=max([len(c.govde) for c in kase.cukurlar] or [0]), tur=t)


def rastgele(oyun, butce=800, tohum=0):
    from env import Env
    rnd = random.Random(tohum); e = Env(oyun); o = e.reset(); sv = 0
    H, W = len(o["grid"]), len(o["grid"][0])
    for _ in range(butce):
        a = rnd.choice(o["avail"] or [6])
        o = (e.step("click", a, rnd.randrange(W), rnd.randrange(H))
             if a == 6 else e.step("act", a))
        sv = max(sv, o["level"])
        if o["state"] not in ("NOT_FINISHED", "NOT_STARTED"):
            o = e.reset()
    return sv


if __name__ == "__main__":
    oyunlar = sys.argv[1:] or sorted(os.listdir(os.environ["ENVIRONMENTS_DIR"]))
    print("=" * 84)
    print("CUKUR — isleyen her eylem dizisi bir cukur. Cukurlar birlesir.")
    print("Tek amac DEGISIM. Odul yok, 'dogru' yok, 'seviye' kelimesi karar")
    print("kodunda gecmiyor. 800 eylem/oyun, 2 tohum.")
    print("=" * 84)
    print(f"  {'oyun':<7}{'RND':>5}{'CUKUR':>7}{'cukur#':>8}{'dogum':>7}"
          f"{'birles':>8}{'zincir':>8}{'en_uzun':>9}{'en_deg':>8}{'ilk sv@':>9}")
    top_r = top_c = ust = 0; ozet = {}
    for g in oyunlar:
        try:
            r = max(rastgele(g, tohum=s) for s in (0, 1))
            ns = [kosu(g, tohum=s) for s in (0, 1)]
        except Exception as ex:
            print(f"  {g:<7}  HATA {type(ex).__name__}: {str(ex)[:34]}")
            continue
        n = max(ns, key=lambda d: d["sv"])
        il = [d["ilk"] for d in ns if d["ilk"]]
        im = "  <--" if n["sv"] > r else ""
        ust += 1 if n["sv"] > r else 0
        top_r += r; top_c += n["sv"]
        ozet[g] = dict(rnd=r, cukur=n["sv"], n=n["cukur"], uzun=n["uzun"])
        print(f"  {g:<7}{r:>5}{n['sv']:>7}{n['cukur']:>8}{n['dogum']:>7}"
              f"{n['birlesme']:>8}{n['zincir']:>8}{n['uzun']:>9}{n['en_deg']:>8}"
              f"{(str(min(il)) if il else '-'):>9}{im}", flush=True)
        json.dump(ozet, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "cukur_ozet.json"), "w"),
                  indent=1)
    print(f"\n  TOPLAM seviye: rastgele {top_r}  ->  CUKUR {top_c}"
          f"   ({ust}/{len(ozet)} oyunda ustun)")
    json.dump(ozet, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "cukur_ozet.json"), "w"), indent=1)
