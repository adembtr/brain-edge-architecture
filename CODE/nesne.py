"""
nesne.py — ALFABE = NESNELER.  (Adem'in tasarimi)

"Her nesne bir token: genislik, uzunluk, xy, sekli (yuvarlak/kare),
 kapladigi alan, rengi, durumu. Nesneler boyle olmali, bu bir alfabe."

Iki kazanc birden:
  1. phi'nin alfabesi: hucre renkleri yerine NESNE OZELLIKLERI
  2. EYLEM UZAYI: 64x64=4096 hucre yerine ~N nesne  (buyuk kisalma)

Eylemler: 1..5 (ne yaptiklari BILINMIYOR) + 6 (tiklama).
Ajan hicbirinin anlamini bilmiyor; hepsini denemek zorunda.
"""
import os, sys, random, json
from collections import defaultdict, Counter

AGI = os.environ.get("AGI_DIR", os.path.abspath(os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "..", "arc-agi3-agent")))
os.environ.setdefault("OPERATION_MODE", "offline")
os.environ.setdefault("ENVIRONMENTS_DIR", f"{AGI}/environment_files")
os.environ.setdefault("MPLBACKEND", "agg")
sys.path.insert(0, f"{AGI}/denme"); sys.path.insert(0, f"{AGI}/denme/infra")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import perception as P                                    # noqa: E402


def _kova(n, kesim=(1, 2, 4, 9, 25, 100)):
    for i, k in enumerate(kesim):
        if n <= k:
            return i
    return len(kesim)


SEKIL = {}          # canonical mask -> sekil id (ISIM YOK, sadece numara)


def sekil_id(ob):
    c = ob.canonical
    if c not in SEKIL:
        SEKIL[c] = len(SEKIL)
    return SEKIL[c]


def iliskiler(obs):
    """
    ONERILEN ATOMLAR (LLM YOK -- elle onerildi, sistem SINAYACAK).
    Olculen eksik: nesneler ARASI iliski. cd82/cn04/dc22 tam bunun icin
    cuvalliyordu. Dordu de perception.py'de zaten yazili.

    Hepsi 0/1 -- kaba tutuldu, cunku ince alfabe genellemiyor (bkz. §8).
    """
    n = len(obs)
    ic = [0]*n; dg = [0]*n; es = [0]*n
    for i in range(n):
        for j in range(n):
            if i == j:
                continue
            if not ic[i] and P.contains(obs[j], obs[i]): ic[i] = 1      # icinde
            if not dg[i] and P.touching(obs[i], obs[j]): dg[i] = 1      # degiyor
            if not es[i] and P.same_shape(obs[i], obs[j]): es[i] = 1    # esi var
    return ic, dg, es


def token(ob, H, W, il=(0, 0, 0), yalniz=0):
    """
    NESNE TOKEN'I = alfabenin harfi.
    Adem'in listesi: renk, genislik, uzunluk, alan, sekil, konum, durum.
    Hicbiri isim tasimaz -- hepsi olcum.
    """
    h, w = ob.height, ob.width
    dolu = ob.size / max(1, w * h)      # doluluk: 1.0=dolu kare, ~0.8=yuvarlak
    return (
        ob.color,                        # rengi
        _kova(w), _kova(h),              # genisligi, uzunlugu
        _kova(ob.size),                  # kapladigi alan
        1 if w == h else 0,              # kare mi
        0 if dolu > 0.95 else (1 if dolu > 0.6 else 2),   # sekli (dolu/yuvarlak/seyrek)
        str(P.is_symmetric(ob) or "-"),  # simetrisi
        il[0], il[1], il[2],             # ONERILEN: icinde / degiyor / esi_var
        yalniz,                          # ONERILEN: sahnede tek ornek mi
    )


def nesneler(grid, ust=400):
    return [o for o in P.find_objects(grid) if o.size <= ust]


def etki(onceki, sonraki):
    """Oyun-notr etki imzasi. 'seviye' kelimesi GECMIYOR."""
    deg = degisim(onceki, sonraki)
    if deg == 0:
        return ("yok",)
    return ("deg", _kova(deg))


def degisim(onceki, sonraki):
    """DEGISIM BUYUKLUGU. Adem'in tek amaci: bu sayiyi buyutmek."""
    return sum(1 for y in range(len(onceki)) for x in range(len(onceki[0]))
               if onceki[y][x] != sonraki[y][x])


# =====================================================================
class Ajan:
    """q = 'bu token'a su eylemi uygulamak YENI bir sey getiriyor mu'."""

    def __init__(self, Nmax=4.0, tau=4.0, alpha=0.30):
        self.Nmax, self.tau, self.alpha = Nmax, tau, alpha
        self.q = defaultdict(lambda: 0.6)      # (token, eylem) -> yenilik
        self.N = defaultdict(lambda: Nmax)
        self.gorulen = defaultdict(set)        # (token, eylem) -> etkiler
        self.tum_etkiler = set()
        self.recete = []                       # SEVIYE GECIREN (token, eylem)ler
        self.kullanim = defaultdict(int)
        self.birlesme = 0
        # ---- PLANNER durumu ----
        self.model = defaultdict(Counter)   # (token,eylem) -> etki sayaci
        self.zincirler = set()              # gorulen ETKI ZINCIRLERI
        self.son_etki = None
        self.plan = []                      # sirada bekleyen (token,eylem)ler
        self.makro = {}                     # etki_zinciri -> [(token,eylem)...]
        self.plan_sayisi = 0
        self.plan_tuttu = 0

    def qe(self, k):
        return self.q[k] * (self.N[k] / self.Nmax)

    def sec(self, adaylar):
        k = max(adaylar, key=self.qe)
        return k, random.choice(adaylar[k])

    # ================= PLANNER =================
    def etkiler(self):
        return sorted(self.tum_etkiler - {("yok",)}, key=str)

    def planla(self, adaylar, uzunluk=2):
        """
        ETKI UZAYINDA PLAN.  Eylem uzayi ~150, etki uzayi ~5.
        Hic uretilmemis bir ETKI ZINCIRI hedef secilir; her halkasi icin
        o etkiyi uretmeyi BILEN (token,eylem) modelden TERS CEVRILEREK
        bulunur. Arama yok. Odul yok. Sadece "bu kombinasyonu yapmadim".
        """
        es = self.etkiler()
        if len(es) < 2:
            return None
        # hedef: gorulmemis zincirler, once kisa olanlar
        hedefler = []
        for a in es:
            for b in es:
                z = (a, b)
                if z not in self.zincirler:
                    hedefler.append(z)
        if not hedefler:
            return None
        random.shuffle(hedefler)
        for z in hedefler[:12]:
            adim = []
            for hedef_etki in z:
                # modeli TERS CEVIR: bu etkiyi kim uretiyor?
                en, sk = None, 0.0
                for k in adaylar:
                    c = self.model.get(k)
                    if not c:
                        continue
                    p = c[hedef_etki] / sum(c.values())
                    if p > sk:
                        en, sk = k, p
                if en is None or sk < 0.25:
                    adim = None
                    break
                adim.append(en)
            if adim:
                self.plan_sayisi += 1
                return z, adim
        return None

    def ogren(self, k, e):
        yeni = 1.0 if e not in self.tum_etkiler else (
            0.5 if e not in self.gorulen[k] else 0.0)
        if e == ("yok",):
            yeni = 0.0
        # ---- ETKI ZINCIRI YENILIGI (planner'in yakiti) ----
        if self.son_etki is not None:
            z = (self.son_etki, e)
            if z not in self.zincirler and e != ("yok",) and self.son_etki != ("yok",):
                yeni = max(yeni, 0.8)        # yeni ZINCIR de yeniliktir
                self.zincirler.add(z)
        self.son_etki = e
        self.model[k][e] += 1
        self.tum_etkiler.add(e); self.gorulen[k].add(e)
        self.q[k] = min(1.0, max(0.0, self.q[k] + self.alpha*(yeni - self.q[k])))

    def harca(self, k):
        self.N[k] = max(0.0, self.N[k] - 1.0)
        self.kullanim[k] += 1

    def tik(self, ks):
        for k in ks:
            self.N[k] += (self.Nmax - self.N[k]) / self.tau

    # ---------- EYLEM UZAYINDA BISIMULATION ----------
    def eylem_birlestir(self, min_kullanim=8, min_etki=2):
        """
        Iki (token, eylem) cifti AYNI etki kumesini uretiyorsa ayirt
        edilemez -> ayni sey. q ve N'i paylassinlar.
        OLCULMUS HATA: gevsek esikle (2 gozlem) cd82'de 441 birlesme oldu ve
        SEVIYE KAYBEDILDI (5 -> 4). Iki cift, tesaduefen ayni 2 etkiyi
        gormus diye ayni degildir. Bisimulation KANIT ister:
          - her cift en az min_kullanim kez denenmis olmali
          - etki kumesi ayirt edici olmali (>= min_etki farkli etki)
        """
        grup = defaultdict(list)
        for k, es in self.gorulen.items():
            if len(es) >= min_etki and self.kullanim[k] >= min_kullanim:
                grup[frozenset(es)].append(k)
        for _, ks in grup.items():
            if len(ks) < 2:
                continue
            q = max(self.q[k] for k in ks)
            N = min(self.N[k] for k in ks)
            for k in ks:
                self.q[k], self.N[k] = q, N
            self.birlesme += len(ks) - 1

    # ---------- HAFIZA: seviye recetesi ----------
    def recete_kaydet(self, k):
        """Seviye gecirdi -> RECETE. Ozel bir odul degil; sadece
        'bu isi goren hamle' notu. Bir sonraki seviyede once bu denenir."""
        if k is not None and k not in self.recete:
            self.recete.append(k)
        if k is not None:
            self.q[k] = 1.0

    def yeni_seviye(self):
        """
        Adem: "her seviye gectiginde hafiza olusmali; ikinci seviyede bos
        seylerle ilgilenmeyip once birinci seviyede ise yarayani denemeli,
        yolda baska sey cikinca ogrenmeli."

        Receteler taze butce + yuksek oncelikle geri gelir. N hala calisiyor:
        recete tutmazsa tukenir ve sira kesfe gecer -> "yolda ogrenme".
        """
        for k in self.recete:
            self.q[k] = max(self.q[k], 0.95)
            self.N[k] = self.Nmax


ILISKI = True          # onerilen iliski atomlari acik mi
PLANNER = True         # etki-uzayinda planlama acik mi


def kosu_buyume(oyun, butce=800, tohum=0, kesif_adim=3):
    """
    ADEM'IN TASARIMI — tek amac DEGISIM.

    "Bir degisim varsa bu hedef iyidir, bunu SAKLA ve bu hedefin uzerine
     tahminler yap. Seviye gecmeden daha buyuk hedef olmadigi icin hep
     seviye gecmeye oynayacak -- en buyuk degisim o. Eylem dizisinin
     sonunda degisim yoksa YON DEGISTIRMELI."

    Odul yok, "dogru" yok, "seviye" yok. Tek sayi: kac hucre degisti.
    Seviye atlamak en buyuk degisimi urettigi icin KENDILIGINDEN hedef olur.

    Dongu:
      1. sifirla, EN IYI PLANI tekrar oyna   (bilinen zemin)
      2. ustune kesif_adim kadar YENI adim ekle
      3. toplam degisim arttiysa -> yeni EN IYI PLAN
         artmadiysa            -> yon degistir (baska kesif)
    """
    from env import Env
    rnd = random.Random(tohum); random.seed(tohum)
    e = Env(oyun)
    en_iyi, en_deger = [], -1.0
    en_sv, ilk, harcanan, tur = 0, None, 0, 0
    aj = Ajan()
    kuru = 0

    while harcanan < butce:
        tur += 1
        o = e.reset(); toplam = 0.0; plan = []
        for k in en_iyi:                       # 1) bilinen zemini tekrar oyna
            if harcanan >= butce: break
            o, d, k2 = _oyna(e, o, aj, k)
            harcanan += 1; toplam += d; plan.append(k2 or k)
            if o["level"] > en_sv:
                en_sv = o["level"]; ilk = ilk if ilk is not None else harcanan
        son_dilim = 0.0
        for _ in range(kesif_adim):            # 2) ustune yeni adim
            if harcanan >= butce: break
            o, d, k2 = _oyna(e, o, aj, None)
            harcanan += 1; toplam += d; son_dilim += d
            if k2: plan.append(k2)
            if o["level"] > en_sv:
                en_sv = o["level"]; ilk = ilk if ilk is not None else harcanan
        if toplam > en_deger:                  # 3) daha buyuk degisim -> sakla
            en_deger, en_iyi, kuru = toplam, plan[:], 0
        elif son_dilim == 0:                   # sonunda degisim yok -> YON DEGISTIR
            kuru += 1
            for k in list(aj.q):               # denenmisleri sustur, sira baskasina
                aj.N[k] = max(0.0, aj.N[k] - 0.5)
            if kuru >= 6 and en_iyi:           # cok kurudu -> zemini kisalt
                en_iyi = en_iyi[:max(0, len(en_iyi)-2)]; en_deger *= 0.7; kuru = 0
    return dict(sv=en_sv, ilk=ilk, token=len(aj.q), cift=len(aj.q),
                etki=len(aj.tum_etkiler), birlesme=aj.birlesme,
                recete=len(en_iyi), zincir=int(en_deger), plan=tur)


def _oyna(e, o, aj, k_zorla):
    """Tek adim. k_zorla verilirse o (token,eylem), yoksa kesif secimi."""
    grid = o["grid"]
    eylemler = o["avail"] or [6]
    obs = nesneler(grid)
    if ILISKI and obs:
        ic, dg, es = iliskiler(obs); kaba = Counter(token(x, 0, 0) for x in obs)
    else:
        ic = dg = es = [0]*len(obs); kaba = None
    adaylar = defaultdict(list)
    for i, ob in enumerate(obs):
        yal = 1 if (kaba is not None and kaba[token(ob, 0, 0)] == 1) else 0
        tk = token(ob, 0, 0, (ic[i], dg[i], es[i]), yal)
        h = random.choice(sorted(ob.cells))
        for a2 in eylemler:
            adaylar[(tk, a2)].append((int(h[1]), int(h[0]), a2))
    if not adaylar:
        return o, 0.0, None
    k = k_zorla if (k_zorla in adaylar) else aj.sec(adaylar)[0]
    cx, cy, a = random.choice(adaylar[k])
    aj.harca(k); aj.tik(list(adaylar.keys()))
    o2 = e.step("click", a, cx, cy) if a == 6 else e.step("act", a)
    d = degisim(grid, o2["grid"])
    aj.ogren(k, etki(grid, o2["grid"]))
    if o2["state"] not in ("NOT_FINISHED", "NOT_STARTED"):
        o2 = e.reset()
    return o2, float(d), k


def kosu(oyun, butce=800, mod="nesne", tohum=0):
    if mod == "buyume":
        return kosu_buyume(oyun, butce, tohum)
    from env import Env
    rnd = random.Random(tohum)
    e = Env(oyun); o = e.reset()
    H, W = len(o["grid"]), len(o["grid"][0])
    aj = Ajan()
    en_sv = o["level"]; ilk = None; tokenlar = set()

    for t in range(butce):
        grid = o["grid"]
        eylemler = [a for a in o["avail"]]
        if not eylemler:
            eylemler = [6]
        if mod == "rastgele":
            a = rnd.choice(eylemler)
            hedef = (rnd.randrange(W), rnd.randrange(H)) if a == 6 else None
            k = None
        else:
            obs = nesneler(grid)
            if ILISKI:
                ic, dg, es = iliskiler(obs)
                kaba = Counter(token(o2b, H, W) for o2b in obs)
            else:
                ic = dg = es = [0]*len(obs); kaba = None
            adaylar = defaultdict(list)
            for i, ob in enumerate(obs):
                yal = 0
                if kaba is not None:
                    yal = 1 if kaba[token(ob, H, W)] == 1 else 0
                tk = token(ob, H, W, (ic[i], dg[i], es[i]), yal)
                tokenlar.add(tk)
                hucre = random.choice(sorted(ob.cells))   # (r, c)
                for a2 in eylemler:
                    adaylar[(tk, a2)].append((int(hucre[1]), int(hucre[0]), a2))
            if not adaylar:
                a = rnd.choice(eylemler); hedef = (rnd.randrange(W), rnd.randrange(H)); k = None
            else:
                if PLANNER and not aj.plan and t % 3 == 0:
                    pr = aj.planla(adaylar)
                    if pr:
                        aj.plan = [kk for kk in pr[1] if kk in adaylar]
                if aj.plan:
                    k = aj.plan.pop(0)
                    if k not in adaylar:
                        aj.plan = []; k, _ = aj.sec(adaylar)
                else:
                    k, _ = aj.sec(adaylar)
                cx, cy, a = random.choice(adaylar[k])
                aj.harca(k); aj.tik(list(adaylar.keys()))
                hedef = (cx, cy)

        # env.step 'kind'e gore dallaniyor: eylem 6 degilse TIKLAMA DEGIL.
        if a == 6 and hedef:
            o2 = e.step("click", a, hedef[0], hedef[1])
        else:
            o2 = e.step("act", a)
        if k is not None:
            aj.ogren(k, etki(grid, o2["grid"]))
        if o2["level"] > en_sv:
            en_sv = o2["level"]
            if ilk is None:
                ilk = t
            if mod != "rastgele":
                aj.recete_kaydet(k)      # HAFIZA
                aj.yeni_seviye()         # recete-once
        if mod != "rastgele" and t % 100 == 99:
            aj.eylem_birlestir()         # eylem uzayinda bisimulation
        o = o2
        if o["state"] not in ("NOT_FINISHED", "NOT_STARTED"):
            o = e.reset()
    return dict(sv=en_sv, ilk=ilk, token=len(tokenlar),
                cift=len(aj.q), etki=len(aj.tum_etkiler),
                birlesme=aj.birlesme, recete=len(aj.recete),
                zincir=len(aj.zincirler), plan=aj.plan_sayisi)


if __name__ == "__main__":
    oyunlar = sys.argv[1:] or sorted(os.listdir(os.environ["ENVIRONMENTS_DIR"]))
    print("=" * 78)
    print("TEK AMAC: DEGISIM.  En iyi planin uzerine insa et.  (Adem'in tasarimi)")
    print("ALFABE = NESNELER.  Eylem uzayi: 4096 hucre -> N nesne-token")
    print("Butce 800 eylem/oyun, 2 tohum. Kiyas: rastgele.")
    print("=" * 78)
    print(f"  {'oyun':<7}{'RND':>5}{'NESNE':>7}{'token':>7}{'(tok,eyl)':>11}"
          f"{'etki':>6}{'en_deg':>8}{'tur':>6}{'plan_uz':>9}{'ilk sv @':>10}")
    ozet = {}
    kazanc = 0
    for g in oyunlar:
        try:
            r = max(kosu(g, mod="rastgele", tohum=s)["sv"] for s in (0, 1))
            ns = [kosu(g, mod="buyume", tohum=s) for s in (0, 1)]
        except Exception as ex:
            print(f"  {g:<7}  HATA {type(ex).__name__}: {str(ex)[:35]}")
            continue
        n = max(ns, key=lambda d: d["sv"])
        ilkler = [d["ilk"] for d in ns if d["ilk"] is not None]
        im = f"  <-- +{n['sv']-r}" if n["sv"] > r else ""
        if n["sv"] > r:
            kazanc += 1
        ozet[g] = dict(rnd=r, nesne=n["sv"], token=n["token"], etki=n["etki"])
        print(f"  {g:<7}{r:>5}{n['sv']:>7}{n['token']:>7}{n['cift']:>11}"
              f"{n['etki']:>6}{n['zincir']:>8}{n['plan']:>6}{n['recete']:>9}"
              f"{(str(min(ilkler)) if ilkler else '-'):>10}{im}")
    tr = sum(v["rnd"] for v in ozet.values()); tn = sum(v["nesne"] for v in ozet.values())
    print(f"\n  TOPLAM seviye: rastgele {tr}  ->  nesne-alfabe {tn}"
          f"   ({kazanc}/{len(ozet)} oyunda ustun)")
    json.dump(ozet, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "nesne_ozet.json"), "w"), indent=1)
